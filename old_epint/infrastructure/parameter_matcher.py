# -*- coding: utf-8 -*-

import difflib
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from .type_converter import TypeConverter


def sanitize_param_name(text: str) -> str:
    """Parametre ismi için sanitize fonksiyonu
    
    Parametre eşleştirme için basitleştirilmiş sanitize:
    - Unicode normalize (Türkçe karakterler için)
    - Küçük harfe çevir
    - Tire/underscore normalize (startDate vs start_date)
    - Özel karakterleri temizle
    
    Args:
        text: Parametre ismi
        
    Returns:
        str: Sanitize edilmiş parametre ismi
    """
    if not text:
        return ""
    
    # Türkçe karakterleri normalize et
    text = unicodedata.normalize('NFKD', str(text))
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Küçük harfe çevir
    text = text.lower()
    
    # Özel karakterleri temizle (sadece harf, rakam, tire, underscore bırak)
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Boşluk, tire, underscore'ı normalize et (hepsini underscore'a çevir)
    text = re.sub(r'[\s\-_]+', '_', text)
    
    # Çoklu underscore'ları tek yap
    text = re.sub(r'_+', '_', text)
    
    # Başta/sonda underscore varsa temizle
    text = text.strip('_')
    
    return text


class ParameterMatcher:
    def __init__(self, endpoint_params: List[Any], category: str = ""):
        self.endpoint_params = endpoint_params
        self.category = category

    def fuzzy_match_params(
        self, provided_params: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        matched_params = {}
        unmatched_params = {}
        used_param_names = set()
        used_nested_names = set()  # Nested parametreler için tracking
        
        # Nested parametreler için body/object parametrelerini bul
        body_param_name = None
        
        for param in self.endpoint_params:
            if param.var_type in ["object", "dict"] and param.properties:
                body_param_name = param.name
                break

        for provided_key, provided_value in provided_params.items():
            # Önce top-level eşleşme dene
            best_match = self._find_best_param_match(provided_key, used_param_names)

            # Body parametresi için özel kontrol: body parametresi top-level olarak eşleşmemeli
            # Çünkü body içindeki parametreler nested olarak eşleşmeli
            if best_match == body_param_name:
                # Body parametresi top-level olarak eşleşmemeli, nested olarak işlenmeli
                best_match = None

            # Önce nested (body) parametrelerinde ara (öncelikli)
            # Çünkü start/end gibi parametreler body içindeki startDate/endDate ile eşleşmeli
            nested_match = None
            if body_param_name:
                nested_match = self._find_best_nested_param_match(
                    provided_key, body_param_name, used_nested_names
                )
            
            if nested_match and nested_match not in used_nested_names:
                # Nested eşleşme bulundu, bunu kullan
                if body_param_name not in matched_params:
                    matched_params[body_param_name] = {}
                # Eğer body_param_name zaten bir dict değilse, dict'e çevir
                if not isinstance(matched_params[body_param_name], dict):
                    matched_params[body_param_name] = {}
                matched_params[body_param_name][nested_match] = provided_value
                used_nested_names.add(nested_match)
            elif best_match and best_match not in used_param_names:
                # Top-level eşleşme bulundu ve nested eşleşme yok
                converted_value = self._convert_parameter_value(
                    provided_value, best_match
                )
                matched_params[best_match] = converted_value
                used_param_names.add(best_match)
            else:
                # Hiçbir eşleşme bulunamadı
                unmatched_params[provided_key] = provided_value

        # Body parametresini oluştur (eğer nested parametreler eşleştiyse)
        if body_param_name and body_param_name in matched_params:
            # Body içindeki nested parametreleri dönüştür
            body_data = matched_params[body_param_name]
            converted_body = {}
            for nested_key, nested_value in body_data.items():
                nested_param = self._find_nested_param_definition(body_param_name, nested_key)
                if nested_param:
                    # Nested parametre için type conversion yap
                    converted_value = self._convert_nested_parameter_value(nested_value, nested_param)
                    converted_body[nested_key] = converted_value
                else:
                    converted_body[nested_key] = nested_value
            matched_params[body_param_name] = converted_body
            
            # GOP için özel kontrol: body içindeki body'yi wrap et
            if self.category == "gop" and body_param_name == "body":
                matched_params[body_param_name] = {"body": converted_body}

        self._add_default_values_if_needed(matched_params)

        return matched_params, unmatched_params

    def _add_default_values_if_needed(self, matched_params: Dict[str, Any]) -> None:
        default_values = {
            "region": "TR1",
            "regionCode": "TR1",
            "page": {"page": 1, "size": 1},
            "pageInfo": {"page": 1, "size": 1},
        }

        for param in self.endpoint_params:
            param_name = param.name.lower()

            # Eğer parametre required ise ve eşleşmemişse default değer ver
            if param.required and param.name not in matched_params:
                # Object/dict tipi ise ve properties varsa, nested parametreleri kontrol et
                if param.var_type in ["object", "dict"] and param.properties:
                    if param.name not in matched_params:
                        matched_params[param.name] = {}
                    
                    # Nested required parametreleri kontrol et
                    for nested_param in param.properties:
                        if nested_param.required:
                            nested_name = nested_param.name
                            if nested_name not in matched_params[param.name]:
                                # Nested parametre için default verme (kullanıcı vermeli)
                                continue
                # Özel eşleştirmeler
                elif "region" in param_name:
                    matched_params[param.name] = "TR1"
                elif "pageinfo" in param_name:
                    matched_params[param.name] = {"page": 1, "size": 1}
                elif "page" in param_name and "info" not in param_name:
                    matched_params[param.name] = {"page": 1, "size": 1}
                else:
                    # Diğer required parametreler için genel default değerler
                    if param.var_type == "str":
                        matched_params[param.name] = ""
                    elif param.var_type == "int":
                        matched_params[param.name] = 0
                    elif param.var_type == "datetime":
                        # Datetime için default değer verme, kullanıcı vermeli
                        continue
                    else:
                        matched_params[param.name] = None
            else:
                # Eğer parametre required değilse ve eşleşmemişse default değer ver
                for default_key, default_value in default_values.items():
                    if default_key in param_name and param.name not in matched_params:
                        matched_params[param.name] = default_value
                        break

    def _find_best_param_match(
        self, provided_key: str, used_param_names: set = None
    ) -> Optional[str]:
        if used_param_names is None:
            used_param_names = set()

        best_match = None
        best_score = 0
        
        # Sanitize edilmiş provided_key
        sanitized_provided = sanitize_param_name(provided_key)

        # Önce exact match kontrolü (case-insensitive)
        for param in self.endpoint_params:
            if param.name in used_param_names:
                continue
            if provided_key.lower() == param.name.lower():
                return param.name

        # Period date parametreleri için özel kontrol (periodDateStart, periodDateEnd)
        period_date_patterns = {
            "perioddatestart": "periodDateStart",
            "perioddateend": "periodDateEnd",
            "period_date_start": "periodDateStart",
            "period_date_end": "periodDateEnd",
        }
        sanitized_lower = sanitized_provided.lower()
        if sanitized_lower in period_date_patterns:
            target_name = period_date_patterns[sanitized_lower]
            for param in self.endpoint_params:
                if param.name in used_param_names:
                    continue
                if param.name == target_name:
                    return param.name

        for param in self.endpoint_params:
            # Skip already used parameters
            if param.name in used_param_names:
                continue

            if provided_key == param.name:
                return param.name
            
            # Sanitize edilmiş parametre ismi
            sanitized_param = sanitize_param_name(param.name)
            
            # Sanitize edilmiş isimlerle direkt eşleşme kontrolü
            if sanitized_provided == sanitized_param:
                return param.name

            # Period date parametreleri için özel kontrol
            # periodDateStart -> periodDateStart (exact match öncelikli)
            if sanitized_provided in ["perioddatestart", "period_date_start"]:
                if sanitized_param == "perioddatestart":
                    return param.name
            if sanitized_provided in ["perioddateend", "period_date_end"]:
                if sanitized_param == "perioddateend":
                    return param.name

            # Özel eşleştirme kuralları (sanitize edilmiş isimlerle)
            # Ancak period date parametreleri için effectiveDate ile eşleşmemeli
            if sanitized_provided.startswith("perioddate") and sanitized_param.startswith("effectivedate"):
                continue  # Bu eşleşmeyi atla
            
            if self._check_abbreviation_match(sanitized_provided, sanitized_param):
                # Period date parametreleri için effectiveDate ile eşleşmeyi engelle
                if sanitized_provided.startswith("perioddate") and sanitized_param.startswith("effectivedate"):
                    continue
                return param.name

            scores = []

            scores.append(
                difflib.SequenceMatcher(
                    None, sanitized_provided, sanitized_param
                ).ratio()
            )

            provided_words = sanitized_provided.replace("_", " ").split()
            param_words = sanitized_param.replace("_", " ").split()
            word_score = self._calculate_word_similarity(provided_words, param_words)
            scores.append(word_score)

            abbrev_score = self._calculate_abbreviation_similarity(
                sanitized_provided, sanitized_param
            )
            scores.append(abbrev_score)

            method_score = self._calculate_method_similarity(
                sanitized_provided, sanitized_param
            )
            scores.append(method_score)

            score = max(scores)

            # Period date parametreleri için effectiveDate ile eşleşmeyi engelle
            if sanitized_provided.startswith("perioddate") and sanitized_param.startswith("effectivedate"):
                score = 0  # Bu eşleşmeyi engelle

            if score > best_score and score > 0.3:
                best_match = param.name
                best_score = score

        return best_match

    def _check_start_end_match(self, provided: str, param: str) -> bool:
        """start/end ile ilgili eşleştirmeleri kontrol et (sanitize edilmiş değerlerle çalışır)"""
        # Zaten sanitize edilmiş değerler geliyor, direkt karşılaştır
        provided_sanitized = sanitize_param_name(provided)
        param_sanitized = sanitize_param_name(param)
        
        # Period date parametreleri için özel kontrol - effectiveDate ile eşleşmemeli
        if provided_sanitized.startswith("perioddate") and param_sanitized.startswith("effectivedate"):
            return False
        
        # Period date parametreleri için exact match kontrolü
        if provided_sanitized == "perioddatestart" and param_sanitized == "perioddatestart":
            return True
        if provided_sanitized == "perioddateend" and param_sanitized == "perioddateend":
            return True
        
        # start/end -> startdate/enddate eşleştirmesi
        if provided_sanitized in ["start", "end"]:
            # startdate, starttime gibi kombinasyonlar (öncelikli kontrol)
            if param_sanitized == provided_sanitized + "date" or param_sanitized == provided_sanitized + "time":
                return True
            # startdate, starttime gibi kombinasyonlar (startswith kontrolü)
            if param_sanitized.startswith(provided_sanitized + "date") or param_sanitized.startswith(provided_sanitized + "time"):
                return True
            # Genel startswith kontrolü (ama period date ile eşleşmemeli)
            if param_sanitized.startswith(provided_sanitized) and not param_sanitized.startswith("perioddate"):
                return True
        
        # startdate/enddate -> start/end eşleştirmesi (ters yön)
        if param_sanitized in ["start", "end"]:
            if provided_sanitized.startswith(param_sanitized):
                return True
        
        # start_date/end_date -> effectiveDateStart/effectiveDateEnd eşleştirmesi
        # Ama periodDateStart/periodDateEnd ile eşleşmemeli
        if provided_sanitized == "start_date" and param_sanitized.startswith("effectivedatestart"):
            if not provided_sanitized.startswith("perioddate"):
                return True
        if provided_sanitized == "end_date" and param_sanitized.startswith("effectivedateend"):
            if not provided_sanitized.startswith("perioddate"):
                return True
        
        # payment date eşleştirmesi
        if provided_sanitized in ["start", "end"] and "payment" in param_sanitized and "date" in param_sanitized:
            return True
        
        return False

    def _check_date_keywords_match(self, provided: str, param: str) -> bool:
        """Tarih anahtar kelimelerini kontrol et"""
        date_keywords = ["date", "time", "period"]
        for keyword in date_keywords:
            if keyword in provided and keyword in param:
                return True
        return False

    def _check_abbreviation_match(self, provided: str, param: str) -> bool:
        return self._check_start_end_match(
            provided, param
        ) or self._check_date_keywords_match(provided, param)

    def _calculate_word_similarity(self, words1: List[str], words2: List[str]) -> float:
        if not words1 or not words2:
            return 0.0

        total_score = 0
        for word1 in words1:
            best_score = 0
            for word2 in words2:
                score = difflib.SequenceMatcher(None, word1, word2).ratio()
                best_score = max(best_score, score)
            total_score += best_score

        return total_score / len(words1)

    def _calculate_abbreviation_similarity(self, provided: str, param: str) -> float:
        # Zaten sanitize edilmiş değerler geliyor
        provided_sanitized = sanitize_param_name(provided)
        param_sanitized = sanitize_param_name(param)
        
        # Period date parametreleri için özel kontrol - effectiveDate ile eşleşmemeli
        if provided_sanitized.startswith("perioddate") and param_sanitized.startswith("effectivedate"):
            return 0.0
        
        # Period date parametreleri için exact match
        if provided_sanitized == "perioddatestart" and param_sanitized == "perioddatestart":
            return 1.0
        if provided_sanitized == "perioddateend" and param_sanitized == "perioddateend":
            return 1.0
        
        # start/end ile startDate/endDate eşleştirmesi için özel kurallar
        if provided_sanitized in ["start", "end"] and param_sanitized.startswith(provided_sanitized + "date"):
            # Period date ile eşleşmemeli
            if not param_sanitized.startswith("perioddate"):
                return 0.9
        if provided_sanitized in ["start", "end"] and param_sanitized.startswith(provided_sanitized + "time"):
            return 0.9

        # start_date/end_date ile effectiveDateStart/effectiveDateEnd eşleştirmesi
        # Ama periodDateStart/periodDateEnd ile eşleşmemeli
        if provided_sanitized == "start_date" and param_sanitized.startswith("effectivedatestart"):
            if not provided_sanitized.startswith("perioddate"):
                return 0.95
        if provided_sanitized == "end_date" and param_sanitized.startswith("effectivedateend"):
            if not provided_sanitized.startswith("perioddate"):
                return 0.95

        if len(provided_sanitized) < len(param_sanitized) and provided_sanitized in param_sanitized:
            # Period date kontrolü
            if provided_sanitized.startswith("perioddate") and param_sanitized.startswith("effectivedate"):
                return 0.0
            return 0.8

        if len(param_sanitized) < len(provided_sanitized) and param_sanitized in provided_sanitized:
            # Period date kontrolü
            if provided_sanitized.startswith("perioddate") and param_sanitized.startswith("effectivedate"):
                return 0.0
            return 0.8

        if provided_sanitized.startswith(param_sanitized[:3]) or param_sanitized.startswith(provided_sanitized[:3]):
            # Period date kontrolü
            if provided_sanitized.startswith("perioddate") and param_sanitized.startswith("effectivedate"):
                return 0.0
            return 0.6

        return 0.0

    def _convert_parameter_value(self, value: Any, param_name: str) -> Any:
        param_def = self._find_param_definition(param_name)
        if not param_def:
            return value

        if isinstance(value, str):
            return TypeConverter.convert_string_value(value, param_def.var_type)

        if self._is_correct_type(value, param_def.var_type):
            return value

        return value
    
    def _convert_nested_parameter_value(self, value: Any, nested_param: Any) -> Any:
        """Nested parametre için type conversion"""
        if not nested_param:
            return value
        
        if isinstance(value, str):
            return TypeConverter.convert_string_value(value, nested_param.var_type)
        
        if self._is_correct_type(value, nested_param.var_type):
            return value
        
        return value

    def _is_correct_type(self, value: Any, expected_type: str) -> bool:
        type_checks = {
            "datetime": lambda v: hasattr(v, "date"),
            "date": lambda v: hasattr(v, "date"),
            "int": lambda v: isinstance(v, int),
            "float": lambda v: isinstance(v, (int, float)),
            "bool": lambda v: isinstance(v, bool),
            "str": lambda v: isinstance(v, str),
            "string": lambda v: isinstance(v, str),
            "list": lambda v: isinstance(v, list),
            "array": lambda v: isinstance(v, list),
            "dict": lambda v: isinstance(v, dict),
            "object": lambda v: isinstance(v, dict),
        }

        check_func = type_checks.get(expected_type)
        return check_func(value) if check_func else False

    def _find_param_definition(self, param_name: str) -> Optional[Any]:
        for param in self.endpoint_params:
            if param.name == param_name:
                return param
        return None
    
    def _find_nested_param_definition(self, parent_param_name: str, nested_param_name: str) -> Optional[Any]:
        """Nested parametre tanımını bul (body.startDate gibi)"""
        parent_param = self._find_param_definition(parent_param_name)
        if not parent_param or not parent_param.properties:
            return None
        
        for prop in parent_param.properties:
            if prop.name == nested_param_name:
                return prop
        return None
    
    def _find_best_nested_param_match(
        self, provided_key: str, parent_param_name: str, used_nested_names: set = None
    ) -> Optional[str]:
        """Nested parametreler için en iyi eşleşmeyi bul"""
        if used_nested_names is None:
            used_nested_names = set()
        
        parent_param = self._find_param_definition(parent_param_name)
        if not parent_param or not parent_param.properties:
            return None
        
        best_match = None
        best_score = 0
        
        # Sanitize edilmiş provided_key
        sanitized_provided = sanitize_param_name(provided_key)
        
        # Önce exact match kontrolü (case-insensitive)
        for nested_param in parent_param.properties:
            if nested_param.name in used_nested_names:
                continue
            if provided_key.lower() == nested_param.name.lower():
                return nested_param.name
        
        # Period date parametreleri için özel kontrol
        period_date_patterns = {
            "perioddatestart": "periodDateStart",
            "perioddateend": "periodDateEnd",
            "period_date_start": "periodDateStart",
            "period_date_end": "periodDateEnd",
        }
        sanitized_lower = sanitized_provided.lower()
        if sanitized_lower in period_date_patterns:
            target_name = period_date_patterns[sanitized_lower]
            for nested_param in parent_param.properties:
                if nested_param.name in used_nested_names:
                    continue
                if nested_param.name == target_name:
                    return nested_param.name
        
        for nested_param in parent_param.properties:
            if nested_param.name in used_nested_names:
                continue
            
            if provided_key == nested_param.name:
                return nested_param.name
            
            # Sanitize edilmiş nested parametre ismi
            sanitized_nested = sanitize_param_name(nested_param.name)
            
            # Sanitize edilmiş isimlerle direkt eşleşme kontrolü
            if sanitized_provided == sanitized_nested:
                return nested_param.name
            
            # Period date parametreleri için özel kontrol
            if sanitized_provided in ["perioddatestart", "period_date_start"]:
                if sanitized_nested == "perioddatestart":
                    return nested_param.name
            if sanitized_provided in ["perioddateend", "period_date_end"]:
                if sanitized_nested == "perioddateend":
                    return nested_param.name
            
            # Özel eşleştirme kuralları (sanitize edilmiş isimlerle)
            # Period date parametreleri için effectiveDate ile eşleşmeyi engelle
            if sanitized_provided.startswith("perioddate") and sanitized_nested.startswith("effectivedate"):
                continue  # Bu eşleşmeyi atla
            
            if self._check_abbreviation_match(sanitized_provided, sanitized_nested):
                # Period date parametreleri için effectiveDate ile eşleşmeyi engelle
                if sanitized_provided.startswith("perioddate") and sanitized_nested.startswith("effectivedate"):
                    continue
                return nested_param.name
            
            scores = []
            
            scores.append(
                difflib.SequenceMatcher(
                    None, sanitized_provided, sanitized_nested
                ).ratio()
            )
            
            provided_words = sanitized_provided.replace("_", " ").split()
            param_words = sanitized_nested.replace("_", " ").split()
            word_score = self._calculate_word_similarity(provided_words, param_words)
            scores.append(word_score)
            
            abbrev_score = self._calculate_abbreviation_similarity(
                sanitized_provided, sanitized_nested
            )
            scores.append(abbrev_score)
            
            method_score = self._calculate_method_similarity(
                sanitized_provided, sanitized_nested
            )
            scores.append(method_score)
            
            score = max(scores)
            
            # Period date parametreleri için effectiveDate ile eşleşmeyi engelle
            if sanitized_provided.startswith("perioddate") and sanitized_nested.startswith("effectivedate"):
                score = 0  # Bu eşleşmeyi engelle
            
            if score > best_score and score > 0.3:
                best_match = nested_param.name
                best_score = score
        
        return best_match

    def _calculate_method_similarity(self, provided: str, param: str) -> float:
        method_keywords = self._get_method_keywords()
        provided_words = provided.replace("_", " ").split()
        param_words = param.replace("_", " ").split()

        total_score = 0
        matched_words = 0

        for provided_word in provided_words:
            best_score = self._calculate_word_method_score(
                provided_word, param_words, method_keywords
            )
            if best_score > 0.3:
                total_score += best_score
                matched_words += 1

        return total_score / len(provided_words) if matched_words > 0 else 0.0

    def _get_method_keywords(self) -> Dict[str, List[str]]:
        return {
            "list": ["list", "get", "fetch", "retrieve"],
            "hourly": ["hourly", "hour", "time"],
            "offer": ["offer", "bid", "proposal"],
            "create": ["create", "add", "new", "insert"],
            "update": ["update", "edit", "modify", "change"],
            "delete": ["delete", "remove", "drop", "destroy"],
            "count": ["count", "total", "number", "quantity"],
            "history": ["history", "log", "audit", "record"],
        }

    def _calculate_word_method_score(
        self,
        provided_word: str,
        param_words: List[str],
        method_keywords: Dict[str, List[str]],
    ) -> float:
        best_score = 0

        for param_word in param_words:
            direct_score = difflib.SequenceMatcher(
                None, provided_word, param_word
            ).ratio()
            best_score = max(best_score, direct_score)

        for category, keywords in method_keywords.items():
            if provided_word in keywords:
                for param_word in param_words:
                    if param_word in keywords:
                        best_score = max(best_score, 0.9)
                    else:
                        category_score = difflib.SequenceMatcher(
                            None, provided_word, category
                        ).ratio()
                        best_score = max(best_score, category_score * 0.8)

        return best_score
