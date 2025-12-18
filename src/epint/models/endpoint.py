# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Dict, Any, Optional

import epint
from ..modules.authentication.auth_manager import Authentication
from ..modules.http_client import HTTPClient
from ..modules.error_handler import ErrorHandler
from ..modules.date_range_handler import DateRangeHandler
from ..modules.pagination_handler import PaginationHandler
from ..modules.search.find_closest import find_closest_match
from ..modules.repr_formatter.endpoint_repr import format_endpoint_repr
from .swagger import SwaggerModel
from .request_model import RequestModel
from .response_model import ResponseModel


class Endpoint:
    """Endpoint model'ini wrap eden callable sınıf"""
    
    def __init__(self, category: str, name: str, data: Dict[str, Any]):
        self._category = category
        self._name = name
        self._data = data
        self.client = HTTPClient()
        self.date_range_handler = DateRangeHandler()
        self.pagination_handler = PaginationHandler()

    def __repr__(self) -> str:
        """Endpoint bilgilerini detaylı olarak göster"""
        return format_endpoint_repr(self._category, self._name, self._data)
    
    def _extract_all_data_param(self, kwargs: Dict[str, Any]) -> bool:
        """allData parametresini kwargs'tan çıkarır ve boolean değerini döndürür
        
        Args:
            kwargs: Endpoint parametreleri dictionary'si
            
        Returns:
            allData parametresinin boolean değeri (varsayılan: False)
        """
        all_data = False
        all_data_keys = ['allData', 'all_data', 'alldata', 'all-data', 'AllData', 'ALL_DATA']
        
        # Önce direkt eşleşmeleri kontrol et (case-insensitive)
        kwargs_keys_lower = {k.lower(): k for k in kwargs.keys()}
        for key in all_data_keys:
            key_lower = key.lower()
            if key_lower in kwargs_keys_lower:
                original_key = kwargs_keys_lower[key_lower]
                all_data = bool(kwargs.pop(original_key))
                break
        
        # Direkt eşleşme yoksa fuzzy matching yap
        if not all_data and kwargs:
            matched_key = find_closest_match('allData', list(kwargs.keys()), threshold=0.7)
            if matched_key:
                all_data = bool(kwargs.pop(matched_key))
        
        return all_data
    
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        """Endpoint çağrıldığında çalışır"""
        
        # allData parametresini kontrol et ve kwargs'tan çıkar
        all_data = self._extract_all_data_param(kwargs)
        
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

        # ErrorHandler oluştur
        error_handler = ErrorHandler(auth)
        try:
            response = self.client.__getattribute__(method.lower())(
                url,
                **request_args
            )
            # ResponseModel oluştur
            response_model = ResponseModel(self._data, response)
            result_data = response_model.data
            
            # all_data parametresi verildiyse ve pagination varsa tüm sayfaları topla
            if all_data and isinstance(result_data, dict):
                if self.pagination_handler.has_pagination(result_data):
                    result_data = self.pagination_handler.collect_all_pages(
                        result_data,
                        kwargs,
                        self.__call__
                    )
            
            return result_data
        except Exception as e:

            if all_data:
                # Tarih aralığı hatası kontrolü
                is_date_error = self.date_range_handler.is_date_range_error(e)
                
                if is_date_error:
                    result = self.date_range_handler.handle_date_range_error(
                        kwargs,
                        request_model,
                        self.__call__
                    )
                    
                    if result is not None:
                        return result
            
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
