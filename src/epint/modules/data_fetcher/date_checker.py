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

"""Date parameter checking and parsing utilities"""

import datetime
from typing import Dict, Any, Optional

from ..datetime import DateTimeUtils


# Tarih parametre isimleri
DATE_PARAM_NAMES = [
    'startDate', 'endDate', 'start', 'end',
    'startDateTime', 'endDateTime',
    'baslangicTarihi', 'bitisTarihi',
    'baslangic', 'bitis'
]


def has_date_params(kwargs: Dict[str, Any], request_model: Any) -> bool:
    """
    Tarih parametreleri var mı kontrol et

    Args:
        kwargs: Endpoint çağrısı kwargs'ları
        request_model: Request model objesi

    Returns:
        Tarih parametreleri varsa True
    """
    return extract_date_params(kwargs, request_model) is not None


def extract_date_params(kwargs: Dict[str, Any], request_model: Any) -> Optional[Dict[str, Any]]:
    """
    Tarih parametrelerini çıkar

    Args:
        kwargs: Endpoint çağrısı kwargs'ları
        request_model: Request model objesi

    Returns:
        Tarih parametreleri dict'i veya None
    """
    date_params = {}

    # kwargs'tan tarih parametrelerini bul
    for param_name in DATE_PARAM_NAMES:
        if param_name in kwargs:
            date_params[param_name] = kwargs[param_name]

    # request_model.json'dan tarih parametrelerini bul
    if hasattr(request_model, 'json') and request_model.json:
        for param_name in DATE_PARAM_NAMES:
            if param_name in request_model.json:
                date_params[param_name] = request_model.json[param_name]

    # request_model.params'tan tarih parametrelerini bul
    if hasattr(request_model, 'params') and request_model.params:
        for param_name in DATE_PARAM_NAMES:
            if param_name in request_model.params:
                date_params[param_name] = request_model.params[param_name]

    if len(date_params) < 2:
        return None

    # Start ve end parametrelerini belirle
    start_param = None
    end_param = None

    # Öncelik sırasına göre kontrol et
    for start_name in ['startDate', 'start', 'startDateTime', 'baslangicTarihi', 'baslangic']:
        if start_name in date_params:
            start_param = start_name
            break

    for end_name in ['endDate', 'end', 'endDateTime', 'bitisTarihi', 'bitis']:
        if end_name in date_params:
            end_param = end_name
            break

    if not start_param or not end_param:
        return None

    return {
        'start_param': start_param,
        'end_param': end_param,
        'start_value': date_params[start_param],
        'end_value': date_params[end_param]
    }


def parse_date_value(value: Any) -> Optional[datetime.datetime]:
    """
    Tarih değerini parse et

    Args:
        value: Parse edilecek değer (str, datetime, date)

    Returns:
        datetime.datetime objesi veya None
    """
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=DateTimeUtils.DEFAULT_TIMEZONE)
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(
            value,
            datetime.time.min
        ).replace(tzinfo=DateTimeUtils.DEFAULT_TIMEZONE)
    if isinstance(value, str):
        try:
            dt = DateTimeUtils.from_string(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=DateTimeUtils.DEFAULT_TIMEZONE)
            return dt
        except:
            try:
                date_val = DateTimeUtils.from_date_string(value)
                return datetime.datetime.combine(
                    date_val,
                    datetime.time.min
                ).replace(tzinfo=DateTimeUtils.DEFAULT_TIMEZONE)
            except:
                return None
    return None


def format_date_value(dt: datetime.datetime, original_value: Any) -> Any:
    """
    Orijinal format'a göre tarih değerini formatla

    Args:
        dt: Formatlanacak datetime objesi
        original_value: Orijinal değer (format belirlemek için)

    Returns:
        Formatlanmış tarih değeri
    """
    if isinstance(original_value, str):
        if 'T' in original_value or len(original_value) > 10:
            # datetime formatı
            return DateTimeUtils.to_iso_string(dt)
        else:
            # date formatı
            return dt.strftime('%Y-%m-%d')
    else:
        return dt


__all__ = ['has_date_params', 'extract_date_params', 'parse_date_value', 'format_date_value', 'DATE_PARAM_NAMES']

