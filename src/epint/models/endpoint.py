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

    def __repr__(self) -> str:
        """Endpoint bilgilerini detaylı olarak göster"""
        lines = [f"{self._category} | {self._name}"]
        
        # Summary/Description
        summary = self._data.get('summary', '')
        description = self._data.get('description', '')
        if summary:
            lines.append(f"Summary: {summary}")
        if description and description != summary:
            lines.append(f"Description: {description[:100]}..." if len(description) > 100 else f"Description: {description}")
        
        # Method ve Path
        method = self._data.get('method', '')
        path = self._data.get('path', '')
        if method and path:
            lines.append(f"{method} {path}")
        
        # Parameters
        parameters = self._data.get('parameters', [])
        if parameters:
            lines.append("\nParameters:")
            for param in parameters[:10]:  # İlk 10 parametreyi göster
                param_info = []
                param_name = param.get('name', '')
                param_type = param.get('type', '')
                param_format = param.get('format', '')
                param_in = param.get('in', '')
                param_required = param.get('required', False)
                param_desc = param.get('description', '')
                
                # Schema'dan example değerleri çıkar
                example_value = None
                schema = param.get('schema', {})
                
                # Service wrapper kontrolü (GOP kategorisi için)
                is_service_wrapper = False
                if isinstance(schema, dict) and 'properties' in schema:
                    props = schema.get('properties', {})
                    if 'header' in props and 'body' in props:
                        is_service_wrapper = True
                
                if isinstance(schema, dict):
                    example_value = schema.get('example')
                    if not example_value and 'properties' in schema:
                        # İlk property'den example al
                        props = schema.get('properties', {})
                        if props:
                            first_prop = list(props.values())[0]
                            example_value = first_prop.get('example')
                
                param_info.append(f"  - {param_name}")
                if param_in:
                    param_info.append(f"({param_in})")
                if param_type:
                    param_info.append(f": {param_type}")
                if param_format:
                    param_info.append(f"[{param_format}]")
                if param_required:
                    param_info.append("[REQUIRED]")
                if example_value is not None:
                    param_info.append(f"example: {example_value}")
                if param_desc:
                    desc_short = param_desc[:50] + "..." if len(param_desc) > 50 else param_desc
                    param_info.append(f"- {desc_short}")
                
                lines.append(" ".join(param_info))
                
                # Body parametresi içindeki properties'leri göster
                if param_name == 'body' and isinstance(schema, dict):
                    # Service wrapper kontrolü (GOP kategorisi için)
                    if is_service_wrapper:
                        body_schema = schema.get('properties', {}).get('body', {})
                        if isinstance(body_schema, dict) and 'properties' in body_schema:
                            lines.append("    Service Wrapper Body Parameters:")
                            self._format_schema_properties(body_schema.get('properties', {}), lines, indent=6, max_depth=5)
                    # Normal body parametresi (seffaflik, epys vb.)
                    elif 'properties' in schema:
                        lines.append("    Body Parameters:")
                        self._format_schema_properties(schema.get('properties', {}), lines, indent=4, max_depth=5)
            
            if len(parameters) > 10:
                lines.append(f"  ... and {len(parameters) - 10} more parameters")
        
        # Responses
        responses = self._data.get('responses', {})
        if responses:
            lines.append("\nResponses:")
            for status_code, response_data in list(responses.items())[:5]:  # İlk 5 response'u göster
                resp_info = [f"  {status_code}:"]
                resp_desc = response_data.get('description', '')
                if resp_desc:
                    resp_info.append(resp_desc[:60] + "..." if len(resp_desc) > 60 else resp_desc)
                
                # Response schema yapısını göster
                resp_schema = response_data.get('schema', {})
                if isinstance(resp_schema, dict):
                    resp_type = resp_schema.get('type', '')
                    if resp_type:
                        resp_info.append(f"({resp_type})")
                    elif 'properties' in resp_schema:
                        props_count = len(resp_schema.get('properties', {}))
                        resp_info.append(f"(object with {props_count} properties)")
                
                lines.append(" ".join(resp_info))
            
            if len(responses) > 5:
                lines.append(f"  ... and {len(responses) - 5} more responses")
        
        return "\n".join(lines)
    
    def _format_schema_properties(self, properties: Dict[str, Any], lines: List[str], indent: int = 2, max_depth: int = 5, current_depth: int = 0):
        """Schema properties'lerini recursive olarak formatla"""
        if current_depth >= max_depth:
            return
        
        indent_str = " " * indent
        for prop_name, prop_value in list(properties.items())[:20]:  # İlk 20 property
            if not isinstance(prop_value, dict):
                continue
            
            prop_type = prop_value.get('type', '')
            prop_format = prop_value.get('format', '')
            prop_desc = prop_value.get('description', '')
            prop_example = prop_value.get('example')
            prop_enum = prop_value.get('enum')
            
            # Object tipinde ise içindeki property isimlerini göster
            nested_props = None
            if prop_type == 'object' and 'properties' in prop_value:
                nested_props = prop_value.get('properties', {})
            
            # Array tipinde ise items içindeki yapıyı kontrol et
            array_items = None
            if prop_type == 'array' and 'items' in prop_value:
                array_items = prop_value.get('items', {})
            
            prop_info = [f"{indent_str}- {prop_name}"]
            
            if prop_type:
                prop_info.append(f": {prop_type}")
                # Object ise içindeki property isimlerini göster
                if prop_type == 'object' and nested_props:
                    prop_names = list(nested_props.keys())[:5]
                    prop_names_str = ", ".join(prop_names)
                    if len(nested_props) > 5:
                        prop_names_str += f", ... ({len(nested_props)} total)"
                    prop_info.append(f" {{{prop_names_str}}}")
                # Array ise items tipini göster
                elif prop_type == 'array' and isinstance(array_items, dict):
                    items_type = array_items.get('type', '')
                    if items_type == 'object' and 'properties' in array_items:
                        items_props = array_items.get('properties', {})
                        items_prop_names = list(items_props.keys())[:5]
                        items_prop_names_str = ", ".join(items_prop_names)
                        if len(items_props) > 5:
                            items_prop_names_str += f", ... ({len(items_props)} total)"
                        prop_info.append(f"[object {{{items_prop_names_str}}}]")
                    elif items_type:
                        prop_info.append(f"[{items_type}]")
            if prop_format:
                prop_info.append(f"[{prop_format}]")
            if prop_enum:
                enum_str = ", ".join([str(e) for e in prop_enum[:3]])
                if len(prop_enum) > 3:
                    enum_str += f", ... ({len(prop_enum)} total)"
                prop_info.append(f"enum: [{enum_str}]")
            if prop_example is not None:
                example_str = str(prop_example)
                if len(example_str) > 30:
                    example_str = example_str[:30] + "..."
                prop_info.append(f"example: {example_str}")
            if prop_desc:
                desc_short = prop_desc[:40] + "..." if len(prop_desc) > 40 else prop_desc
                prop_info.append(f"- {desc_short}")
            
            lines.append(" ".join(prop_info))
            
            # Nested properties (object içinde) - detaylı göster
            if prop_type == 'object' and nested_props:
                self._format_schema_properties(nested_props, lines, indent + 2, max_depth, current_depth + 1)
            
            # Array items içindeki properties - detaylı göster
            if prop_type == 'array' and isinstance(array_items, dict):
                if array_items.get('type') == 'object' and 'properties' in array_items:
                    lines.append(f"{indent_str}  Array items (object):")
                    self._format_schema_properties(array_items.get('properties', {}), lines, indent + 4, max_depth, current_depth + 1)
        
        if len(properties) > 20:
            lines.append(f"{indent_str}... and {len(properties) - 20} more properties")
    
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
