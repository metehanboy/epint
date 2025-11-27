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

    @staticmethod
    def parse_response(response_data: Any, response_structure: Any) -> Any:
        """Response'u response_structure'a göre parse eder ve type conversion yapar"""
        if response_structure is None:
            return response_data
        
        if response_data is None:
            return None
        
        if isinstance(response_structure, dict):
            # Dict yapısı - her key için parse et
            parsed = {}
            
            # Önce response_data'da olan key'leri parse et
            for key, structure in response_structure.items():
                if key in response_data:
                    parsed[key] = TypeConverter.parse_response(response_data[key], structure)
                # Key yoksa None ekleme - sadece response_data'da olan key'leri işle
            
            # response_data'da olup response_structure'da olmayan key'leri de ekle
            if isinstance(response_data, dict):
                for key in response_data:
                    if key not in parsed:
                        # response_structure'da tanımlı değilse direkt ekle
                        parsed[key] = response_data[key]
            
            # Eğer parsed boşsa ama response_data varsa, response_data'yı direkt döndür
            if not parsed and response_data:
                return response_data
            
            return parsed if parsed else response_data
        elif isinstance(response_structure, list):
            # List yapısı - YAML'da list item'ları şu şekilde: [- item1, item2]
            if len(response_structure) > 0:
                item_structure = response_structure[0]
                if isinstance(response_data, list):
                    return [TypeConverter.parse_response(item, item_structure) for item in response_data]
                else:
                    return response_data
            return response_data
        else:
            # Type tanımı (str, int, float, datetime, vb.)
            if isinstance(response_structure, str):
                target_type = response_structure.lower()
                
                # String değerleri convert et
                if isinstance(response_data, str):
                    if target_type in ["int", "float", "datetime", "date", "bool"]:
                        return TypeConverter.convert_string_value(response_data, target_type)
                    return response_data
                # Zaten doğru type ise direkt döndür
                elif target_type == "int" and isinstance(response_data, (int, float)):
                    return int(response_data)
                elif target_type == "float" and isinstance(response_data, (int, float)):
                    return float(response_data)
                elif target_type == "datetime" and isinstance(response_data, _dt.datetime):
                    return response_data
                elif target_type == "bool" and isinstance(response_data, bool):
                    return response_data
            
            return response_data
