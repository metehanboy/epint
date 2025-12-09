# -*- coding: utf-8 -*-

import re
from typing import Dict, Any, List, Optional, Callable
from ..modules.search.find_closest import find_closest_match


class RequestModel:
    """Endpoint parametrelerine göre request payload ve params oluşturur"""
    
    # Ön tanımlı parametreler ve default değerleri (factory fonksiyonları)
    DEFAULT_PARAMS: Dict[str, Callable[[], Any]] = {
        'page': lambda: {'number': 1, 'size': 1000},
        'region': lambda: 'TR1',
        'regionCode': lambda: 'TR1',
    }
    
    def __init__(self, endpoint_data: Dict[str, Any], kwargs: Dict[str, Any]):
        """
        Request model oluştur
        
        Args:
            endpoint_data: Endpoint model bilgileri (parameters, method, path, vb.)
            kwargs: Kullanıcıdan gelen parametreler
        """
        self._endpoint_data = endpoint_data
        self._category = endpoint_data.get('category', '')
        self._kwargs = kwargs.copy()
        self._params = {}
        self._headers = {}
        self._json = None
        self._data = None
        
        self._parse_parameters()
    
    def _find_param_match(self, param_name: str, available_params: List[str], threshold: float = 0.5) -> Optional[str]:
        """
        Fuzzy matching ile parametre eşleştir
        
        Args:
            param_name: Eşleştirilecek parametre ismi
            available_params: Mevcut parametre isimleri listesi
            threshold: Minimum benzerlik oranı (default: 0.5)
        
        Returns:
            Eşleşen parametre ismi veya None
        """
        if not param_name or not available_params:
            return None
        
        # 1. Önce case-insensitive tam eşleşme kontrolü
        param_lower = param_name.lower()
        for candidate in available_params:
            if candidate.lower() == param_lower:
                return candidate
        
        # 2. Substring eşleşmesi kontrolü (daha kısa isim, daha uzun isimde geçiyor mu?)
        # Örnek: "readingorganizationid" -> "readingOrganizationId" (daha iyi)
        #         "readingorganizationid" -> "meterReadingOrganizationId" (daha kötü)
        param_words = self._split_camel_case(param_lower)
        best_substring_match = None
        best_substring_score = 0.0
        
        for candidate in available_params:
            candidate_lower = candidate.lower()
            candidate_words = self._split_camel_case(candidate_lower)
            
            # Önce tam substring kontrolü (param candidate'ın başında veya sonunda mı?)
            if param_lower in candidate_lower:
                # Param candidate'ın substring'i ise, candidate'ın uzunluğuna göre score ver
                # Daha kısa candidate'lar daha iyi (ör: "readingOrganizationId" < "meterReadingOrganizationId")
                substring_ratio = len(param_lower) / len(candidate_lower)
                if substring_ratio > best_substring_score:
                    best_substring_score = substring_ratio
                    best_substring_match = candidate
            
            # Parametre kelimelerinin kaç tanesi candidate'de geçiyor?
            matched_words = sum(1 for word in param_words if word in candidate_lower)
            score = matched_words / len(param_words) if param_words else 0
            
            # Eğer tüm kelimeler eşleşiyorsa ve candidate daha kısa veya eşit uzunluktaysa öncelik ver
            if matched_words == len(param_words) and len(candidate_lower) <= len(param_lower) * 1.2:
                if score > best_substring_score:
                    best_substring_score = score
                    best_substring_match = candidate
        
        # Tam substring eşleşmesi varsa ve score yeterince yüksekse döndür
        if best_substring_match and best_substring_score >= 0.7:
            return best_substring_match
        
        # 3. Fuzzy matching (SequenceMatcher ile)
        match = find_closest_match(param_name, available_params, threshold=threshold)
        return match
    
    def _split_camel_case(self, name: str) -> List[str]:
        """CamelCase veya snake_case string'i kelimelere ayır"""
        import re
        # Önce büyük harfleri küçük harfe çevir ve önüne boşluk ekle (CamelCase için)
        words = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        # Snake_case ve tire'leri split et
        words = re.sub(r'[_\s-]+', ' ', words)
        # Küçük harfe çevir ve boşluklara göre split et
        result = [w.lower() for w in words.split() if w]
        
        # Eğer tek kelime varsa ve uzunsa, yaygın kelimelere göre böl
        # Örnek: "readingorganizationid" -> ["reading", "organization", "id"]
        if len(result) == 1 and len(result[0]) > 10:
            word = result[0]
            # Yaygın kelimeleri ara
            common_words = ['id', 'code', 'name', 'date', 'time', 'type', 'status', 
                          'organization', 'reading', 'meter', 'point', 'consumption']
            found_words = []
            remaining = word
            
            for common_word in sorted(common_words, key=len, reverse=True):
                if common_word in remaining:
                    idx = remaining.find(common_word)
                    if idx > 0:
                        found_words.append(remaining[:idx])
                    found_words.append(common_word)
                    remaining = remaining[idx + len(common_word):]
            
            if found_words:
                if remaining:
                    found_words.append(remaining)
                return found_words
        
        return result
    
    def _is_service_wrapper(self, schema: Dict[str, Any]) -> bool:
        """
        Service wrapper yapısını tespit et (GOP kategorisi için)
        
        Service wrapper yapısı:
        {
          "properties": {
            "header": { "type": "array", ... },
            "body": { "$ref": "...", ... }  // veya çözülmüş properties
          }
        }
        """
        if not isinstance(schema, dict) or 'properties' not in schema:
            return False
        
        properties = schema['properties']
        # Service wrapper: hem 'header' hem 'body' property'si var
        return 'header' in properties and 'body' in properties
    
    def _get_array_field_mapping(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """
        Array field'ları ve hangi array'e ait olduklarını döndür
        
        Returns:
            Dict[str, str]: {field_name: array_name} mapping'i
            Örnek: {'deliveryDay': 'contracts', 'regionCode': 'contracts'}
        """
        mapping = {}
        
        if not isinstance(schema, dict) or 'properties' not in schema:
            return mapping
        
        # Service wrapper ise body'yi al
        if self._is_service_wrapper(schema):
            body_prop = schema['properties'].get('body', {})
            if isinstance(body_prop, dict) and 'properties' in body_prop:
                schema = body_prop
        
        # Her property'yi kontrol et
        for prop_name, prop_value in schema.get('properties', {}).items():
            if isinstance(prop_value, dict) and prop_value.get('type') == 'array':
                # Array property'si bulundu, items içindeki field'ları al
                items = prop_value.get('items', {})
                if isinstance(items, dict) and 'properties' in items:
                    # Items içindeki field'ları array_name ile eşleştir
                    for nested_field in items['properties'].keys():
                        mapping[nested_field] = prop_name
        
        return mapping
    
    def _extract_nested_array_fields(self, prop_value: Dict[str, Any]) -> List[str]:
        """
        Array property'sinin items'ındaki field'ları çıkar
        
        Örnek:
        {
          "contracts": {
            "type": "array",
            "items": {
              "$ref": "#/definitions/QueryContractRequest"  // çözülmüş olmalı
            }
          }
        }
        """
        fields = []
        if isinstance(prop_value, dict):
            # Array type'ı kontrol et
            if prop_value.get('type') == 'array' and 'items' in prop_value:
                items = prop_value['items']
                if isinstance(items, dict):
                    # Items içindeki properties'leri çıkar ($ref zaten çözülmüş olmalı)
                    if 'properties' in items:
                        fields.extend(items['properties'].keys())
        return fields
    
    def _extract_schema_fields(self, schema: Dict[str, Any]) -> List[str]:
        """
        Schema'dan field isimlerini çıkar (schema zaten SwaggerModel tarafından çözülmüş olmalı)
        
        İki tip yapı desteklenir:
        1. Normal DTO: Direkt properties içindeki field'lar
        2. Service wrapper (GOP): body property'si içindeki field'lar
        
        Ayrıca nested array içindeki field'lar da çıkarılır (örn: contracts[].deliveryDay)
        """
        fields = []
        
        if not isinstance(schema, dict):
            return fields
        
        # Properties yoksa boş döndür
        if 'properties' not in schema:
            return fields
        
        # Service wrapper yapısını kontrol et (GOP kategorisi için)
        if self._is_service_wrapper(schema):
            # Service wrapper: sadece 'body' içindeki field'ları çıkar
            body_prop = schema['properties'].get('body', {})
            if isinstance(body_prop, dict):
                # Body içindeki properties'leri al ($ref zaten SwaggerModel tarafından çözülmüş olmalı)
                if 'properties' in body_prop:
                    # Body'nin properties'lerini ekle
                    for prop_name, prop_value in body_prop['properties'].items():
                        fields.append(prop_name)
                        # Eğer array ise, items içindeki field'ları da ekle
                        nested_fields = self._extract_nested_array_fields(prop_value)
                        fields.extend(nested_fields)
                # Eğer body direkt çözülmüş schema ise (type: object olmadan da gelebilir)
                # body_prop'un kendisi zaten çözülmüş schema olabilir
                elif not body_prop or (isinstance(body_prop, dict) and '$ref' not in body_prop):
                    # Body boş dict veya $ref içermiyorsa, recursive olarak içindeki properties'leri kontrol et
                    # Bu durumda body_prop zaten çözülmüş schema olabilir
                    if 'properties' in body_prop:
                        for prop_name, prop_value in body_prop['properties'].items():
                            fields.append(prop_name)
                            nested_fields = self._extract_nested_array_fields(prop_value)
                            fields.extend(nested_fields)
            # 'header' property'sini ignore et (kullanıcıdan gelmez)
            return fields
        
        # Normal DTO yapısı: direkt properties içindeki field'ları çıkar
        for prop_name, prop_value in schema['properties'].items():
            # 'body' property'si özel durum: içindeki field'ları çıkar (body. prefix'i olmadan)
            if prop_name == 'body' and isinstance(prop_value, dict):
                # Body içindeki properties'leri al (zaten çözülmüş olmalı)
                if 'properties' in prop_value:
                    for nested_prop_name, nested_prop_value in prop_value['properties'].items():
                        fields.append(nested_prop_name)
                        nested_fields = self._extract_nested_array_fields(nested_prop_value)
                        fields.extend(nested_fields)
                continue
            
            # Diğer property'ler için normal işlem
            if isinstance(prop_value, dict):
                if 'properties' in prop_value:
                    # Nested object varsa içindeki field'ları ekle
                    fields.extend(prop_value['properties'].keys())
                else:
                    # Normal property
                    fields.append(prop_name)
                    # Array ise nested field'ları da ekle
                    nested_fields = self._extract_nested_array_fields(prop_value)
                    fields.extend(nested_fields)
            else:
                # Normal property
                fields.append(prop_name)
        
        return fields
    
    def _categorize_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Parametreleri tipine göre kategorize et"""
        categorized = {
            'body': [],
            'query': [],
            'header': [],
            'path': []
        }
        
        for param in parameters:
            param_in = param.get('in', '')
            if param_in in categorized:
                categorized[param_in].append(param)
        
        return categorized
    
    def _match_and_extract_params(
        self, 
        param_names: List[str], 
        target_dict: Dict[str, Any],
        remove_from_kwargs: bool = True
    ) -> Dict[str, Any]:
        """
        Parametreleri fuzzy matching ile eşleştir ve çıkar
        
        Args:
            param_names: Eşleştirilecek parametre isimleri listesi
            target_dict: Eşleşen parametrelerin ekleneceği dict
            remove_from_kwargs: Eşleşen parametreleri kwargs'tan çıkar mı
        
        Returns:
            Eşleşen parametrelerin dict'i
        """
        matched = {}
        kwargs_to_remove = []
        
        # Parametre isimlerini listeye çevir (boş liste kontrolü)
        if not param_names:
            return matched
        
        for kwarg_name, kwarg_value in list(self._kwargs.items()):
            matched_name = self._find_param_match(kwarg_name, param_names)
            if matched_name:
                matched[matched_name] = kwarg_value
                target_dict[matched_name] = kwarg_value
                kwargs_to_remove.append(kwarg_name)
        
        if remove_from_kwargs:
            for kwarg_name in kwargs_to_remove:
                self._kwargs.pop(kwarg_name)
        
        return matched
    
    def _apply_default_params(self, target_dict: Dict[str, Any], param_names: List[str]):
        """
        Eksik zorunlu parametrelere default değerleri uygula
        
        Args:
            target_dict: Parametrelerin ekleneceği dict (params, headers, json body)
            param_names: Endpoint'te tanımlı parametre isimleri listesi
        """
        for param_name, default_factory in self.DEFAULT_PARAMS.items():
            # Parametre endpoint'te tanımlı mı ve kullanıcı vermemiş mi kontrol et
            if param_name in param_names and param_name not in target_dict:
                # Factory fonksiyonunu çağırarak yeni değer oluştur
                default_value = default_factory()
                # None değerleri ekleme, sadece gerçek default değerleri ekle
                if default_value is not None:
                    target_dict[param_name] = default_value
    
    def _process_query_params(self, query_params: List[Dict[str, Any]]):
        """Query parametrelerini işle"""
        query_param_names = [p.get('name', '') for p in query_params]
        self._match_and_extract_params(query_param_names, self._params)
        # Default parametreleri uygula
        self._apply_default_params(self._params, query_param_names)
    
    def _process_header_params(self, header_params: List[Dict[str, Any]]):
        """Header parametrelerini işle"""
        header_param_names = [p.get('name', '') for p in header_params]
        self._match_and_extract_params(header_param_names, self._headers)
        # Default parametreleri uygula
        self._apply_default_params(self._headers, header_param_names)
    
    def _process_path_params(self, path_params: List[Dict[str, Any]]):
        """Path parametrelerini işle (şimdilik sadece kwargs'tan çıkar)"""
        path_param_names = [p.get('name', '') for p in path_params]
        self._match_and_extract_params(path_param_names, {}, remove_from_kwargs=True)
    
    def _process_body_params(self, body_params: List[Dict[str, Any]]):
        """Body parametrelerini işle"""
        if not body_params:
            # Body parametresi yoksa ama kwargs varsa, json olarak ekle
            if self._kwargs:
                self._json = self._kwargs.copy()
            return
        
        body_param = body_params[0]  # Genelde tek body parametresi var
        schema = body_param.get('schema', {})
        
        # Schema'dan field'ları çıkar (schema zaten SwaggerModel tarafından çözülmüş)
        body_field_names = self._extract_schema_fields(schema)
        
        # Array field mapping'i al (hangi field hangi array'e ait)
        array_field_mapping = self._get_array_field_mapping(schema)
        
        # Body field'ları için fuzzy matching yap
        matched_body = {}
        if body_field_names:
            # Schema field'ları varsa fuzzy matching yap
            matched_body = self._match_and_extract_params(body_field_names, matched_body, remove_from_kwargs=True)
        else:
            # Schema field'ları yoksa kalan kwargs'ları direkt kullan
            matched_body = self._kwargs.copy()
            self._kwargs.clear()
        
        # Default parametreleri body'ye uygula
        if body_field_names:
            self._apply_default_params(matched_body, body_field_names)
        
        # Nested array field'larını ilgili array'lere ekle
        if array_field_mapping:
            # Hangi array'ler var ve hangi field'lar bunlara ait
            array_data = {}  # {array_name: {field: value}}
            
            # Önce array field'larını topla
            for field_name, array_name in array_field_mapping.items():
                if field_name in matched_body:
                    if array_name not in array_data:
                        array_data[array_name] = {}
                    array_data[array_name][field_name] = matched_body.pop(field_name)
            
            # Array'leri matched_body'ye ekle
            for array_name, array_fields in array_data.items():
                if array_name not in matched_body:
                    matched_body[array_name] = []
                # Array içine object olarak ekle
                matched_body[array_name].append(array_fields)
        
        # Body'yi ayarla
        if matched_body:
            consumes = self._endpoint_data.get('consumes', [])
            if 'application/json' in consumes:
                self._json = matched_body
            else:
                self._data = matched_body
    
    def _parse_parameters(self):
        """Endpoint parametrelerine göre kwargs'ları parse et"""
        parameters = self._endpoint_data.get('parameters', [])
        
        # Parametreleri kategorize et
        categorized = self._categorize_parameters(parameters)
        
        # Her parametre tipini sırayla işle
        self._process_query_params(categorized['query'])
        self._process_header_params(categorized['header'])
        self._process_path_params(categorized['path'])
        self._process_body_params(categorized['body'])
        
        # Content-Type header'ı ekle
        consumes = self._endpoint_data.get('consumes', [])
        if consumes:
            if 'application/json' in consumes:
                self._headers['Content-Type'] = 'application/json'
            else:
                self._headers['Content-Type'] = consumes[0]
        
        # Accept header'ı ekle
        produces = self._endpoint_data.get('produces', [])
        if produces:
            if 'application/json' in produces:
                self._headers['Accept'] = 'application/json'
            else:
                self._headers['Accept'] = produces[0]
    
    @property
    def params(self) -> Dict[str, Any]:
        """Query parametreleri"""
        return self._params
    
    @property
    def headers(self) -> Dict[str, Any]:
        """HTTP header'ları"""
        return self._headers
    
    @property
    def json(self) -> Optional[Dict[str, Any]]:
        """JSON body (varsa)"""
        return self._json
    
    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """Form data (varsa)"""
        return self._data
    
    def to_dict(self) -> Dict[str, Any]:
        """Request bilgilerini dict olarak döndür"""
        result = {
            'params': self._params,
            'headers': self._headers,
        }
        
        if self._json:
            result['json'] = self._json
        if self._data:
            result['data'] = self._data
        
        return result
    
    def __repr__(self) -> str:
        """Request model bilgisini göster"""
        return f"<RequestModel: params={len(self._params)}, headers={len(self._headers)}, json={self._json is not None}, data={self._data is not None}>"

