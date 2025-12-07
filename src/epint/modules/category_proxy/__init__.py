# -*- coding: utf-8 -*-
from typing import Dict, Any
from ...models.endpoint import EndpointModel
from ..search.method_name_decorator import to_python_method_name


class CategoryProxy:
    """Kategori proxy objesi - epint.category.method_name şeklinde erişim sağlar"""
    
    def __init__(self, category: str):
        self._category = category
    
    def __getattr__(self, name):
        """Method ismine erişim - epint.category.method_name"""
        normalized_name = to_python_method_name(name)
        
        endpoints = EndpointModel.get_category_endpoints(self._category)
        # Önce normalize edilmiş isimle ara
        if normalized_name in endpoints:
            endpoint = endpoints[normalized_name]
            return lambda **kwargs: endpoint
        
        # Orijinal isimle ara
        if name in endpoints:
            endpoint = endpoints[name]
            return lambda **kwargs: endpoint
        
        # Tüm endpoint isimlerinde ara (case-insensitive, normalize edilmiş)
        for endpoint_name, endpoint_data in endpoints.items():
            normalized_endpoint = to_python_method_name(endpoint_name)
            if normalized_endpoint == normalized_name or endpoint_name.lower() == name.lower():
                return lambda **kwargs: endpoint_data
        
        available = list(endpoints.keys())[:10]
        raise AttributeError(
            f"'{self._category}' category has no endpoint '{name}'. "
            f"Available endpoints: {available}"
        )

