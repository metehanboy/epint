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

import json
import re
import warnings
from collections import defaultdict
from typing import Dict, Any, List, Optional

from ..modules.search.method_name_decorator import to_python_method_name

# Bazı EPİAŞ swagger kaynaklarında operationId güvenilir değil:
# - "#{...}" / "${...}" içeren, hiç çözülmemiş şablon (i18n/property key eksik)
# - Springfox'un varsayılan "XController_method_VERB" nickname'i (özel nickname verilmemiş)
# - operationId'nin kendisi zaten path'in birebir kopyası
# Bu durumlarda path'ten isim türetmek daha güvenilir ve daha okunaklı sonuç verir.
_UNRESOLVED_TEMPLATE_RE = re.compile(r'[#$]\{')
_CONTROLLER_NICKNAME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9]*Controller_[A-Za-z0-9]+_(GET|POST|PUT|DELETE|PATCH)$')
_BOILERPLATE_PATH_SEGMENTS = {'rest', 'v1', 'v2', 'api'}


def _is_unreliable_operation_id(operation_id: str) -> bool:
    if not operation_id:
        return True
    stripped = operation_id.strip()
    if _UNRESOLVED_TEMPLATE_RE.search(stripped):
        return True
    if _CONTROLLER_NICKNAME_RE.match(stripped):
        return True
    if stripped.startswith('/'):
        return True
    return False


def _name_from_path(path: str) -> str:
    segments = [
        seg for seg in path.split('/')
        if seg and seg.lower() not in _BOILERPLATE_PATH_SEGMENTS
    ]
    return to_python_method_name('/' + '/'.join(segments))


class SwaggerModel:
    """Swagger JSON modeli - tüm swagger verilerini tutar"""
    
    def __init__(self, swagger_path: str):
        """Swagger dosyasını yükle ve parse et"""
        self._swagger_path = swagger_path
        with open(swagger_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)

        self._parse()
    
    def _parse(self):
        """Swagger verisini parse et"""
        self.info = self._data.get('info', {})
        self.host = self._data.get('host', '')
        self.base_path = self._data.get('basePath', '')
        self.definitions = self._data.get('definitions', {})
        self.paths = self._data.get('paths', {})
        self.tags = self._data.get('tags', [])
        self.endpoints = self._parse_endpoints()
    
    def _parse_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Path'leri endpoint'lere çevir"""
        raw_entries = []  # [name, path, method, method_data, operation_id]

        for path, path_item in self.paths.items():
            for method, method_data in path_item.items():
                if method not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue

                operation_id = method_data.get('operationId', '')

                if _is_unreliable_operation_id(operation_id):
                    name = _name_from_path(path)
                else:
                    name = operation_id.replace('-', '_')

                raw_entries.append([name, path, method, method_data, operation_id])

        self._resolve_name_collisions(raw_entries)

        endpoints = {}
        for name, path, method, method_data, operation_id in raw_entries:
            endpoints[name] = {
                'host': self.host,
                'basePath': self.base_path,
                'path': path,
                'method': method.upper(),
                'operation_id': operation_id,
                'summary': method_data.get('summary', ''),
                'description': method_data.get('description', ''),
                'tags': method_data.get('tags', []),
                'consumes': method_data.get('consumes', []),
                'produces': method_data.get('produces', []),
                'parameters': self._parse_parameters(method_data.get('parameters', [])),
                'responses': self._parse_responses(method_data.get('responses', {})),
            }

        return endpoints

    def _resolve_name_collisions(self, raw_entries: List[list]) -> None:
        """
        Aynı isme düşen (operationId çakışması ya da tesadüfi eşleşme) entry'leri
        path'ten türetilmiş isimlerle ayrıştır; bu da yetmezse sayısal suffix ekle.
        Çözülmemiş çakışma sessizce üzerine yazma yerine veri kaybına yol açacağından
        (aynı isim = dict'te tek slot), her düzeltme uyarı olarak bildirilir.
        """
        groups = defaultdict(list)
        for entry in raw_entries:
            groups[entry[0]].append(entry)

        for name, entries in groups.items():
            if len(entries) <= 1:
                continue

            warnings.warn(
                f"epint: '{self._swagger_path}' içinde '{name}' operationId'i "
                f"{len(entries)} farklı endpoint'te tekrarlanıyor "
                f"({', '.join(e[1] for e in entries)}); path'ten türetilen isimlerle ayrıştırıldı.",
                stacklevel=3,
            )
            for entry in entries:
                entry[0] = _name_from_path(entry[1])

        # Path'ten türetme sonrası hâlâ çakışma kalmışsa (örn. aynı path'te
        # birden fazla HTTP metodu) sayısal suffix ile kesin benzersizlik sağla.
        final_groups = defaultdict(list)
        for entry in raw_entries:
            final_groups[entry[0]].append(entry)

        for name, entries in final_groups.items():
            if len(entries) <= 1:
                continue
            for suffix, entry in enumerate(entries[1:], start=2):
                entry[0] = f"{name}_{suffix}"

    def _parse_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parametreleri parse et"""
        parsed = []
        for param in parameters:
            param_data = {
                'name': param.get('name', ''),
                'in': param.get('in', ''),
                'required': param.get('required', False),
                'type': param.get('type', ''),
                'format': param.get('format', ''),
                'description': param.get('description', ''),
            }
            
            # Schema referansı varsa
            if 'schema' in param:
                schema = param['schema']
                if '$ref' in schema:
                    resolved_schema = self._resolve_ref_recursive(schema['$ref'])
                    if resolved_schema:
                        # Resolved schema'yı da tamamen çöz (nested $ref'ler ve properties içindeki $ref'ler için)
                        param_data['schema'] = self._resolve_all_refs(resolved_schema)
                    else:
                        param_data['schema'] = None
                else:
                    # Schema içindeki tüm $ref'leri recursive olarak çöz
                    param_data['schema'] = self._resolve_all_refs(schema)
            
            # Items (array için)
            if 'items' in param:
                param_data['items'] = self._resolve_all_refs(param['items'])
            
            parsed.append(param_data)
        
        return parsed
    
    def _parse_responses(self, responses: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Response'ları parse et"""
        parsed = {}
        for status_code, response_data in responses.items():
            parsed[status_code] = {
                'description': response_data.get('description', ''),
                'schema': None,
            }
            
            if 'schema' in response_data:
                schema = response_data['schema']
                if '$ref' in schema:
                    parsed[status_code]['schema'] = self._resolve_ref_recursive(schema['$ref'])
                else:
                    parsed[status_code]['schema'] = self._resolve_all_refs(schema)
        
        return parsed
    
    def _resolve_ref_recursive(self, ref: str, visited: set = None) -> Optional[Dict[str, Any]]:
        """Definition referansını recursive olarak çöz"""
        if visited is None:
            visited = set()
        
        if ref.startswith('#/definitions/'):
            def_name = ref.replace('#/definitions/', '')
            
            # Circular reference kontrolü
            if def_name in visited:
                return None
            
            visited.add(def_name)
            definition = self.definitions.get(def_name)
            
            if definition:
                # Definition içindeki tüm referansları çöz
                return self._resolve_all_refs(definition, visited)
        
        return None
    
    def _resolve_all_refs(self, obj: Any, visited: set = None) -> Any:
        """Objedeki tüm $ref referanslarını recursive olarak çöz"""
        if visited is None:
            visited = set()
        
        if isinstance(obj, dict):
            # $ref varsa çöz
            if '$ref' in obj and len(obj) == 1:
                return self._resolve_ref_recursive(obj['$ref'], visited)
            
            # Dict içindeki tüm değerleri recursive olarak işle
            resolved = {}
            for key, value in obj.items():
                if key == '$ref':
                    # $ref'i çöz ama diğer key'lerle birlikte varsa koru
                    ref_value = self._resolve_ref_recursive(value, visited)
                    if ref_value:
                        resolved.update(ref_value)
                else:
                    resolved[key] = self._resolve_all_refs(value, visited)
            return resolved
        
        elif isinstance(obj, list):
            # List içindeki tüm elemanları recursive olarak işle
            return [self._resolve_all_refs(item, visited) for item in obj]
        
        return obj
    
    def get_endpoint(self, name: str) -> Optional[Dict[str, Any]]:
        """Endpoint al"""
        return self.endpoints.get(name)
    
    def get_all_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Tüm endpoint'leri al"""
        return self.endpoints
