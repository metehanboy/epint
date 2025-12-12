# -*- coding: utf-8 -*-
from typing import Dict, Any
import epint
from ...models.endpoint import EndpointModel, Endpoint
from ..search.method_name_decorator import to_python_method_name
from ..search.find_closest import find_closest_match


class CategoryProxy:
    """Kategori proxy objesi - epint.category.method_name şeklinde erişim sağlar"""
    
    def __init__(self, category: str):
        self._category = category
    
    def __getattr__(self, name):
        """Method ismine erişim - epint.category.method_name"""

        epint._check_auth()

        normalized_name = to_python_method_name(name)
        
        endpoints = EndpointModel.get_category_endpoints(self._category)
        endpoint_data = None
        endpoint_name = None
        
        # 1. Önce normalize edilmiş isimle tam eşleşme kontrolü
        if normalized_name in endpoints:
            endpoint_data = endpoints[normalized_name]
            endpoint_name = normalized_name
        # 2. Orijinal isimle tam eşleşme kontrolü
        elif name in endpoints:
            endpoint_data = endpoints[name]
            endpoint_name = name
        else:
            # 3. Normalize edilmiş isimlerle fuzzy matching
            normalized_endpoints = {to_python_method_name(ep_name): ep_name for ep_name in endpoints.keys()}
            closest_normalized = find_closest_match(normalized_name, list(normalized_endpoints.keys()), threshold=0.7)
            if closest_normalized:
                endpoint_name = normalized_endpoints[closest_normalized]
                endpoint_data = endpoints[endpoint_name]
            else:
                # 4. Orijinal endpoint isimleriyle fuzzy matching (düşük threshold)
                closest = find_closest_match(name, list(endpoints.keys()), threshold=0.6)
                if closest:
                    endpoint_name = closest
                    endpoint_data = endpoints[closest]
        
        if not endpoint_data:
            available = list(endpoints.keys())[:10]
            raise AttributeError(
                f"'{self._category}' category has no endpoint '{name}'. "
                f"Available endpoints: {available}"
            )
        
        # EndpointModel.Endpoint objesi döndür
        return Endpoint(self._category, endpoint_name or name, endpoint_data)

