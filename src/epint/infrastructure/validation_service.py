# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Dict, Any, List
from .endpoint_models import EndpointInfo, ValidationResult
from .parameter_matcher import ParameterMatcher
from .parameter_validator import ParameterValidator


class ValidationService:

    def __init__(self, endpoint_info: EndpointInfo):
        self.endpoint_info = endpoint_info
        self.parameter_matcher = ParameterMatcher(endpoint_info.var_type, endpoint_info.category)

    def validate_endpoint_call(self, **kwargs) -> ValidationResult:
        errors = []
        warnings = []

        matched_params, unmatched_params = self._fuzzy_match_params(kwargs)

        if unmatched_params:
            warnings.append(f"Eşleşmeyen parametreler: {list(unmatched_params.keys())}")

        validated_params = self._validate_all_parameters(matched_params, errors)

        self._check_extra_parameters(matched_params, warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_params=validated_params,
            endpoint_info=self.endpoint_info,
        )

    def _fuzzy_match_params(self, provided_params: Dict[str, Any]):
        return self.parameter_matcher.fuzzy_match_params(provided_params)

    def _validate_all_parameters(
        self, matched_params: Dict[str, Any], errors: List[str]
    ) -> Dict[str, Any]:
        validated_params = {}
        for param in self.endpoint_info.var_type:
            if param.name in matched_params:
                value = matched_params[param.name]
                
                # Object/dict tipi ise nested parametreleri de validate et
                if param.var_type in ["object", "dict"] and isinstance(value, dict) and param.properties:
                    # GOP için özel kontrol: body içinde body varsa, içteki body'yi validate et
                    if self.endpoint_info.category == "gop" and param.name == "body" and "body" in value:
                        # Body içindeki body'yi validate et
                        body_data = value["body"]
                        validated_nested = {}
                        for nested_param in param.properties:
                            if nested_param.name in body_data:
                                nested_value = body_data[nested_param.name]
                                is_valid, error_msg = ParameterValidator.validate_parameter_type(
                                    nested_param.name, nested_value, nested_param.var_type
                                )
                                if is_valid:
                                    validated_nested[nested_param.name] = nested_value
                                else:
                                    errors.append(error_msg)
                            elif nested_param.required:
                                errors.append(f"Zorunlu parametre '{param.name}.{nested_param.name}' eksik")
                        
                        # Validated nested parametreleri body içine wrap et
                        if validated_nested:
                            validated_params[param.name] = {"body": validated_nested}
                    else:
                        # Normal nested parametreleri validate et
                        validated_nested = {}
                        for nested_param in param.properties:
                            if nested_param.name in value:
                                nested_value = value[nested_param.name]
                                is_valid, error_msg = ParameterValidator.validate_parameter_type(
                                    nested_param.name, nested_value, nested_param.var_type
                                )
                                if is_valid:
                                    validated_nested[nested_param.name] = nested_value
                                else:
                                    errors.append(error_msg)
                            elif nested_param.required:
                                errors.append(f"Zorunlu parametre '{param.name}.{nested_param.name}' eksik")
                        
                        # Validated nested parametreleri ekle
                        if validated_nested:
                            validated_params[param.name] = validated_nested
                else:
                    # Normal parametre validation
                    is_valid, error_msg = ParameterValidator.validate_parameter_type(
                        param.name, value, param.var_type
                    )

                    if is_valid:
                        validated_params[param.name] = value
                    else:
                        errors.append(error_msg)
            elif param.required:
                # Required parametre eksik - ama object tipi ise nested kontrolü yap
                if param.var_type in ["object", "dict"] and param.properties:
                    # Nested required parametreleri kontrol et
                    for nested_param in param.properties:
                        if nested_param.required:
                            errors.append(f"Zorunlu parametre '{param.name}.{nested_param.name}' eksik")
                else:
                    errors.append(f"Zorunlu parametre '{param.name}' eksik")
        return validated_params

    def _check_extra_parameters(
        self, matched_params: Dict[str, Any], warnings: List[str]
    ):
        for param_name in matched_params:
            if param_name not in [p.name for p in self.endpoint_info.var_type]:
                warnings.append(f"Beklenmeyen parametre: {param_name}")
