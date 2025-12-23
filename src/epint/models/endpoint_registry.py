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

from .swagger import SwaggerModel
from .endpoint_callable import Endpoint


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


__all__ = ['EndpointModel']

