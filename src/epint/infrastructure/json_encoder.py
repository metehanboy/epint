# -*- coding: utf-8 -*-

"""
Custom JSON Encoder/Decoder for epint
Python'ın date, datetime, Decimal gibi sınıflarını JSON'a serialize edebilmek için
custom encoder/decoder sınıfları
"""

import json
import datetime
from decimal import Decimal
from typing import Any, Dict, List, Union
from .logger import get_logger
from .datetime_utils import DateTimeUtils

logger = get_logger()


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder - Python objelerini JSON'a serialize eder"""
    
    def default(self, obj: Any) -> Any:
        """Python objelerini JSON serializable hale getirir"""
        try:
            # Date objesi
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            
            # DateTime objesi - DateTimeUtils kullan
            if isinstance(obj, datetime.datetime):
                # DateTimeUtils.to_iso_string() ile serialize et
                return DateTimeUtils.to_iso_string(obj)
            
            # Time objesi
            if isinstance(obj, datetime.time):
                return obj.isoformat()
            
            # Decimal objesi
            if isinstance(obj, Decimal):
                return float(obj)
            
            # Set objesi
            if isinstance(obj, set):
                return list(obj)
            
            # Tuple objesi
            if isinstance(obj, tuple):
                return list(obj)
            
            # Bytes objesi
            if isinstance(obj, bytes):
                return obj.decode('utf-8')
            
            # Enum objesi
            if hasattr(obj, 'value'):
                return obj.value
            
            # Callable objesi
            if callable(obj):
                return str(obj)
            
            # Diğer objeler için str() kullan
            return str(obj)
            
        except Exception as e:
            logger.log_error(
                "json_encoding_error",
                error_msg=f"JSON encoding error for object {type(obj)}: {str(e)}"
            )
            return str(obj)


class CustomJSONDecoder(json.JSONDecoder):
    """Custom JSON Decoder - JSON'dan Python objelerine deserialize eder"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """JSON objelerini Python objelerine dönüştürür"""
        try:
            # ISO format tarihleri datetime'a dönüştür - DateTimeUtils kullan
            for key, value in obj.items():
                if isinstance(value, str):
                    # ISO date format (YYYY-MM-DD)
                    if len(value) == 10 and value.count('-') == 2:
                        try:
                            obj[key] = DateTimeUtils.from_date_string(value)
                        except ValueError:
                            pass
                    
                    # ISO datetime format (YYYY-MM-DDTHH:MM:SS)
                    elif 'T' in value or 'Z' in value or len(value) >= 19:
                        try:
                            # DateTimeUtils.from_string() ile parse et
                            obj[key] = DateTimeUtils.from_string(value)
                        except ValueError:
                            pass
            
            return obj
            
        except Exception as e:
            logger.log_error(
                "json_decoding_error",
                error_msg=f"JSON decoding error: {str(e)}"
            )
            return obj


class JSONUtils:
    """JSON işlemleri için utility sınıfı"""
    
    @staticmethod
    def dumps(obj: Any, **kwargs) -> str:
        """Python objesini JSON string'e dönüştürür"""
        try:
            # Custom encoder kullan
            return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)
        except Exception as e:
            logger.log_error(
                "json_dumps_error",
                error_msg=f"JSON dumps error: {str(e)}"
            )
            raise
    
    @staticmethod
    def loads(json_str: str, **kwargs) -> Any:
        """JSON string'i Python objesine dönüştürür"""
        try:
            # Custom decoder kullan
            return json.loads(json_str, cls=CustomJSONDecoder, **kwargs)
        except Exception as e:
            logger.log_error(
                "json_loads_error",
                error_msg=f"JSON loads error: {str(e)}"
            )
            raise
    
    @staticmethod
    def dump(obj: Any, fp, **kwargs) -> None:
        """Python objesini JSON file'a yazar"""
        try:
            json.dump(obj, fp, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)
        except Exception as e:
            logger.log_error(
                "json_dump_error",
                error_msg=f"JSON dump error: {str(e)}"
            )
            raise
    
    @staticmethod
    def load(fp, **kwargs) -> Any:
        """JSON file'dan Python objesi okur"""
        try:
            return json.load(fp, cls=CustomJSONDecoder, **kwargs)
        except Exception as e:
            logger.log_error(
                "json_load_error",
                error_msg=f"JSON load error: {str(e)}"
            )
            raise
    
    @staticmethod
    def is_json_serializable(obj: Any) -> bool:
        """Objenin JSON serializable olup olmadığını kontrol eder"""
        try:
            json.dumps(obj, cls=CustomJSONEncoder)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def make_serializable(obj: Any) -> Any:
        """Objeyi JSON serializable hale getirir (recursive)"""
        try:
            if isinstance(obj, dict):
                return {key: JSONUtils.make_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [JSONUtils.make_serializable(item) for item in obj]
            elif isinstance(obj, datetime.datetime):
                # DateTimeUtils.to_iso_string() kullan
                return DateTimeUtils.to_iso_string(obj)
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            elif isinstance(obj, datetime.time):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, bytes):
                return obj.decode('utf-8')
            elif hasattr(obj, 'value'):  # Enum
                return obj.value
            else:
                # Önce JSON'a dönüştür, sonra geri al
                json_str = json.dumps(obj, cls=CustomJSONEncoder)
                return json.loads(json_str)
        except Exception as e:
            logger.log_error(
                "make_serializable_error",
                error_msg=f"Make serializable error: {str(e)}"
            )
            return str(obj)


# Global instance
json_utils = JSONUtils()

# Convenience functions
def json_dumps(obj: Any, **kwargs) -> str:
    """Python objesini JSON string'e dönüştürür"""
    return json_utils.dumps(obj, **kwargs)


def json_loads(json_str: str, **kwargs) -> Any:
    """JSON string'i Python objesine dönüştürür"""
    return json_utils.loads(json_str, **kwargs)


def json_dump(obj: Any, fp, **kwargs) -> None:
    """Python objesini JSON file'a yazar"""
    json_utils.dump(obj, fp, **kwargs)


def json_load(fp, **kwargs) -> Any:
    """JSON file'dan Python objesi okur"""
    return json_utils.load(fp, **kwargs)

