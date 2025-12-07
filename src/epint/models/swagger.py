
import json
from typing import Dict, Any, List, Optional

class SwaggerModel:
    """Swagger JSON modeli - tüm swagger verilerini tutar"""
    
    def __init__(self, swagger_path: str):
        """Swagger dosyasını yükle ve parse et"""
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
        endpoints = {}
        
        for path, path_item in self.paths.items():
            for method, method_data in path_item.items():
                if method not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                operation_id = method_data.get('operationId', '')
                if not operation_id:
                    continue
                
                method_name = operation_id.replace('-', '_')
                
                endpoints[method_name] = {
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
                    param_data['schema'] = self._resolve_ref_recursive(schema['$ref'])
                else:
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
