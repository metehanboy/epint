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

from __future__ import annotations

import datetime as _dt
from zoneinfo import ZoneInfo
from typing import Optional, Union, Tuple
from calendar import monthrange


class DateTimeUtils:

    DEFAULT_TIMEZONE = ZoneInfo("Europe/Istanbul")

    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    @classmethod
    def now(cls) -> _dt.datetime:
        return _dt.datetime.now(cls.DEFAULT_TIMEZONE)

    @classmethod
    def today(cls) -> _dt.date:
        return cls.now().date()

    @classmethod
    def utc_now(cls) -> _dt.datetime:
        return _dt.datetime.now(_dt.timezone.utc)

    @classmethod
    def from_string(
        cls, date_string: str, format_string: Optional[str] = None
    ) -> _dt.datetime:
        if format_string is None:
            return cls._auto_parse_datetime(date_string)
        else:
            dt = _dt.datetime.strptime(date_string, format_string)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)
            return dt

    @classmethod
    def from_date_string(cls, date_string: str) -> _dt.date:
        formats = [cls.DATE_FORMAT, "%d/%m/%Y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                return _dt.datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue
        raise ValueError(
            f"Tarih parse edilemedi: '{date_string}'. "
            f"Geçerli formatlar: {', '.join(formats)}"
        )

    @classmethod
    def to_string(cls, dt: Union[_dt.datetime, _dt.date], format_string: str = DATETIME_FORMAT) -> str:
        # date nesnesi ise datetime'a çevir
        if isinstance(dt, _dt.date) and not isinstance(dt, _dt.datetime):
            dt = _dt.datetime.combine(dt, _dt.time.min)
        return dt.strftime(format_string)

    @classmethod
    def to_iso_string(cls, dt: Union[_dt.datetime, _dt.date]) -> str:
        # date nesnesi ise datetime'a çevir
        if isinstance(dt, _dt.date) and not isinstance(dt, _dt.datetime):
            dt = _dt.datetime.combine(dt, _dt.time.min)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)

        formatted = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        if len(formatted) > 19 and formatted[-5] in "+-":
            formatted = formatted[:-2] + ":" + formatted[-2:]
        return formatted

    @classmethod
    def to_gop_iso_string(cls, dt: Union[_dt.datetime, _dt.date]) -> str:
        """GOP servisi için özel ISO format: 2016-04-22T00:00:00.000+0300"""
        # date nesnesi ise datetime'a çevir
        if isinstance(dt, _dt.date) and not isinstance(dt, _dt.datetime):
            dt = _dt.datetime.combine(dt, _dt.time.min)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)

        # Timezone offset'i al (+0300 formatında, : olmadan)
        offset = dt.strftime("%z")

        # Milisaniye ekle
        milliseconds = dt.microsecond // 1000

        # Format: YYYY-MM-DDTHH:MM:SS.mmm+HHMM
        formatted = dt.strftime(f"%Y-%m-%dT%H:%M:%S.{milliseconds:03d}{offset}")
        return formatted

    def to_gunici_iso_string(cls, dt: Union[_dt.datetime, _dt.date]) -> str:
        if isinstance(dt, _dt.date) and not isinstance(dt, _dt.datetime):
            dt = _dt.datetime.combine(dt, _dt.time.min)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)

        # Format: YYYY-MM-DDTHH:MM:SS
        formatted = dt.strftime(f"%Y-%m-%dT%H:%M:%S")
        return formatted

    @classmethod
    def add_hours(cls, dt: _dt.datetime, hours: int) -> _dt.datetime:

        return dt + _dt.timedelta(hours=hours)

    @classmethod
    def add_minutes(cls, dt:_dt.datetime, minutes: int) -> _dt.datetime:

        return dt + _dt.timedelta(minutes=minutes)

    @classmethod
    def add_seconds(cls, dt: _dt.datetime, seconds: int) -> _dt.datetime:

        return dt + _dt.timedelta(seconds=seconds)

    @classmethod
    def get_timedelta(cls, delta_type: str, delta_value: Union[int, float]) -> _dt.timedelta:

        VALID_DELTA_TYPES = ["seconds", "minutes", "hours", "days", "weeks", "microseconds"]

        delta_type = delta_type.lower()

        if delta_type not in VALID_DELTA_TYPES:
            valid_types = ", ".join(f"'{t}'" for t in VALID_DELTA_TYPES)
            raise ValueError(
                f"Geçersiz delta_type: '{delta_type}'. "
                f"Geçerli değerler: {valid_types}"
            )

        return _dt.timedelta(**{delta_type: delta_value})

    @classmethod
    def is_expired(cls, expire_date: str, format_string: str = DATETIME_FORMAT) -> bool:

        try:
            expire_dt = _dt.datetime.strptime(expire_date, format_string)
            if expire_dt.tzinfo is None:
                expire_dt = expire_dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)
            return cls.now() > expire_dt
        except Exception:
            return True

    @classmethod
    def get_validity_status(
        cls, expire_date: str, format_string: str = DATETIME_FORMAT
    ) -> str:

        try:
            expire_dt = _dt.datetime.strptime(expire_date, format_string)
            if expire_dt.tzinfo is None:
                expire_dt = expire_dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)
            return "GEÇERLİ" if cls.now() < expire_dt else "GEÇERSİZ"
        except Exception:
            return "TARİH HATALI"

    @classmethod
    def _auto_parse_datetime(cls, date_string: str) -> _dt.datetime:

        iso_result = cls._try_iso_format(date_string)
        if iso_result:
            return iso_result

        other_result = cls._try_other_formats(date_string)
        if other_result:
            return other_result

        raise ValueError(
            f"Datetime parse edilemedi: '{date_string}'. "
            f"ISO 8601 formatı veya şu formatlardan biri kullanın: "
            f"'YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM', 'DD/MM/YYYY HH:MM:SS'"
        )

    @classmethod
    def _try_iso_format(cls, date_string: str) -> Optional[_dt.datetime]:

        if "T" in date_string or "Z" in date_string:
            try:
                dt = _dt.datetime.fromisoformat(date_string.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)
                return dt.astimezone(cls.DEFAULT_TIMEZONE)
            except ValueError:
                pass
        return None

    @classmethod
    def _try_other_formats(cls, date_string: str) -> Optional[_dt.datetime]:

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                dt = _dt.datetime.strptime(date_string, fmt)
                return dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)
            except ValueError:
                continue
        return None

    @classmethod
    def convert_to_timezone(
        cls, dt: _dt.datetime, target_timezone: Union[str, ZoneInfo]
    ) -> _dt.datetime:

        if isinstance(target_timezone, str):
            target_timezone = ZoneInfo(target_timezone)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)

        return dt.astimezone(target_timezone)

    @classmethod
    def get_timezone_info(cls) -> dict:

        now = cls.now()
        return {
            "timezone": str(cls.DEFAULT_TIMEZONE),
            "current_time": cls.to_string(now),
            "current_time_iso": cls.to_iso_string(now),
            "utc_offset": now.strftime("%z"),
        }

    @classmethod
    def get_time_dam(cls) -> _dt.date:

        now = cls.now()
        if now.hour < 14:
            return cls.get_today()
        else:
            return cls.get_tomorrow()

    @classmethod
    def get_time_bpm(cls) -> _dt.date:

        now = cls.now()
        if now.hour < 16:
            return cls.get_today()
        else:
            return cls.get_tomorrow()

    @classmethod
    def get_this_month(cls) -> _dt.date:

        now = cls.now()
        return _dt.date(now.year, now.month, 1)

    @classmethod
    def get_today(cls) -> _dt.date:

        return cls.now().date()

    @classmethod
    def get_year(cls) -> _dt.date:

        now = cls.now()
        return _dt.date(now.year, 1, 1)

    @classmethod
    def get_last_year(cls) -> _dt.date:

        now = cls.now()
        return _dt.date(now.year - 1, 1, 1)

    @classmethod
    def get_yesterday(cls) -> _dt.date:

        yesterday = cls.now() - _dt.timedelta(days=1)
        return yesterday.date()

    @classmethod
    def get_tomorrow(cls) -> _dt.date:

        tomorrow = cls.now() + _dt.timedelta(days=1)
        return tomorrow.date()

    @classmethod
    def get_settlement_date(
        cls, date: Union[Tuple[int, int, int], _dt.date]
    ) -> Tuple[_dt.date, _dt.date]:

        if isinstance(date, _dt.date):
            y, m, d = date.year, date.month, date.day
        else:
            y, m, d = date

        period = _dt.datetime(y, m, 1, tzinfo=cls.DEFAULT_TIMEZONE)
        _, days = monthrange(y, m)
        settlement_date = _dt.datetime(
            period.year, period.month, 15, tzinfo=cls.DEFAULT_TIMEZONE
        )
        if settlement_date.weekday() == 5:
            settlement_date = settlement_date + _dt.timedelta(days=2)
        elif settlement_date.weekday() == 6:
            settlement_date = settlement_date + _dt.timedelta(days=1)

        transparency_date = settlement_date + _dt.timedelta(days=1)
        transparency_date_day = transparency_date.day

        if d < transparency_date_day:
            selected_period = (period - _dt.timedelta(days=35)).replace(day=1)
            yd, md = selected_period.year, selected_period.month
        else:
            selected_period = (period - _dt.timedelta(days=1)).replace(day=1)
            yd, md = selected_period.year, selected_period.month

        _, dd = monthrange(yd, md)
        return _dt.date(yd, md, 1), _dt.date(yd, md, dd)

    @classmethod
    def get_current_settlement_day(
        cls,
    ) -> Tuple[_dt.date, _dt.date]:

        now = cls.now()
        fday, lday = cls.get_settlement_date(now.date())
        return fday, lday

    @classmethod
    def get_month_range(cls, date: Union[str, _dt.date, _dt.datetime]) -> Tuple[_dt.date, _dt.date]:
        # String ise date'e çevir
        if isinstance(date, str):
            try:
                # Önce datetime formatını dene
                date = cls.from_string(date).date()
            except (ValueError, AttributeError):
                # Datetime parse edilemezse date formatını dene
                date = cls.from_date_string(date)

        # datetime ise date'e çevir
        if isinstance(date, _dt.datetime):
            date = date.date()

        year = date.year
        month = date.month

        # Ayın ilk günü
        first_day = _dt.date(year, month, 1)

        # Ayın son günü
        _, last_day_num = monthrange(year, month)
        last_day = _dt.date(year, month, last_day_num)

        return first_day, last_day

    @classmethod
    def get_current_settlement_fday(cls) -> _dt.date:

        now = cls.now()
        fday, lday = cls.get_settlement_date(now.date())
        return fday

    @classmethod
    def get_current_settlement_lday(cls) -> _dt.date:

        now = cls.now()
        fday, lday = cls.get_settlement_date(now.date())
        return lday
