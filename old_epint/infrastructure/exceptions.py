# -*- coding: utf-8 -*-

"""
EPINT API Exception sınıfları
"""

from typing import List, Dict, Any, Optional


class EPINTException(Exception):
    """EPINT base exception"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 correlation_id: Optional[str] = None, 
                 additional_errors: Optional[List[str]] = None):
        self.error_code = error_code
        self.correlation_id = correlation_id
        self.additional_errors = additional_errors or []
        super().__init__(message)


class APIValidationError(EPINTException):
    """API validation hatası (400) - İstek parametreleri hatalı"""
    pass


class APIBusinessRuleError(EPINTException):
    """API iş kuralı hatası (400) - İş kurallarına uymayan istek"""
    pass


class APIAuthenticationError(EPINTException):
    """API kimlik doğrulama hatası (401)"""
    pass


class APIAuthorizationError(EPINTException):
    """API yetkilendirme hatası (403)"""
    pass


class APINotFoundError(EPINTException):
    """API endpoint bulunamadı hatası (404)"""
    pass


class APIServerError(EPINTException):
    """API sunucu hatası (500+)"""
    pass


class DateRangeError(APIBusinessRuleError):
    """Tarih aralığı hatası - Özel iş kuralı hatası"""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 correlation_id: Optional[str] = None,
                 max_range: Optional[str] = None,
                 provided_range: Optional[str] = None,
                 additional_errors: Optional[List[str]] = None):
        self.max_range = max_range
        self.provided_range = provided_range
        super().__init__(message, error_code, correlation_id, additional_errors)


def parse_api_error(error_data: Dict[str, Any]) -> EPINTException:
    """
    API error response'undan uygun exception oluşturur
    
    Args:
        error_data: API'den gelen error response dict
        
    Returns:
        EPINTException: Uygun exception sınıfı
    """
    status = error_data.get("status", "Unknown")
    correlation_id = error_data.get("correlationId", "N/A")
    errors = error_data.get("errors", [])
    
    if not errors:
        return EPINTException(
            f"API Hatası: {status}",
            correlation_id=correlation_id
        )
    
    # İlk hatayı ana hata olarak al
    main_error = errors[0] if isinstance(errors[0], dict) else {}
    error_code = main_error.get("errorCode", "Unknown")
    error_message = main_error.get("errorMessage", "Unknown error")
    
    # Ek hataları topla
    additional_errors = []
    for error in errors[1:]:
        if isinstance(error, dict):
            additional_errors.append(
                f"[{error.get('errorCode', 'Unknown')}] {error.get('errorMessage', 'Unknown error')}"
            )
    
    # Hata koduna göre özel exception oluştur
    if error_code.startswith("(BUS)"):
        # İş kuralı hatası
        # Tarih aralığı hatası kontrolü
        if "tarih" in error_message.lower() and "aralık" in error_message.lower():
            # Tarih aralığı hatası - max range'i parse et
            max_range = None
            if "1 YEAR" in error_message:
                max_range = "1 YEAR"
            elif "1 MONTH" in error_message:
                max_range = "1 MONTH"
            elif "1 WEEK" in error_message:
                max_range = "1 WEEK"
            elif "1 DAY" in error_message:
                max_range = "1 DAY"
            
            return DateRangeError(
                f"Tarih aralığı hatası: {error_message}",
                error_code=error_code,
                correlation_id=correlation_id,
                max_range=max_range,
                additional_errors=additional_errors
            )
        
        return APIBusinessRuleError(
            f"İş kuralı hatası: {error_message}",
            error_code=error_code,
            correlation_id=correlation_id,
            additional_errors=additional_errors
        )
    elif error_code.startswith("(VAL)"):
        # Validation hatası
        return APIValidationError(
            f"Parametre doğrulama hatası: {error_message}",
            error_code=error_code,
            correlation_id=correlation_id,
            additional_errors=additional_errors
        )
    else:
        # Genel iş kuralı hatası
        return APIBusinessRuleError(
            f"API Hatası: [{error_code}] {error_message}",
            error_code=error_code,
            correlation_id=correlation_id,
            additional_errors=additional_errors
        )


def create_exception_from_status_code(
    status_code: int, 
    error_data: Optional[Dict[str, Any]] = None,
    error_text: Optional[str] = None
) -> EPINTException:
    """
    HTTP status code'a göre uygun exception oluşturur
    
    Args:
        status_code: HTTP status code
        error_data: API error response dict (opsiyonel)
        error_text: Hata mesajı (opsiyonel)
        
    Returns:
        EPINTException: Uygun exception sınıfı
    """
    if error_data:
        exception = parse_api_error(error_data)
        return exception
    
    # Error data yoksa status code'a göre oluştur
    if status_code == 400:
        return APIValidationError(
            error_text or "Geçersiz istek parametreleri",
            correlation_id="N/A"
        )
    elif status_code == 401:
        return APIAuthenticationError(
            error_text or "Kimlik doğrulama hatası",
            correlation_id="N/A"
        )
    elif status_code == 403:
        return APIAuthorizationError(
            error_text or "Erişim reddedildi",
            correlation_id="N/A"
        )
    elif status_code == 404:
        return APINotFoundError(
            error_text or "Endpoint bulunamadı",
            correlation_id="N/A"
        )
    elif status_code >= 500:
        return APIServerError(
            error_text or "Sunucu hatası",
            correlation_id="N/A"
        )
    else:
        return EPINTException(
            error_text or f"Bilinmeyen hata (HTTP {status_code})",
            correlation_id="N/A"
        )

