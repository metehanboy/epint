# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any, List, Optional
from .swagger import SwaggerModel
from .request_model import RequestModel


class Endpoint:
    """Endpoint model'ini wrap eden callable sınıf"""
    
    def __init__(self, category: str, name: str, data: Dict[str, Any]):
        self._category = category
        self._name = name
        self._data = data
    
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        """Endpoint çağrıldığında çalışır"""

        import epint

        print(f"username: {epint._username}")
        print(f"password: {epint._password}")
        print(f"mode: {epint._mode}")

        

        print(f"'{self._category}.{self._name}' methodu çalıştırıldı")
        

        
        # RequestModel oluştur
        request_model = RequestModel(self._data, kwargs)
        
        # Request bilgilerini göster
        print(f"Request Model: {request_model}")
        print(f"Params: {request_model.params}")
        print(f"Headers: {request_model.headers}")
        if request_model.json:
            print(f"JSON Body: {json.dumps(request_model.json, indent=2, ensure_ascii=False)}")
        if request_model.data:
            print(f"Form Data: {request_model.data}")
        
        return request_model.to_dict()
        # return self._data
    
    def __getitem__(self, key: str) -> Any:
        """Endpoint data'sına erişim için"""
        return self._data.get(key)
    
    def __repr__(self) -> str:
        """Endpoint bilgisini göster"""
        return f"<Endpoint: {self._data.get('operation_id', 'unknown')}>"


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
