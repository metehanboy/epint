# -*- coding: utf-8 -*-
from typing import Dict, Any
from ...models.endpoint import EndpointModel, Endpoint
from ..search.method_name_decorator import to_python_method_name


class CategoryProxy:
    """Kategori proxy objesi - epint.category.method_name şeklinde erişim sağlar"""
    
    def __init__(self, category: str):
        self._category = category
    
    def __getattr__(self, name):
        """Method ismine erişim - epint.category.method_name"""
        normalized_name = to_python_method_name(name)
        
        endpoints = EndpointModel.get_category_endpoints(self._category)
        endpoint_data = None
        endpoint_name = None
        
        # Önce normalize edilmiş isimle ara
        if normalized_name in endpoints:
            endpoint_data = endpoints[normalized_name]
            endpoint_name = normalized_name
        # Orijinal isimle ara
        elif name in endpoints:
            endpoint_data = endpoints[name]
            endpoint_name = name
        else:
            # Tüm endpoint isimlerinde ara (case-insensitive, normalize edilmiş)
            for ep_name, ep_data in endpoints.items():
                normalized_endpoint = to_python_method_name(ep_name)
                if normalized_endpoint == normalized_name or ep_name.lower() == name.lower():
                    endpoint_data = ep_data
                    endpoint_name = ep_name
                    break
        
        if not endpoint_data:
            available = list(endpoints.keys())[:10]
            raise AttributeError(
                f"'{self._category}' category has no endpoint '{name}'. "
                f"Available endpoints: {available}"
            )
        
        # EndpointModel.Endpoint objesi döndür
        return Endpoint(self._category, endpoint_name or name, endpoint_data)

