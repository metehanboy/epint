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
        self, auth_mode: str, service_ticket_url: Optional[str] = None
    ) -> Dict[str, str]:
        tgt = self.auth_manager.get_tgt()
        header = {
            "TGT": tgt[0],
            "Accept": "application/json",
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
            return self.prepare_gop_message(matched_params)

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
        
        # Eğer sadece 'body' parametresi varsa ve başka parametre yoksa, body içeriğini unwrap et
        # Bu, seffaflik-electricity gibi servislerde body wrapper'ını kaldırmak için
        if len(serialized) == 1 and "body" in serialized and isinstance(serialized["body"], dict):
            # Body içeriğini direkt gönder (unwrap)
            return serialized["body"]
        
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
