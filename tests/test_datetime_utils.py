# -*- coding: utf-8 -*-
import datetime as dt

from epint.modules.datetime import DateTimeUtils


def test_to_iso_string_uses_colon_offset():
    d = dt.datetime(2026, 4, 22, 0, 0, 0)
    assert DateTimeUtils.to_iso_string(d) == "2026-04-22T00:00:00+03:00"


def test_to_gop_iso_string_uses_milliseconds_and_no_colon_offset():
    d = dt.datetime(2016, 4, 22, 0, 0, 0)
    assert DateTimeUtils.to_gop_iso_string(d) == "2016-04-22T00:00:00.000+0300"


def test_to_gunici_iso_string_has_no_timezone_suffix():
    # Regresyon testi: to_gunici_iso_string @classmethod olmadan tek argümanla
    # çağrıldığında TypeError fırlatıyordu (bkz. request_model._convert_value_by_format).
    d = dt.datetime(2016, 4, 22, 0, 0, 0)
    assert DateTimeUtils.to_gunici_iso_string(d) == "2016-04-22T00:00:00"


def test_is_expired_for_past_date():
    past = DateTimeUtils.to_string(DateTimeUtils.now() - dt.timedelta(hours=1))
    assert DateTimeUtils.is_expired(past) is True


def test_is_expired_for_future_date():
    future = DateTimeUtils.to_string(DateTimeUtils.now() + dt.timedelta(hours=1))
    assert DateTimeUtils.is_expired(future) is False


def test_is_expired_treats_garbage_as_expired():
    assert DateTimeUtils.is_expired("not-a-date") is True


def test_get_validity_status():
    future = DateTimeUtils.to_string(DateTimeUtils.now() + dt.timedelta(hours=1))
    past = DateTimeUtils.to_string(DateTimeUtils.now() - dt.timedelta(hours=1))
    assert DateTimeUtils.get_validity_status(future) == "GEÇERLİ"
    assert DateTimeUtils.get_validity_status(past) == "GEÇERSİZ"
    assert DateTimeUtils.get_validity_status("garbage") == "TARİH HATALI"


def test_from_string_auto_parses_date_only():
    parsed = DateTimeUtils.from_string("2026-07-20")
    assert (parsed.year, parsed.month, parsed.day) == (2026, 7, 20)


def test_from_string_auto_parses_iso_with_time():
    parsed = DateTimeUtils.from_string("2026-07-20T10:30:00")
    assert (parsed.hour, parsed.minute) == (10, 30)
