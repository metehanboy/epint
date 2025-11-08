# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, Any, Optional
from .auth_manager import Authentication
from .http_client import HTTPClient
from .service_config import (
    get_service_config,
    get_auth_mode,
    get_service_ticket_url,
    get_full_url,
)
from .endpoint_models import EndpointInfo, ValidationResult
from .endpoint_parser import EndpointParser
from .validation_service import ValidationService
from .request_builder import RequestBuilder
from .logger import get_logger
from .type_converter import TypeConverter
import json
import time


class EndpointManager:

    def __init__(
        self,
        endpoint_name: str,
        endpoint_data: Dict[str, Any],
        username: str,
        password: str,
        category: str = "",
        mode: str = "prod",
    ):
        self.logger = get_logger()
        self.endpoint_name = endpoint_name
        self.endpoint_info: EndpointInfo = EndpointParser.parse_endpoint_info(
            endpoint_name, endpoint_data, category
        )
        self.username = username
        self.password = password
        self.category = category
        self.mode = mode

        self.validation_service = ValidationService(self.endpoint_info)
        self._auth_manager: Optional[Authentication] = None
        self._request_builder: Optional[RequestBuilder] = None
        self._http_client: Optional[HTTPClient] = None
        self._http_client_timeout: Optional[int] = None

    def validate_endpoint_call(self, **kwargs) -> ValidationResult:
        return self.validation_service.validate_endpoint_call(**kwargs)

    def get_endpoint_info(self) -> EndpointInfo:
        return self.endpoint_info

    def get_endpoint_name(self) -> str:
        return self.endpoint_name

    def get_service_config(self):
        return get_service_config(self.endpoint_info.category, self.mode)

    def get_full_url(self) -> str:
        return get_full_url(
            self.endpoint_info.category, self.endpoint_info.endpoint, self.mode
        )

    def get_service_ticket_url(self) -> str:
        return get_service_ticket_url(self.endpoint_info.category, self.mode)

    @property
    def auth_manager(self) -> Authentication:
        import epint

        global_username = epint._username
        global_password = epint._password

        if (
            self._auth_manager is None
            or self._auth_manager.username != global_username
            or self._auth_manager.password != global_password
        ):

            auth_mode = get_auth_mode(self.endpoint_info.category, self.mode)
            self._auth_manager = Authentication(
                username=global_username,
                password=global_password,
                auth_mode=auth_mode,
                environment_mode=self.mode,
            )

        return self._auth_manager

    @property
    def request_builder(self) -> RequestBuilder:
        if self._request_builder is None:
            self._request_builder = RequestBuilder(
                self.auth_manager,
                self.endpoint_info.method,
                application_name="epint-client",
            )
        return self._request_builder
    
    def get_http_client(self, timeout: Optional[int] = None) -> HTTPClient:
        """HTTP Client'ı cache'leyerek döndür
        
        Args:
            timeout: İsteğe bağlı timeout değeri (saniye). None ise default kullanılır.
        
        Returns:
            HTTPClient: Cache'lenmiş veya yeni oluşturulmuş HTTPClient instance
        
        Note:
            - Default timeout (None) için client cache'lenir ve session reuse edilir
            - Custom timeout belirtilirse ve cache'deki timeout ile eşleşirse cache kullanılır
            - Farklı custom timeout için geçici client oluşturulur (nadiren kullanılır)
        """
        # Default timeout için cache kullan
        if timeout is None:
            if self._http_client is None:
                self._http_client = HTTPClient()
            return self._http_client
        
        # Custom timeout - cache'deki ile aynıysa reuse et
        if timeout == self._http_client_timeout and self._http_client is not None:
            return self._http_client
        
        # Yeni custom timeout - cache'le
        if self._http_client is not None and self._http_client.session:
            # Eski session'ı kapat
            self._http_client.session.close()
        
        self._http_client = HTTPClient(timeout=timeout)
        self._http_client_timeout = timeout
        return self._http_client
    
    def close(self):
        """HTTP client session'ını kapat"""
        if self._http_client is not None and self._http_client.session:
            self._http_client.session.close()
            self._http_client = None
            self._http_client_timeout = None
    
    def __del__(self):
        """Destructor - session'ı temizle"""
        self.close()

    def __repr__(self):
        return str(self.endpoint_info)

    def _process_error_response(self, response) -> None:
        try:
            error_data = response.json()
        except json.JSONDecodeError:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        if self._is_gop_error_format(error_data):
            if error_data.get("resultCode") == "0":
                return

            error_text = self._build_gop_error_message(error_data)
        else:
            error_text = self._build_error_message(error_data)

        self._raise_appropriate_exception(response.status_code, error_text)

    def _is_gop_error_format(self, error_data: dict) -> bool:
        return (
            "resultCode" in error_data
            and "resultDescription" in error_data
            and "resultType" in error_data
        )

    def _build_gop_error_message(self, error_data: dict) -> str:
        result_code = error_data.get("resultCode", "UNKNOWN")
        result_description = error_data.get("resultDescription", "Bilinmeyen hata")
        result_type = error_data.get("resultType", "UNKNOWN")

        if result_code == "0":
            return f"[GOP SUCCESS] {result_description}"

        if result_type == "BUSINESSERROR":
            return f"[GOP İş Kuralı Hatası] {result_code}: {result_description}"
        elif result_type == "SYSTEMERROR":
            return f"[GOP Sistem Hatası] {result_code}: {result_description}"
        else:
            return f"[GOP {result_type}] {result_code}: {result_description}"

    def _build_error_message(self, error_data: dict) -> str:
        status = error_data.get("status", "Unknown")
        correlation_id = error_data.get("correlationId", "N/A")
        errors = error_data.get("errors", [])

        error_messages = []
        for error in errors:
            if isinstance(error, dict):
                error_code = error.get("errorCode", "Unknown")
                error_message = error.get("errorMessage", "Unknown error")
                error_messages.append(f"[{error_code}] {error_message}")
            else:
                error_messages.append(str(error))

        if error_messages:
            main_error = error_messages[0]
            additional_errors = error_messages[1:] if len(error_messages) > 1 else []

            error_text = f"API Hatası: {main_error}"
            if additional_errors:
                error_text += f"\nEk Hatalar: {'; '.join(additional_errors)}"
        else:
            error_text = f"API Hatası: {status}"

        error_text += f"\nCorrelation ID: {correlation_id}"
        return error_text

    def _raise_appropriate_exception(self, status_code: int, error_text: str) -> None:
        if status_code == 400:
            raise ValueError(error_text)
        elif status_code == 401:
            raise PermissionError(f"Kimlik doğrulama hatası: {error_text}")
        elif status_code == 403:
            raise PermissionError(f"Erişim reddedildi: {error_text}")
        elif status_code == 404:
            raise FileNotFoundError(f"Endpoint bulunamadı: {error_text}")
        elif status_code >= 500:
            raise ConnectionError(f"Sunucu hatası: {error_text}")
        else:
            raise Exception(error_text)

    def __call__(self, **kwargs):
        debug = kwargs.get("debug", False)
        start_time = time.time()

        try:
            # http_timeout parametresini validation'dan önce çıkar ve sakla
            http_timeout = kwargs.pop('http_timeout', None)
            
            self.logger.log_operation(
                "endpoint_call_start",
                endpoint=self.endpoint_name,
                category=self.endpoint_info.category,
                method=self.endpoint_info.method,
                params_count=len(kwargs),
            )

            result = self.validate_endpoint_call(**kwargs)
            
            # http_timeout'u validated_params'a ekle
            if http_timeout is not None:
                result.validated_params['http_timeout'] = http_timeout
            
            response = self._make_http_request(result.validated_params, debug)

            duration = time.time() - start_time
            self.logger.log_performance(
                "endpoint_call",
                duration,
                endpoint=self.endpoint_name,
                category=self.endpoint_info.category,
                method=self.endpoint_info.method,
                success=True,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.logger.log_error(
                "endpoint_call_error",
                endpoint=self.endpoint_name,
                category=self.endpoint_info.category,
                method=self.endpoint_info.method,
                error_msg=str(e),
                duration=duration,
            )
            raise

    def _make_http_request(self, matched_params: Dict[str, Any], debug: bool = False):
        auth_mode = get_auth_mode(self.endpoint_info.category)
        service_ticket_url = self.get_service_ticket_url()

        # http_timeout parametresini çıkar (eğer varsa)
        timeout = matched_params.pop('http_timeout', None)
        if timeout is not None:
            try:
                timeout = int(timeout)
            except (ValueError, TypeError):
                timeout = None

        header = self.request_builder.prepare_headers(auth_mode, service_ticket_url)
        serialized_params = self.request_builder.serialize_parameters(
            matched_params, auth_mode, self.endpoint_info.category
        )

        # Cache'lenmiş HTTP client'ı kullan (session reuse için)
        client = self.get_http_client(timeout)
        
        # Context manager KULLANMA - session'ı açık tut için connection reuse
        response = client.execute_request(
            self.endpoint_info.method,
            self.get_full_url(),
            header,
            serialized_params,
        )
        
        if debug:
            return response

        if not response.ok:
            self._process_error_response(response)

        response_data = response.json()
        
        # response_structure varsa parse et
        if self.endpoint_info.response_structure:
            response_data = TypeConverter.parse_response(
                response_data, 
                self.endpoint_info.response_structure
            )
        
        return response_data
