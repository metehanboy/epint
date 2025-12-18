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

"""Error detection utilities for date range errors"""

from typing import List


# Tarih aralığı hatası için anahtar kelimeler
DATE_RANGE_KEYWORDS = [
    'sef1117',
    'tanımlanmış aralık',
    'fazla olamaz',
    'aralıktan fazla',
    '1 year',
    'year',
    'tarih aralığı',
    'date range',
    'maximum range',
    'maksimum aralık'
]


def is_date_range_error(exception: Exception) -> bool:
    """
    Tarih aralığı hatası olup olmadığını kontrol et
    
    Args:
        exception: Kontrol edilecek exception
    
    Returns:
        True eğer tarih aralığı hatası ise, False değilse
    """
    # Exception'ın tüm string temsillerini kontrol et
    exception_str = str(exception)
    exception_repr = repr(exception)
    exception_args_str = ' '.join(str(arg) for arg in exception.args) if exception.args else ''
    
    # Tüm string temsillerini birleştir ve kontrol et
    all_text = f"{exception_str} {exception_repr} {exception_args_str}".lower()
    
    # Exception mesajında hata kodunu ara
    for keyword in DATE_RANGE_KEYWORDS:
        if keyword in all_text:
            return True
    
    # Response attribute'dan kontrol et (fallback)
    if hasattr(exception, 'response'):
        response = exception.response
        if response:
            try:
                response_body = response.json()
                errors = response_body.get('errors', [])
                
                for error in errors:
                    error_code = error.get('errorCode', '')
                    error_message = error.get('errorMessage', '')
                    
                    # Tarih aralığı hata kodları ve mesajları
                    error_text = f"{error_code} {error_message}".lower()
                    for keyword in DATE_RANGE_KEYWORDS:
                        if keyword in error_text:
                            return True
            except Exception:
                pass
    
    return False


__all__ = ['is_date_range_error', 'DATE_RANGE_KEYWORDS']

