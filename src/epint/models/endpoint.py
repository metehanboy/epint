# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any, List, Optional
from .swagger import SwaggerModel



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
    def get_endpoint(cls, category: str, name: str) -> Optional[Dict[str, Any]]:
        """Endpoint al"""
        return cls._categories.get(category, {}).get(name)
    
    @classmethod
    def get_category_endpoints(cls, category: str) -> Dict[str, Any]:
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
