# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Any, Optional, Callable, List
from ..authentication.auth_manager import Authentication


class ErrorHandler:
    """HTTP ve API hatalarını yöneten modül"""

    def __init__(self, auth: Optional[Authentication] = None):
        """
        ErrorHandler oluştur

        Args:
            auth: Authentication instance (TGT/ST temizleme için)
        """
        self.auth = auth
        self._handlers: Dict[str, List[Callable]] = {}

    def register_handler(self, error_code: str, handler: Callable):
        """
        Özel hata handler'ı kaydet

        Args:
            error_code: Hata kodu (örn: 'AUTH009', '401', 'RATE_LIMIT')
            handler: Handler fonksiyonu (exception, response) -> None
        """
        if error_code not in self._handlers:
            self._handlers[error_code] = []
        self._handlers[error_code].append(handler)

    def handle_exception(self, exception: Exception, response: Optional[Any] = None) -> None:
        """
        Exception'ı işle ve gerekli aksiyonları al

        Args:
            exception: Yakalanan exception
            response: HTTP response objesi (varsa)
        """
        if not response and hasattr(exception, 'response'):
            response = exception.response

        if not response:
            return

        status_code = getattr(response, 'status_code', None)
        if not status_code:
            return

        # Status code bazlı handler'lar
        if status_code == 401:
            self._handle_401(response)
        elif status_code == 403:
            self._handle_403(response)
        elif status_code == 404:
            self._handle_404(response)
        elif status_code == 429:
            self._handle_429(response)
        elif status_code >= 500:
            self._handle_5xx(response)

        # Response body'den hata kodlarını al ve işle
        try:
            response_body = response.json()
            errors = response_body.get('errors', [])
            for error in errors:
                error_code = error.get('errorCode', '')
                error_message = error.get('errorMessage', '')

                # Özel handler'ları çağır
                if error_code in self._handlers:
                    for handler in self._handlers[error_code]:
                        handler(exception, response, error)

                # Varsayılan handler'lar
                self._handle_error_code(error_code, error_message, response)
        except:
            pass

    def _handle_401(self, response: Any) -> None:
        """401 Unauthorized hatası"""
        try:
            response_body = response.json()
            errors = response_body.get('errors', [])

            for error in errors:
                error_code = error.get('errorCode', '')
                error_message = str(error.get('errorMessage', '')).upper()

                # TGT hatası
                if error_code == 'AUTH009' or 'TGT' in error_message:
                    if self.auth:
                        self.auth.clear_tickets()

                # ST hatası
                elif error_code == 'AUTH010' or 'ST' in error_message:
                    if self.auth:
                        self.auth.clear_tickets()
        except:
            pass

    def _handle_403(self, response: Any) -> None:
        """403 Forbidden hatası"""
        pass

    def _handle_404(self, response: Any) -> None:
        """404 Not Found hatası"""
        try:
            # Response body'yi text olarak al
            response_text = response.text if hasattr(response, 'text') else str(response.content or '')
            response_text_lower = response_text.lower()

            # TGT geçersizliğini belirten anahtar kelimeler
            tgt_invalid_keywords = [
                'could not be found',
                'is considered invalid',
                'invalid',
                'not found',
                'geçersiz',
                'bulunamadı'
            ]

            # TGT ile ilgili bir mesaj var mı kontrol et
            has_tgt_reference = 'tgt-' in response_text_lower or 'ticket' in response_text_lower

            # TGT geçersizliği belirtiliyor mu kontrol et
            is_tgt_invalid = any(keyword in response_text_lower for keyword in tgt_invalid_keywords)

            # Eğer TGT referansı var ve geçersizlik belirtiliyorsa ticket'ları temizle
            if has_tgt_reference and is_tgt_invalid:
                if self.auth:
                    self.auth.clear_tickets()
        except:
            pass

    def _handle_429(self, response: Any) -> None:
        """429 Rate Limit hatası"""
        pass

    def _handle_5xx(self, response: Any) -> None:
        """5xx Server Error hatası"""
        pass

    def _handle_error_code(self, error_code: str, error_message: str, response: Any) -> None:
        """
        Hata koduna göre işlem yap

        Args:
            error_code: Hata kodu
            error_message: Hata mesajı
            response: HTTP response
        """
        # AUTH hataları
        if error_code.startswith('AUTH'):
            if self.auth:
                if error_code in ('AUTH009', 'AUTH010'):
                    self.auth.clear_tickets()

        # Rate limit hataları
        elif error_code.startswith('RATE'):
            pass

        # Validation hataları
        elif error_code.startswith('VALID'):
            pass

