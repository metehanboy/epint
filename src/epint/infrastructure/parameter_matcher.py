# -*- coding: utf-8 -*-

import difflib
from typing import Any, Dict, List, Optional, Tuple
from .type_converter import TypeConverter


class ParameterMatcher:
    def __init__(self, endpoint_params: List[Any]):
        self.endpoint_params = endpoint_params

    def fuzzy_match_params(
        self, provided_params: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        matched_params = {}
        unmatched_params = {}
        used_param_names = set()

        for provided_key, provided_value in provided_params.items():
            best_match = self._find_best_param_match(provided_key, used_param_names)

            if best_match and best_match not in used_param_names:
                converted_value = self._convert_parameter_value(
                    provided_value, best_match
                )
                matched_params[best_match] = converted_value
                used_param_names.add(best_match)
            else:
                unmatched_params[provided_key] = provided_value

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
                # Özel eşleştirmeler
                if "region" in param_name:
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

        for param in self.endpoint_params:
            # Skip already used parameters
            if param.name in used_param_names:
                continue

            if provided_key == param.name:
                return param.name

            # Özel eşleştirme kuralları
            if self._check_abbreviation_match(provided_key.lower(), param.name.lower()):
                return param.name

            scores = []

            scores.append(
                difflib.SequenceMatcher(
                    None, provided_key.lower(), param.name.lower()
                ).ratio()
            )

            provided_words = provided_key.lower().replace("_", " ").split()
            param_words = param.name.lower().replace("_", " ").split()
            word_score = self._calculate_word_similarity(provided_words, param_words)
            scores.append(word_score)

            abbrev_score = self._calculate_abbreviation_similarity(
                provided_key.lower(), param.name.lower()
            )
            scores.append(abbrev_score)

            method_score = self._calculate_method_similarity(
                provided_key.lower(), param.name.lower()
            )
            scores.append(method_score)

            score = max(scores)

            if score > best_score and score > 0.3:
                best_match = param.name
                best_score = score

        return best_match

    def _check_start_end_match(self, provided: str, param: str) -> bool:
        """start/end ile ilgili eşleştirmeleri kontrol et"""
        if provided in ["start", "end"] and param.startswith(provided):
            return True
        if param in ["start", "end"] and provided.startswith(param):
            return True
        if provided in ["start", "end"] and param.startswith(provided + "Date"):
            return True
        if provided in ["start", "end"] and param.startswith(provided + "Time"):
            return True
        if provided in ["start", "end"] and "payment" in param and "date" in param:
            return True
        # start_date/end_date -> effectiveDateStart/effectiveDateEnd eşleştirmesi
        if provided == "start_date" and param.lower().startswith("effectivedatestart"):
            return True
        if provided == "end_date" and param.lower().startswith("effectivedateend"):
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
        # start/end ile startDate/endDate eşleştirmesi için özel kurallar
        if provided in ["start", "end"] and param.startswith(provided + "Date"):
            return 0.9
        if provided in ["start", "end"] and param.startswith(provided + "Time"):
            return 0.9

        # start_date/end_date ile effectiveDateStart/effectiveDateEnd eşleştirmesi
        if provided == "start_date" and param.lower().startswith("effectivedatestart"):
            return 0.95
        if provided == "end_date" and param.lower().startswith("effectivedateend"):
            return 0.95

        if len(provided) < len(param) and provided in param.lower():
            return 0.8

        if len(param) < len(provided) and param in provided.lower():
            return 0.8

        if provided.startswith(param[:3]) or param.startswith(provided[:3]):
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
