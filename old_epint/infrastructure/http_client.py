# -*- coding: utf-8 -*-

import socket
import urllib3
import time
from typing import Dict, Any
from requests import Session
from .logger import get_logger
from .json_encoder import JSONUtils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPClient:

    def __init__(self, use_cert: bool = False, timeout: int = 10):
        self.use_cert = use_cert
        self.timeout = timeout
        self.session = Session()
        self.logger = get_logger()
        self._configure_session()

    def _configure_session(self):
        if not self.use_cert:
            self.session.verify = False
            self.session.trust_env = False

        # Headers'ı clear etme, sadece gerekli olanları ekle
        host_name = socket.gethostname()
        self.session.headers.update(
            {"authority": host_name, "X-Forwarded-Host": host_name}
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def _request(self, method: str, endpoint: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        start_time = time.time()

        try:
            self.logger.log_operation(
                "http_request_start",
                method=method.upper(),
                url=endpoint,
                timeout=self.timeout,
            )

            response = getattr(self.session, method.lower())(endpoint, **kwargs)

            duration = time.time() - start_time
            self.logger.log_performance(
                "http_request",
                duration,
                method=method.upper(),
                url=endpoint,
                status_code=response.status_code,
                success=response.ok,
            )

            if not response.ok:
                # DateRangeError durumunda log yazma (decorator progress bar gösterecek)
                response_text_lower = response.text[:500].lower()
                is_date_range_error = (
                    response.status_code == 400 and
                    "tarih" in response_text_lower and
                    "aralık" in response_text_lower and
                    ("month" in response_text_lower or "year" in response_text_lower or 
                     "week" in response_text_lower or "day" in response_text_lower)
                )
                
                if not is_date_range_error:
                    self.logger.log_error(
                        "http_request_error",
                        method=method.upper(),
                        url=endpoint,
                        status_code=response.status_code,
                        response_text=response.text[:500],  # İlk 500 karakter
                    )

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.logger.log_error(
                "http_request_exception",
                method=method.upper(),
                url=endpoint,
                error_msg=str(e),
                duration=duration,
            )
            raise

    def get(self, endpoint: str, **kwargs):
        return self._request("get", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self._request("post", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self._request("put", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self._request("delete", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs):
        return self._request("patch", endpoint, **kwargs)

    def execute_request(
        self,
        method: str,
        url: str,
        header: Dict[str, str],
        serialized_params: Dict[str, Any],
    ):
        method = method.upper()
        
        # JSON serialization için custom encoder kullan
        # datetime objeleri JSON serializable hale getir
        serialized_params = JSONUtils.make_serializable(serialized_params)
        
        if method == "GET":
            return self.get(url, headers=header, params=serialized_params)
        elif method == "POST":
            # Custom encoder ile serialize et ve data olarak gönder
            json_data = JSONUtils.dumps(serialized_params)
            header_with_content_type = header.copy()
            header_with_content_type.setdefault("Content-Type", "application/json")
            return self.post(url, headers=header_with_content_type, data=json_data)
        elif method == "PUT":
            json_data = JSONUtils.dumps(serialized_params)
            header_with_content_type = header.copy()
            header_with_content_type.setdefault("Content-Type", "application/json")
            return self.put(url, headers=header_with_content_type, data=json_data)
        elif method == "DELETE":
            json_data = JSONUtils.dumps(serialized_params)
            header_with_content_type = header.copy()
            header_with_content_type.setdefault("Content-Type", "application/json")
            return self.delete(url, headers=header_with_content_type, data=json_data)
        elif method == "PATCH":
            json_data = JSONUtils.dumps(serialized_params)
            header_with_content_type = header.copy()
            header_with_content_type.setdefault("Content-Type", "application/json")
            return self.patch(url, headers=header_with_content_type, data=json_data)
        else:
            # Varsayılan olarak POST kullan
            json_data = JSONUtils.dumps(serialized_params)
            header_with_content_type = header.copy()
            header_with_content_type.setdefault("Content-Type", "application/json")
            return self.post(url, headers=header_with_content_type, data=json_data)
