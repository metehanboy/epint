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

import io
from typing import Dict, Any, List, Optional, Union
from requests import Response
from ..modules.datetime import DateTimeUtils


class ResponseModel:
    """Response'u parse edip schema'ya göre dönüştüren sınıf"""
    
    def __init__(self, endpoint_data: Dict[str, Any], response: Response):
        """
        Response model oluştur
        
        Args:
            endpoint_data: Endpoint model bilgileri (responses, method, path, vb.)
            response: HTTP response objesi (requests.Response)
        """
        self._endpoint_data = endpoint_data
        self._category = endpoint_data.get('category', '')
        self._response = response
        self._status_code = str(response.status_code)
        self._raw_data = None
        self._parsed_data = None
        
        self._parse_response()
    
    def _is_binary_content(self) -> bool:
        """Content-Type'a göre binary içerik olup olmadığını kontrol et"""
        content_type = self._response.headers.get('Content-Type', '').lower()
        
        # Binary content type'lar
        binary_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # XLSX
            'application/vnd.ms-excel',  # XLS
            'application/pdf',  # PDF
            'application/octet-stream',  # Genel binary
            'application/zip',  # ZIP
            'application/x-zip-compressed',  # ZIP
            'application/vnd.ms-powerpoint',  # PPT
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # PPTX
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
            'application/msword',  # DOC
            'image/',  # Tüm image tipleri
            'video/',  # Tüm video tipleri
            'audio/',  # Tüm audio tipleri
        ]
        
        # Binary type kontrolü
        for binary_type in binary_types:
            if content_type.startswith(binary_type):
                return True
        
        return False
    
    def _parse_response(self):
        """Response'u parse et ve schema'ya göre dönüştür"""
        # Binary içerik kontrolü
        if self._is_binary_content():
            # Binary ise BytesIO olarak döndür
            self._raw_data = self._response.content
            self._parsed_data = io.BytesIO(self._response.content)
            return
        
        # JSON response
        try:
            self._raw_data = self._response.json()
        except (ValueError, AttributeError):
            # JSON değilse text olarak al
            self._raw_data = self._response.text
        
        # Response schema'yı al
        responses = self._endpoint_data.get('responses', {})
        response_schema = None
        
        # Status code'a göre schema bul
        if self._status_code in responses:
            response_data = responses[self._status_code]
            response_schema = response_data.get('schema')
        elif '200' in responses:
            # 200 yoksa default olarak 200'ü kullan
            response_data = responses['200']
            response_schema = response_data.get('schema')
        
        # Schema varsa dönüştür
        if response_schema and isinstance(self._raw_data, dict):
            self._parsed_data = self._convert_by_schema(self._raw_data, response_schema)
        else:
            self._parsed_data = self._raw_data
    
    def _convert_value_by_format(self, value: Any, prop_schema: Dict[str, Any]) -> Any:
        """
        Format tipine göre değeri dönüştür
        
        Args:
            value: Dönüştürülecek değer
            prop_schema: Property schema bilgisi (type, format içerir)
        
        Returns:
            Dönüştürülmüş değer
        """
        if value is None:
            return value
        
        format_type = prop_schema.get('format', '')
        prop_type = prop_schema.get('type', '')
        
        # date-time formatı
        if format_type == 'date-time':
            if isinstance(value, str):
                try:
                    dt = DateTimeUtils.from_string(value)
                    return dt
                except (ValueError, TypeError):
                    return value
        
        # integer formatları
        if format_type in ('int64', 'int32') or prop_type == 'integer':
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        
        # float formatları
        if format_type in ('float', 'double') or prop_type == 'number':
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
        
        return value
    
    def _convert_by_schema(self, data: Any, schema: Dict[str, Any]) -> Any:
        """
        Data'yı schema'ya göre dönüştür (recursive)
        
        Args:
            data: Dönüştürülecek data
            schema: Schema bilgisi
        
        Returns:
            Dönüştürülmüş data
        """
        if not isinstance(schema, dict):
            return data
        
        # RestResponse yapısı kontrolü (body'yi çıkar)
        if self._is_rest_response(schema, data):
            # RestResponse yapısı: body'yi çıkar
            if isinstance(data, dict) and 'body' in data:
                body_data = data.get('body')
                body_schema = schema.get('properties', {}).get('body', {})
                if body_schema and isinstance(body_data, dict):
                    # Body schema'sı varsa recursive olarak dönüştür
                    if isinstance(body_schema, dict) and 'properties' in body_schema:
                        return self._convert_by_schema(body_data, body_schema)
                    else:
                        return body_data
                return body_data
            return data
        
        # Service wrapper kontrolü (GOP için)
        if self._is_service_wrapper(schema, data):
            # Service wrapper: body'yi çıkar
            if isinstance(data, dict) and 'body' in data:
                body_data = data.get('body')
                body_prop = schema.get('properties', {}).get('body', {})
                if isinstance(body_prop, dict) and 'properties' in body_prop:
                    return self._convert_by_schema(body_data, body_prop)
                return body_data
            return data
        
        # Normal object yapısı
        if not isinstance(data, dict):
            return data
        
        properties = schema.get('properties', {})
        if not properties:
            return data
        
        result = {}
        
        for key, value in data.items():
            if key in properties:
                prop_schema = properties[key]
                
                # Nested object kontrolü
                if isinstance(value, dict) and 'properties' in prop_schema:
                    result[key] = self._convert_by_schema(value, prop_schema)
                # Array kontrolü
                elif isinstance(value, list) and prop_schema.get('type') == 'array':
                    items_schema = prop_schema.get('items', {})
                    if isinstance(items_schema, dict) and 'properties' in items_schema:
                        result[key] = [
                            self._convert_by_schema(item, items_schema) if isinstance(item, dict) else item
                            for item in value
                        ]
                    else:
                        result[key] = [
                            self._convert_value_by_format(item, items_schema) if items_schema else item
                            for item in value
                        ]
                else:
                    result[key] = self._convert_value_by_format(value, prop_schema)
            else:
                # Schema'da bulunamayan field'ları olduğu gibi bırak
                result[key] = value
        
        return result
    
    def _is_rest_response(self, schema: Dict[str, Any], data: Any) -> bool:
        """
        RestResponse yapısını tespit et
        
        RestResponse yapısı:
        {
          "properties": {
            "status": {...},
            "correlationId": {...},
            "body": {...}
          }
        }
        """
        if not isinstance(schema, dict) or 'properties' not in schema:
            return False
        
        properties = schema.get('properties', {})
        # RestResponse: status, correlationId ve body property'leri var
        has_status = 'status' in properties
        has_correlation_id = 'correlationId' in properties
        has_body = 'body' in properties
        
        return has_status and has_correlation_id and has_body
    
    def _is_service_wrapper(self, schema: Dict[str, Any], data: Any) -> bool:
        """
        Service wrapper yapısını tespit et (GOP kategorisi için)
        
        Service wrapper yapısı:
        {
          "properties": {
            "header": { "type": "array", ... },
            "body": { "$ref": "...", ... }
          }
        }
        """
        if not isinstance(schema, dict) or 'properties' not in schema:
            return False
        
        properties = schema['properties']
        # Service wrapper: hem 'header' hem 'body' property'si var
        return 'header' in properties and 'body' in properties
    
    @property
    def status_code(self) -> int:
        """HTTP status code"""
        return self._response.status_code
    
    @property
    def raw_data(self) -> Any:
        """Ham response data"""
        return self._raw_data
    
    @property
    def data(self) -> Any:
        """Parse edilmiş response data"""
        return self._parsed_data
    
    @property
    def headers(self) -> Dict[str, str]:
        """Response header'ları"""
        return dict(self._response.headers)
    
    def to_dict(self) -> Dict[str, Any]:
        """Response bilgilerini dict olarak döndür"""
        return {
            'status_code': self.status_code,
            'headers': self.headers,
            'data': self._parsed_data,
            'raw_data': self._raw_data
        }
    
    def __repr__(self) -> str:
        """Response model bilgisini göster"""
        return f"<ResponseModel: status_code={self.status_code}, data_type={type(self._parsed_data).__name__}>"

