# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Dict, Any, List, Optional
import re
import unicodedata
from .endpoint_models import EndpointParameter, EndpointInfo


def sanitize_method_name(text: str) -> str:
    """Method ismi için sanitize fonksiyonu
    
    Args:
        text: operationId, summary veya description
        
    Returns:
        str: Python method ismi olarak kullanılabilir string
    """
    if not text:
        return ""
    
    # Türkçe karakterleri normalize et
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Küçük harfe çevir
    text = text.lower()
    
    # Özel karakterleri temizle ve boşluk/tire/underscore ile ayır
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Boşluk, tire, underscore'ı normalize et
    text = re.sub(r'[\s\-_]+', '_', text)
    
    # Çoklu underscore'ları tek yap
    text = re.sub(r'_+', '_', text)
    
    # Başta/sonda underscore varsa temizle
    text = text.strip('_')
    
    # Python keyword'leri kontrolü
    python_keywords = {
        'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
        'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global',
        'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'with', 'yield'
    }
    
    if text in python_keywords:
        text = f"{text}_endpoint"
    
    # Boş ise veya sadece sayı ise
    if not text or text.isdigit():
        return ""
    
    return text


def extract_method_name_from_swagger(operation: Dict[str, Any]) -> str:
    """Swagger operation'dan method ismi çıkar
    
    Öncelik sırası:
    1. operationId (eğer uygunsa)
    2. summary (eğer uygunsa)
    3. description (ilk cümle)
    
    Args:
        operation: Swagger operation dict
        
    Returns:
        str: Method ismi
    """
    # 1. operationId'yi dene
    operation_id = operation.get("operationId", "")
    if operation_id:
        sanitized = sanitize_method_name(operation_id)
        if sanitized:
            return sanitized
    
    # 2. summary'yi dene
    summary = operation.get("summary", "")
    if summary:
        sanitized = sanitize_method_name(summary)
        if sanitized:
            return sanitized
    
    # 3. description'dan ilk cümleyi al
    description = operation.get("description", "")
    if description:
        # İlk cümleyi al (nokta veya boşluk ile biten)
        first_sentence = description.split('.')[0].split('\n')[0].strip()
        if first_sentence:
            sanitized = sanitize_method_name(first_sentence)
            if sanitized:
                return sanitized
    
    return ""


def resolve_ref(ref: str, definitions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """$ref referansını çöz
    
    Args:
        ref: $ref string (örn: "#/definitions/BrgQueryRequestDto")
        definitions: Swagger definitions dict
        
    Returns:
        Dict veya None
    """
    if not ref or not ref.startswith("#/definitions/"):
        return None
    
    ref_name = ref.replace("#/definitions/", "")
    return definitions.get(ref_name)


def parse_swagger_parameter(param: Dict[str, Any], definitions: Dict[str, Any]) -> EndpointParameter:
    """Swagger parameter'ını parse et
    
    Args:
        param: Swagger parameter dict
        definitions: Swagger definitions dict
        
    Returns:
        EndpointParameter
    """
    param_name = param.get("name", "")
    param_in = param.get("in", "")
    param_type = param.get("type", "string")
    param_schema = param.get("schema")
    
    # Schema varsa ve $ref içeriyorsa çöz
    if param_schema:
        ref = param_schema.get("$ref")
        if ref:
            resolved = resolve_ref(ref, definitions)
            if resolved:
                # Resolved schema'dan type ve properties al
                param_type = resolved.get("type", "object")
                properties = resolved.get("properties", {})
            else:
                param_type = "object"
                properties = {}
        else:
            param_type = param_schema.get("type", param_type)
            properties = param_schema.get("properties", {})
    else:
        properties = {}
    
    # Properties varsa nested parametreler oluştur
    nested_properties = None
    if properties:
        nested_properties = []
        
        # GOP için özel kontrol: body içinde header ve body varsa, body içindeki parametreleri aç
        # header otomatik dolduruluyor, sadece body içindeki parametreleri göster
        if param_name == "body" and "header" in properties and "body" in properties:
            # Body içindeki body'yi al
            body_prop = properties.get("body")
            if isinstance(body_prop, dict):
                body_ref = body_prop.get("$ref")
                if body_ref:
                    body_resolved = resolve_ref(body_ref, definitions)
                    if body_resolved:
                        # Body içindeki properties'i al
                        body_properties = body_resolved.get("properties", {})
                        body_required = body_resolved.get("required", [])
                        
                        # Body içindeki parametreleri nested_properties'e ekle
                        for body_prop_name, body_prop_data in body_properties.items():
                            if isinstance(body_prop_data, dict):
                                body_prop_type = body_prop_data.get("type", "string")
                                # Format varsa kullan (date-time -> datetime)
                                if body_prop_data.get("format") == "date-time":
                                    body_prop_type = "datetime"
                                elif body_prop_data.get("format") == "date":
                                    body_prop_type = "date"
                                
                                # $ref varsa çöz
                                body_prop_ref = body_prop_data.get("$ref")
                                if body_prop_ref:
                                    body_prop_resolved = resolve_ref(body_prop_ref, definitions)
                                    if body_prop_resolved:
                                        body_prop_type = body_prop_resolved.get("type", "object")
                                
                                # Required kontrolü
                                body_required_flag = body_prop_name in body_required if isinstance(body_required, list) else False
                                
                                nested_properties.append(
                                    EndpointParameter(
                                        name=body_prop_name,
                                        var_type=body_prop_type,
                                        description=body_prop_data.get("description", ""),
                                        required=body_required_flag,
                                        example=body_prop_data.get("example"),
                                        properties=None,
                                        items=body_prop_data.get("items"),
                                    )
                                )
        else:
            # Normal durum: tüm properties'i ekle
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict):
                    prop_type = prop_data.get("type", "string")
                    # Format varsa kullan (date-time -> datetime)
                    if prop_data.get("format") == "date-time":
                        prop_type = "datetime"
                    elif prop_data.get("format") == "date":
                        prop_type = "date"
                    
                    # $ref varsa çöz
                    prop_ref = prop_data.get("$ref")
                    resolved = None
                    if prop_ref:
                        resolved = resolve_ref(prop_ref, definitions)
                        if resolved:
                            prop_type = resolved.get("type", "object")
                    
                    # Required kontrolü
                    required = False
                    if resolved:
                        required_list = resolved.get("required", [])
                        required = prop_name in required_list if isinstance(required_list, list) else False
                    else:
                        required = prop_data.get("required", False)
                    
                    nested_properties.append(
                        EndpointParameter(
                            name=prop_name,
                            var_type=prop_type,
                            description=prop_data.get("description", ""),
                            required=required,
                            example=prop_data.get("example"),
                            properties=None,
                            items=prop_data.get("items"),
                        )
                    )
    
    # Format varsa type'ı güncelle
    param_format = param.get("format")
    if param_format == "date-time":
        param_type = "datetime"
    elif param_format == "date":
        param_type = "date"
    elif param_format == "int64":
        param_type = "int"
    elif param_format == "double" or param_format == "float":
        param_type = "float"
    
    # Array type kontrolü
    if param_type == "array":
        items = param.get("items")
        if items and isinstance(items, dict):
            items_ref = items.get("$ref")
            if items_ref:
                resolved = resolve_ref(items_ref, definitions)
                if resolved:
                    param_type = f"array[{resolved.get('type', 'object')}]"
            else:
                param_type = f"array[{items.get('type', 'object')}]"
    
    return EndpointParameter(
        name=param_name,
        var_type=param_type if param_type != "string" else "str",
        description=param.get("description", ""),
        required=param.get("required", False),
        example=param.get("example"),
        properties=nested_properties,
        items=param.get("items"),
    )


def parse_swagger_path(path: str, path_item: Dict[str, Any], definitions: Dict[str, Any], base_path: str = "") -> List[Dict[str, Any]]:
    """Swagger path'ini parse et ve endpoint'leri çıkar
    
    Args:
        path: Path string (örn: "/v1/brg/query")
        path_item: Path item dict (GET, POST, vb. içerir)
        definitions: Swagger definitions dict
        base_path: Base path (örn: "/balancing-group")
        
    Returns:
        List[Dict]: Endpoint dict'leri
    """
    endpoints = []
    
    # HTTP methodları
    http_methods = ["get", "post", "put", "delete", "patch", "head", "options"]
    
    for method in http_methods:
        if method not in path_item:
            continue
        
        operation = path_item[method]
        
        # Method ismini çıkar
        method_name = extract_method_name_from_swagger(operation)
        
        # Path'ten method ismi türet (fallback veya karşılaştırma için)
        path_parts = path.strip("/").split("/")
        # Path'in son iki kısmını birleştir (örn: /v1/ec-meter/count -> ec-meter/count -> ec_meter_count)
        path_method_name_full = "_".join(path_parts[-2:]) if len(path_parts) >= 2 else path_parts[-1] if path_parts else "endpoint"
        path_method_name_full = sanitize_method_name(path_method_name_full)
        # Path'in sadece son kısmı (örn: /v1/ec-meter/count -> count)
        path_method_name_single = path_parts[-1] if path_parts else ""
        path_method_name_single = sanitize_method_name(path_method_name_single)
        
        if not method_name:
            # Fallback: path'ten method ismi türet (tam path kullan)
            method_name = path_method_name_full
        else:
            # Önce path'in tam method ismi (son iki kısım) ile karşılaştır
            # Eğer path'in tam method ismi operationId ile aynıysa, path'ten çıkanı kullan
            # Bu durumda path'ten çıkan isim daha tutarlı olur
            if path_method_name_full == method_name:
                method_name = path_method_name_full
            # Eğer path'in tam method ismi operationId'den farklıysa ama benzeriyse, path'ten çıkanı kullan
            # Örnek: operationId "ec-meter-count" -> "ec_meter_count", path "ec-meter/count" -> "ec_meter_count"
            elif path_method_name_full and path_method_name_full != path_method_name_single:
                # Normalize edilmiş karşılaştırma (tire ve underscore'ı ignore et)
                method_normalized = method_name.replace("_", "-").replace("-", "")
                path_normalized = path_method_name_full.replace("_", "-").replace("-", "")
                if method_normalized == path_normalized:
                    method_name = path_method_name_full
            # Son olarak, eğer path'in tek method ismi çok kısa ve operationId içinde geçiyorsa, onu kullan
            # Örnek: "available-lookups" içinde "lookup" geçiyor
            # Ama sadece path'in tam method ismi tek kelime ise (yani path_method_name_full == path_method_name_single)
            elif path_method_name_single and len(path_method_name_single) < len(method_name) and \
                 path_method_name_full == path_method_name_single:
                # Path method ismi operationId method isminin sonunda veya içinde geçiyorsa
                if path_method_name_single in method_name or method_name.endswith(path_method_name_single):
                    method_name = path_method_name_single
        
        # Endpoint path'i oluştur
        # base_path service_config'den gelecek, burada sadece path'i kullan
        # base_path'i burada ekleme, service_config'de zaten ekleniyor
        endpoint_path = path if path.startswith("/") else f"/{path}"
        
        # Parametreleri parse et
        parameters = operation.get("parameters", [])
        var_type_list = []
        required_params = []
        
        for param in parameters:
            parsed_param = parse_swagger_parameter(param, definitions)
            var_type_list.append(parsed_param)
            if parsed_param.required:
                required_params.append(parsed_param.name)
        
        # Response structure (basit versiyon)
        response_structure = {}
        responses = operation.get("responses", {})
        if "200" in responses:
            response_200 = responses["200"]
            response_schema = response_200.get("schema")
            if response_schema:
                ref = response_schema.get("$ref")
                if ref:
                    resolved = resolve_ref(ref, definitions)
                    if resolved:
                        # Basit response structure
                        response_structure = {"body": "object"}
        
        # var_type listesini dict formatına çevir
        var_type_dict_list = []
        for p in var_type_list:
            param_dict = {
                "name": p.name,
                "var_type": p.var_type,
                "description": p.description,
                "required": p.required,
                "example": p.example,
            }
            
            # Nested properties varsa ekle
            if p.properties:
                param_dict["properties"] = [
                    {
                        "name": np.name,
                        "type": np.var_type,
                        "description": np.description,
                        "required": np.required,
                        "example": np.example,
                    }
                    for np in p.properties
                ]
            
            if p.items:
                param_dict["items"] = p.items
            
            var_type_dict_list.append(param_dict)
        
        endpoint_data = {
            "endpoint": endpoint_path,
            "method": method.upper(),
            "auth": True,  # Varsayılan olarak auth gerekli
            "short_name": method_name,
            "short_name_tr": operation.get("summary", operation.get("description", ""))[:100],
            "params": [p.name for p in var_type_list],
            "required": required_params if required_params else None,
            "response": [],
            "var_type": var_type_dict_list,
            "summary": operation.get("summary", ""),
            "description": operation.get("description", ""),
            "response_structure": response_structure,
        }
        
        endpoints.append({
            "method_name": method_name,
            "endpoint_data": endpoint_data,
        })
    
    return endpoints


def parse_swagger_file(swagger_path: str, category: str) -> Dict[str, Dict[str, Any]]:
    """Swagger JSON dosyasını parse et
    
    Args:
        swagger_path: Swagger JSON dosya yolu
        category: Kategori adı
        
    Returns:
        Dict: method_name -> endpoint_data mapping
    """
    import json
    
    with open(swagger_path, "r", encoding="utf-8") as f:
        swagger_data = json.load(f)
    
    definitions = swagger_data.get("definitions", {})
    paths = swagger_data.get("paths", {})
    # base_path'i kullanma - service_config zaten root_path'i ekliyor
    # Swagger'daki basePath ile service_config'deki root_path aynı olmalı
    # base_path = swagger_data.get("basePath", "")
    
    endpoints = {}
    method_name_counts = {}  # Method name çakışmalarını takip et
    
    for path, path_item in paths.items():
        # base_path'i parse_swagger_path'e gönderme - service_config zaten root_path'i ekliyor
        parsed_endpoints = parse_swagger_path(path, path_item, definitions, "")
        
        for parsed in parsed_endpoints:
            method_name = parsed["method_name"]
            endpoint_data = parsed["endpoint_data"]
            endpoint_data["category"] = category
            
            # Aynı method_name varsa unique isim oluştur
            if method_name in endpoints:
                # Path'ten unique suffix oluştur
                path_parts = [p for p in path.strip("/").split("/") if p]
                if len(path_parts) >= 2:
                    unique_suffix = "_".join(path_parts[-2:])
                elif len(path_parts) == 1:
                    unique_suffix = path_parts[0]
                else:
                    unique_suffix = "endpoint"
                
                unique_suffix = sanitize_method_name(unique_suffix)
                method_name = f"{method_name}_{unique_suffix}"
            
            # Method name sayısını takip et
            if method_name in method_name_counts:
                method_name_counts[method_name] += 1
                method_name = f"{method_name}_{method_name_counts[method_name]}"
            else:
                method_name_counts[method_name] = 0
            
            endpoints[method_name] = endpoint_data
    
    return endpoints

