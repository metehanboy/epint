# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

import epint
from ..modules.authentication.auth_manager import Authentication
from ..modules.http_client import HTTPClient
from ..modules.error_handler import ErrorHandler
from .swagger import SwaggerModel
from .request_model import RequestModel


class Endpoint:
    """Endpoint model'ini wrap eden callable sınıf"""
    
    def __init__(self, category: str, name: str, data: Dict[str, Any]):
        self._category = category
        self._name = name
        self._data = data
        self.client = HTTPClient()

    
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        """Endpoint çağrıldığında çalışır"""

        target_service = "transparency" if "seffaflik" in self._category else "epys"
        runtime_mode = epint._mode
        auth = Authentication(epint._username, epint._password, target_service, runtime_mode)
        
        # RequestModel oluştur
        request_model = RequestModel(self._data, kwargs)
        

        if "gop" != self._category:
            request_model.headers["TGT"] = auth.get_tgt()[0]
        if not ("gop" in self._category or "seffaflik" in self._category):
            request_model.headers["ST"] = auth.get_st(request_model.st_service_url)[0]
        if "gop" in self._category:
            request_model.headers["gop-service-ticket"] = auth.get_st(request_model.st_service_url)[0]

        
        url = self.client.buildurl(self._data.get("host"), self._data.get("basePath"), self._data.get("path"))
        method = self._data.get("method")

        # Prepare parameters for the HTTP request, including body if exists
        request_args = {
            "headers": request_model.headers
        }
        if request_model.params:
            request_args["params"] = request_model.params
        if request_model.json is not None:
            request_args["json"] = request_model.json
        if request_model.data is not None:
            request_args["data"] = request_model.data
        
        # return request_args
        # ErrorHandler oluştur
        error_handler = ErrorHandler(auth)
        try:
            response = self.client.__getattribute__(method.lower())(
                url,
                **request_args
            )
            return response
        except Exception as e:
            # Hataları ErrorHandler ile yönet
            error_handler.handle_exception(e)
            raise


class EndpointModel:
    
    _endpoints: Dict[str, Dict[str, Any]] = {}
    _categories: Dict[str, Dict[str, Any]] = {}
    _swagger_models: Dict[str, SwaggerModel] = {}
    
    @classmethod
    def load_swagger(cls, category: str, swagger_path: str):
        if category in cls._swagger_models:
            return  # Zaten yüklü
        
        if not os.path.exists(swagger_path):
            return
        
        swagger_model = SwaggerModel(swagger_path)
        cls._swagger_models[category] = swagger_model
        
        # Endpoint'leri kaydet
        for name, endpoint_data in swagger_model.get_all_endpoints().items():
            endpoint_data['category'] = category
            cls.register_endpoint(category, name, endpoint_data)
    
    @classmethod
    def register_endpoint(cls, category: str, name: str, data: Dict[str, Any]):
        """Endpoint kaydet"""
        if category not in cls._categories:
            cls._categories[category] = {}
        cls._categories[category][name] = data
        cls._endpoints[f"{category}.{name}"] = data
    
    @classmethod
    def get_endpoint(cls, category: str, name: str) -> Optional[Endpoint]:
        """Endpoint al - Endpoint objesi döndürür"""
        data = cls._categories.get(category, {}).get(name)
        if data:
            return Endpoint(category, name, data)
        return None
    
    @classmethod
    def get_category_endpoints(cls, category: str) -> Dict[str, Dict[str, Any]]:
        """Kategori endpoint'lerini al"""
        return cls._categories.get(category, {})
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, Dict[str, Any]]:
        """Tüm kategorileri al"""
        return cls._categories
    
    @classmethod
    def get_swagger_model(cls, category: str) -> Optional[SwaggerModel]:
        """Swagger modeli al"""
        return cls._swagger_models.get(category)
