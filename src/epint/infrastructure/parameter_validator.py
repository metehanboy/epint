# -*- coding: utf-8 -*-

from typing import Any, Tuple
import datetime as _dt
from .datetime_utils import DateTimeUtils


class ParameterValidator:

    @staticmethod
    def validate_parameter_type(
        param_name: str, value: Any, expected_type: str
    ) -> Tuple[bool, str]:
        try:
            type_validators = {
                "str": ParameterValidator._validate_string_type,
                "int": ParameterValidator._validate_int_type,
                "float": ParameterValidator._validate_float_type,
                "bool": ParameterValidator._validate_bool_type,
                "list": ParameterValidator._validate_list_type,
                "array": ParameterValidator._validate_list_type,
                "dict": ParameterValidator._validate_dict_type,
                "object": ParameterValidator._validate_dict_type,
                "date": ParameterValidator._validate_date_type,
                "datetime": ParameterValidator._validate_datetime_type,
            }

            validator = type_validators.get(expected_type)
            if validator:
                return validator(param_name, value)
            else:
                return True, ""

        except Exception as e:
            return False, f"'{param_name}' doğrulama hatası: {e}"

    @staticmethod
    def _validate_string_type(param_name: str, value: Any) -> Tuple[bool, str]:
        if isinstance(value, str):
            return True, ""
        else:
            return False, f"'{param_name}' string olmalı"

    @staticmethod
    def _validate_int_type(param_name: str, value: Any) -> Tuple[bool, str]:
        if isinstance(value, int):
            return True, ""
        elif isinstance(value, str) and value.isdigit():
            return True, ""
        else:
            return False, f"'{param_name}' integer olmalı"

    @staticmethod
    def _validate_float_type(param_name: str, value: Any) -> Tuple[bool, str]:
        if isinstance(value, (int, float)):
            return True, ""
        elif isinstance(value, str) and ParameterValidator._is_float(value):
            return True, ""
        else:
            return False, f"'{param_name}' float olmalı"

    @staticmethod
    def _validate_bool_type(param_name: str, value: Any) -> Tuple[bool, str]:
        if isinstance(value, bool):
            return True, ""
        elif isinstance(value, str) and value.lower() in ["true", "false"]:
            return True, ""
        else:
            return False, f"'{param_name}' boolean olmalı"

    @staticmethod
    def _validate_list_type(param_name: str, value: Any) -> Tuple[bool, str]:
        return isinstance(value, list), f"'{param_name}' list olmalı"

    @staticmethod
    def _validate_dict_type(param_name: str, value: Any) -> Tuple[bool, str]:
        return isinstance(value, dict), f"'{param_name}' dict olmalı"

    @staticmethod
    def _validate_date_type(param_name: str, value: Any) -> Tuple[bool, str]:
        if isinstance(value, _dt.date):
            return True, ""
        elif isinstance(value, str):
            try:
                DateTimeUtils.from_date_string(value)
                return True, ""
            except Exception:
                return False, f"'{param_name}' date formatında olmalı (YYYY-MM-DD)"
        return False, f"'{param_name}' date formatında olmalı"

    @staticmethod
    def _validate_datetime_type(param_name: str, value: Any) -> Tuple[bool, str]:
        if isinstance(value, _dt.datetime):
            return True, ""
        elif isinstance(value, str):
            try:
                DateTimeUtils.from_string(value)
                return True, ""
            except Exception:
                return False, f"'{param_name}' datetime formatında olmalı (ISO 8601)"
        return False, f"'{param_name}' datetime formatında olmalı"

    @staticmethod
    def _is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
