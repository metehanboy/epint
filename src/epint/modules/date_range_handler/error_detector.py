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

import re
from typing import List, Optional


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


def extract_max_days_from_error(exception: Exception) -> Optional[int]:
    """
    Hata mesajından maksimum gün sayısını çıkar

    Args:
        exception: Exception objesi

    Returns:
        Maksimum gün sayısı veya None
    """
    error_text = None

    # Exception'ın tüm string temsillerini kontrol et
    exception_str = str(exception)
    exception_repr = repr(exception)
    exception_args_str = ' '.join(str(arg) for arg in exception.args) if exception.args else ''

    # Tüm string temsillerini birleştir
    all_text = f"{exception_str} {exception_repr} {exception_args_str}"
    error_text = all_text

    # Response attribute'dan kontrol et (fallback)
    if hasattr(exception, 'response'):
        response = exception.response
        if response:
            try:
                response_body = response.json()
                errors = response_body.get('errors', [])

                for error in errors:
                    error_message = error.get('errorMessage', '')
                    if error_message:
                        error_text = error_message
                        break
            except Exception:
                pass

    if not error_text:
        return None

    # Hata mesajından süreyi parse et
    # Formatlar: "(3 MONTH)", "(1 YEAR)", "(30 DAY)" gibi
    # Pattern: (sayı) (MONTH|YEAR|DAY|AY|YIL|GÜN)
    patterns = [
        r'\((\d+)\s*(MONTH|YEAR|DAY|AY|YIL|GÜN|MONTHS|YEARS|DAYS)\)',
        r'(\d+)\s*(MONTH|YEAR|DAY|AY|YIL|GÜN|MONTHS|YEARS|DAYS)',
        r'(\d+)\s*(ay|yıl|gün|month|year|day)',
    ]

    for pattern in patterns:
        match = re.search(pattern, error_text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            unit = match.group(2).upper()

            # Birimi gün sayısına çevir
            if unit in ['MONTH', 'MONTHS', 'AY']:
                # Ortalama ay 30 gün
                return value * 30
            elif unit in ['YEAR', 'YEARS', 'YIL']:
                # Yıl 365 gün
                return value * 365
            elif unit in ['DAY', 'DAYS', 'GÜN']:
                return value

    return None


__all__ = ['is_date_range_error', 'extract_max_days_from_error', 'DATE_RANGE_KEYWORDS']

