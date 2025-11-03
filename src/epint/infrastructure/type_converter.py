# -*- coding: utf-8 -*-

from typing import Any
import datetime as _dt
from .datetime_utils import DateTimeUtils


class TypeConverter:

    @staticmethod
    def convert_string_value(value: str, target_type: str) -> Any:
        if target_type == "datetime":
            return DateTimeUtils.from_string(value)
        elif target_type == "date":
            return DateTimeUtils.from_date_string(value)
        elif target_type == "int":
            return TypeConverter._safe_int_convert(value)
        elif target_type == "float":
            return TypeConverter._safe_float_convert(value)
        elif target_type == "bool":
            return value.lower() in ["true", "1", "yes", "on"]
        return value

    @staticmethod
    def serialize_for_post(value: Any) -> Any:
        if isinstance(value, _dt.datetime):
            return DateTimeUtils.to_iso_string(value)
        elif isinstance(value, _dt.date):
            return value.isoformat()
        elif isinstance(value, bool):
            return str(value).lower()
        return value

    @staticmethod
    def serialize_for_get(value: Any) -> Any:
        if isinstance(value, _dt.datetime):
            return DateTimeUtils.to_iso_string(value)
        elif isinstance(value, _dt.date):
            return value.isoformat()
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (list, dict)):
            return str(value)
        return value

    @staticmethod
    def serialize_for_gunici(value: Any) -> Any:
        """Gunici servisleri için tarih formatı: 2021-06-24 14:00:00"""
        if isinstance(value, _dt.datetime):
            return value.strftime(DateTimeUtils.DATETIME_FORMAT)
        elif isinstance(value, _dt.date):
            return value.strftime(DateTimeUtils.DATE_FORMAT)
        elif isinstance(value, bool):
            return str(value).lower()
        return value

    @staticmethod
    def serialize_for_gop(value: Any) -> Any:
        if isinstance(value, _dt.datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + value.strftime("%z")
        elif isinstance(value, _dt.date):
            return value.strftime("%Y-%m-%dT00:00:00.000+0300")
        elif isinstance(value, bool):
            return str(value).lower()
        return value

    @staticmethod
    def _safe_int_convert(value: str) -> Any:
        try:
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def _safe_float_convert(value: str) -> Any:
        try:
            return float(value)
        except ValueError:
            return value
