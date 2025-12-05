# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Dict, Any, Optional
import uuid
from .auth_manager import Authentication
from .type_converter import TypeConverter


class RequestBuilder:

    def __init__(
        self,
        auth_manager: Authentication,
        method: str,
        application_name: str = "epint-client",
    ):
        self.auth_manager = auth_manager
        self.method = method.upper()
        self.application_name = application_name

    def prepare_headers(
        self, auth_mode: str, service_ticket_url: Optional[str] = None, 
        accept_format: Optional[str] = None
    ) -> Dict[str, str]:
        tgt = self.auth_manager.get_tgt()
        
        # Accept header'ını format'a göre ayarla
        # Export servisleri için Accept header'ı "application/json" olarak gönder
        # API exportType parametresine göre response formatını belirliyor
        # Accept header'ı sadece hint olarak kullanılıyor, asıl belirleyici exportType
        if accept_format:
            # Export servisleri için Accept header'ı "application/json" olarak gönder
            # Çünkü API exportType'a göre response formatını belirliyor
            accept = "application/json, text/plain, */*"
        else:
            accept = "application/json"
        
        header = {
            "TGT": tgt[0],
            "Accept": accept,
            "Content-Type": "application/json",
        }

        if auth_mode != "transparency" and service_ticket_url:
            st = self.auth_manager.get_st(service_ticket_url)
            header["ST"] = st[0]

            if auth_mode == "gop":
                header["gop-service-ticket"] = st[0]

        return header

    def prepare_gop_message(
        self, body_data: Dict[str, Any], language: str = "TR"
    ) -> Dict[str, Any]:
        transaction_id = str(uuid.uuid4())

        serialized_body = {}
        for key, value in body_data.items():
            serialized_body[key] = TypeConverter.serialize_for_gop(value)

        gop_message = {
            "header": [
                {"key": "transactionId", "value": transaction_id},
                {"key": "application", "value": self.application_name},
                {"key": "language", "value": language},
            ],
            "body": serialized_body,
        }

        return gop_message

    def serialize_parameters(
        self,
        matched_params: Dict[str, Any],
        auth_mode: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        if auth_mode == "gop":
            # gop-service-ticket parametresini çıkar (zaten header'a ekleniyor)
            gop_params = {k: v for k, v in matched_params.items() if k != "gop-service-ticket"}
            
            # Body içinde body varsa, içteki body'yi al
            if "body" in gop_params and isinstance(gop_params["body"], dict):
                body_data = gop_params["body"]
                # Eğer body içinde body varsa (parameter_matcher'dan gelen yapı), içteki body'yi al
                if "body" in body_data and isinstance(body_data["body"], dict):
                    return self.prepare_gop_message(body_data["body"])
                else:
                    # Body içinde body yoksa, tüm body'yi al
                    return self.prepare_gop_message(body_data)
            else:
                # Body parametresi yoksa, tüm parametreleri al
                return self.prepare_gop_message(gop_params)

        # Serialize et
        if category in ["gunici", "gunici-trading"]:
            serialized = self._serialize_recursive(
                matched_params, TypeConverter.serialize_for_gunici
            )
        elif self.method == "GET":
            serialized = self._serialize_recursive(
                matched_params, TypeConverter.serialize_for_get
            )
        else:
            serialized = self._serialize_recursive(
                matched_params, TypeConverter.serialize_for_post
            )
        
        # Body parametresi unwrap işlemi
        # Eğer 'body' parametresi varsa ve içinde dict varsa, body içeriğini unwrap et
        # Header parametreleri (TGT, ST gibi) body'den ayrı tutulmalı
        if "body" in serialized and isinstance(serialized["body"], dict):
            # Body içeriğini direkt gönder (unwrap)
            # Header parametreleri zaten header'a ekleniyor, body'den çıkar
            body_content = serialized.pop("body")
            
            # Optional parametreler için null değerleri ekle (export servisleri için)
            # Eğer body içinde exportType varsa, optional parametreleri null olarak ekle
            if "exportType" in body_content or "export_type" in body_content:
                # Swagger'dan gelen endpoint info'yu kullanarak optional parametreleri null olarak ekle
                # Bu sadece export servisleri için gerekli olabilir
                pass  # Şimdilik pas geç, API'nin davranışını gözlemle
            
            # Eğer başka parametre yoksa sadece body içeriğini döndür
            if not serialized:
                return body_content
            
            # Eğer başka parametreler varsa (header parametreleri gibi), 
            # bunları body içine ekleme, sadece body içeriğini döndür
            # Header parametreleri zaten header'a ekleniyor
            return body_content
        
        return serialized
    
    def _serialize_recursive(
        self, params: Dict[str, Any], serialize_func
    ) -> Dict[str, Any]:
        """Recursive olarak nested dict'leri serialize et"""
        serialized = {}
        for key, value in params.items():
            if isinstance(value, dict):
                # Nested dict ise recursive serialize et
                serialized[key] = self._serialize_recursive(value, serialize_func)
            elif isinstance(value, list):
                # List ise içindeki her elemanı serialize et
                serialized[key] = [
                    self._serialize_recursive(item, serialize_func) if isinstance(item, dict)
                    else serialize_func(item)
                    for item in value
                ]
            else:
                # Normal değer ise serialize et
                serialized[key] = serialize_func(value)
        return serialized
