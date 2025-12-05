# -*- coding: utf-8 -*-

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
    def to_string(cls, dt: _dt.datetime, format_string: str = DATETIME_FORMAT) -> str:
        return dt.strftime(format_string)

    @classmethod
    def to_iso_string(cls, dt: _dt.datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.DEFAULT_TIMEZONE)

        formatted = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        if len(formatted) > 19 and formatted[-5] in "+-":
            formatted = formatted[:-2] + ":" + formatted[-2:]
        return formatted

    @classmethod
    def add_hours(cls, dt: _dt.datetime, hours: int) -> _dt.datetime:

        return dt + _dt.timedelta(hours=hours)

    @classmethod
    def add_seconds(cls, dt: _dt.datetime, seconds: int) -> _dt.datetime:

        return dt + _dt.timedelta(seconds=seconds)

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
    def get_time_dam(cls) -> Tuple[int, int, int]:

        now = cls.now()
        if now.hour < 14:
            return cls.get_today()
        else:
            return cls.get_tomorrow()

    @classmethod
    def get_time_bpm(cls) -> Tuple[int, int, int]:

        now = cls.now()
        if now.hour < 16:
            return cls.get_today()
        else:
            return cls.get_tomorrow()

    @classmethod
    def get_this_month(cls) -> Tuple[int, int, int]:

        now = cls.now()
        return (now.year, now.month, 1)

    @classmethod
    def get_today(cls) -> Tuple[int, int, int]:

        now = cls.now()
        return (now.year, now.month, now.day)

    @classmethod
    def get_year(cls) -> Tuple[int, int, int]:

        now = cls.now()
        return (now.year, 1, 1)

    @classmethod
    def get_last_year(cls) -> Tuple[int, int, int]:

        now = cls.now()
        return (now.year - 1, 1, 1)

    @classmethod
    def get_yesterday(cls) -> Tuple[int, int, int]:

        yesterday = cls.now() - _dt.timedelta(days=1)
        return (yesterday.year, yesterday.month, yesterday.day)

    @classmethod
    def get_tomorrow(cls) -> Tuple[int, int, int]:

        tomorrow = cls.now() + _dt.timedelta(days=1)
        return (tomorrow.year, tomorrow.month, tomorrow.day)

    @classmethod
    def get_settlement_date(
        cls, date: Tuple[int, int, int]
    ) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:

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
        return (yd, md, 1), (yd, md, dd)

    @classmethod
    def get_current_settlement_day(
        cls,
    ) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:

        now = cls.now()
        y, m, d = now.year, now.month, now.day
        fday, lday = cls.get_settlement_date((y, m, d))
        return fday, lday

    @classmethod
    def get_current_settlement_fday(cls) -> Tuple[int, int, int]:

        now = cls.now()
        y, m, d = now.year, now.month, now.day
        fday, lday = cls.get_settlement_date((y, m, d))
        return fday

    @classmethod
    def get_current_settlement_lday(cls) -> Tuple[int, int, int]:

        now = cls.now()
        y, m, d = now.year, now.month, now.day
        fday, lday = cls.get_settlement_date((y, m, d))
        return lday
