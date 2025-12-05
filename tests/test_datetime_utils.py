# -*- coding: utf-8 -*-

"""
DateTimeUtils Testleri

DateTimeUtils sınıfının tüm metodlarını test eder.
"""

import unittest
import datetime as dt
from zoneinfo import ZoneInfo
import sys
import os

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.epint.utils.datetime_utils import DateTimeUtils


class TestDateTimeUtils(unittest.TestCase):
    """DateTimeUtils sınıfı testleri"""

    def setUp(self):
        """Her test öncesi çalışır"""
        self.default_timezone = ZoneInfo("Europe/Istanbul")

    def test_now(self):
        """now() metodunu test et"""
        result = DateTimeUtils.now()
        self.assertIsInstance(result, dt.datetime)
        self.assertEqual(result.tzinfo, self.default_timezone)
        self.assertAlmostEqual(
            result.timestamp(),
            dt.datetime.now(self.default_timezone).timestamp(),
            delta=1.0
        )

    def test_today(self):
        """today() metodunu test et"""
        result = DateTimeUtils.today()
        self.assertIsInstance(result, dt.date)
        self.assertEqual(result, dt.datetime.now(self.default_timezone).date())

    def test_utc_now(self):
        """utc_now() metodunu test et"""
        result = DateTimeUtils.utc_now()
        self.assertIsInstance(result, dt.datetime)
        self.assertEqual(result.tzinfo, dt.timezone.utc)
        self.assertAlmostEqual(
            result.timestamp(),
            dt.datetime.now(dt.timezone.utc).timestamp(),
            delta=1.0
        )

    def test_from_string_with_format(self):
        """from_string() metodunu format ile test et"""
        result = DateTimeUtils.from_string("2024-01-15 14:30:00", "%Y-%m-%d %H:%M:%S")
        self.assertIsInstance(result, dt.datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.tzinfo, self.default_timezone)

    def test_from_string_iso_format(self):
        """from_string() metodunu ISO format ile test et"""
        result = DateTimeUtils.from_string("2024-01-15T14:30:00+03:00")
        self.assertIsInstance(result, dt.datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_from_string_auto_parse(self):
        """from_string() metodunu otomatik parse ile test et"""
        # ISO format
        result = DateTimeUtils.from_string("2024-01-15T14:30:00")
        self.assertIsInstance(result, dt.datetime)
        
        # Standart format
        result = DateTimeUtils.from_string("2024-01-15 14:30:00")
        self.assertIsInstance(result, dt.datetime)
        
        # Tarih formatı
        result = DateTimeUtils.from_string("2024-01-15")
        self.assertIsInstance(result, dt.datetime)

    def test_from_string_invalid(self):
        """from_string() metodunu geçersiz format ile test et"""
        with self.assertRaises(ValueError):
            DateTimeUtils.from_string("invalid-date")

    def test_from_date_string(self):
        """from_date_string() metodunu test et"""
        # YYYY-MM-DD formatı
        result = DateTimeUtils.from_date_string("2024-01-15")
        self.assertIsInstance(result, dt.date)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
        
        # DD/MM/YYYY formatı
        result = DateTimeUtils.from_date_string("15/01/2024")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
        
        # DD-MM-YYYY formatı
        result = DateTimeUtils.from_date_string("15-01-2024")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_from_date_string_invalid(self):
        """from_date_string() metodunu geçersiz format ile test et"""
        with self.assertRaises(ValueError):
            DateTimeUtils.from_date_string("invalid-date")

    def test_to_string(self):
        """to_string() metodunu test et"""
        dt_obj = dt.datetime(2024, 1, 15, 14, 30, 0, tzinfo=self.default_timezone)
        result = DateTimeUtils.to_string(dt_obj)
        self.assertEqual(result, "2024-01-15 14:30:00")
        
        # Custom format
        result = DateTimeUtils.to_string(dt_obj, "%Y/%m/%d")
        self.assertEqual(result, "2024/01/15")

    def test_to_iso_string(self):
        """to_iso_string() metodunu test et"""
        dt_obj = dt.datetime(2024, 1, 15, 14, 30, 0, tzinfo=self.default_timezone)
        result = DateTimeUtils.to_iso_string(dt_obj)
        self.assertIn("2024-01-15T14:30:00", result)
        self.assertIn("+03:00", result or "+02:00")

    def test_to_iso_string_no_timezone(self):
        """to_iso_string() metodunu timezone olmadan test et"""
        dt_obj = dt.datetime(2024, 1, 15, 14, 30, 0)
        result = DateTimeUtils.to_iso_string(dt_obj)
        self.assertIn("2024-01-15T14:30:00", result)

    def test_add_hours(self):
        """add_hours() metodunu test et"""
        dt_obj = dt.datetime(2024, 1, 15, 14, 30, 0, tzinfo=self.default_timezone)
        result = DateTimeUtils.add_hours(dt_obj, 5)
        self.assertEqual(result.hour, 19)
        self.assertEqual(result.minute, 30)
        
        # Negatif saat
        result = DateTimeUtils.add_hours(dt_obj, -2)
        self.assertEqual(result.hour, 12)

    def test_add_seconds(self):
        """add_seconds() metodunu test et"""
        dt_obj = dt.datetime(2024, 1, 15, 14, 30, 0, tzinfo=self.default_timezone)
        result = DateTimeUtils.add_seconds(dt_obj, 3600)
        self.assertEqual(result.hour, 15)
        self.assertEqual(result.minute, 30)
        
        # Negatif saniye
        result = DateTimeUtils.add_seconds(dt_obj, -1800)
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 0)

    def test_is_expired(self):
        """is_expired() metodunu test et"""
        # Geçmiş tarih
        past_date = (dt.datetime.now(self.default_timezone) - dt.timedelta(days=1)).strftime(
            DateTimeUtils.DATETIME_FORMAT
        )
        self.assertTrue(DateTimeUtils.is_expired(past_date))
        
        # Gelecek tarih
        future_date = (dt.datetime.now(self.default_timezone) + dt.timedelta(days=1)).strftime(
            DateTimeUtils.DATETIME_FORMAT
        )
        self.assertFalse(DateTimeUtils.is_expired(future_date))
        
        # Geçersiz format
        self.assertTrue(DateTimeUtils.is_expired("invalid-date"))

    def test_get_validity_status(self):
        """get_validity_status() metodunu test et"""
        # Geçmiş tarih
        past_date = (dt.datetime.now(self.default_timezone) - dt.timedelta(days=1)).strftime(
            DateTimeUtils.DATETIME_FORMAT
        )
        self.assertEqual(DateTimeUtils.get_validity_status(past_date), "GEÇERSİZ")
        
        # Gelecek tarih
        future_date = (dt.datetime.now(self.default_timezone) + dt.timedelta(days=1)).strftime(
            DateTimeUtils.DATETIME_FORMAT
        )
        self.assertEqual(DateTimeUtils.get_validity_status(future_date), "GEÇERLİ")
        
        # Geçersiz format
        self.assertEqual(DateTimeUtils.get_validity_status("invalid-date"), "TARİH HATALI")

    def test_convert_to_timezone(self):
        """convert_to_timezone() metodunu test et"""
        dt_obj = dt.datetime(2024, 1, 15, 14, 30, 0, tzinfo=self.default_timezone)
        
        # String timezone
        result = DateTimeUtils.convert_to_timezone(dt_obj, "UTC")
        self.assertIsNotNone(result.tzinfo)
        # UTC timezone kontrolü (ZoneInfo veya timezone.utc olabilir)
        self.assertTrue(
            str(result.tzinfo) == "UTC" or 
            result.tzinfo == dt.timezone.utc or
            (hasattr(result.tzinfo, 'key') and result.tzinfo.key == 'UTC')
        )
        
        # ZoneInfo timezone
        result = DateTimeUtils.convert_to_timezone(dt_obj, ZoneInfo("America/New_York"))
        self.assertIsNotNone(result.tzinfo)
        
        # Timezone olmayan datetime
        dt_no_tz = dt.datetime(2024, 1, 15, 14, 30, 0)
        result = DateTimeUtils.convert_to_timezone(dt_no_tz, "UTC")
        self.assertIsNotNone(result.tzinfo)

    def test_get_timezone_info(self):
        """get_timezone_info() metodunu test et"""
        result = DateTimeUtils.get_timezone_info()
        self.assertIsInstance(result, dict)
        self.assertIn("timezone", result)
        self.assertIn("current_time", result)
        self.assertIn("current_time_iso", result)
        self.assertIn("utc_offset", result)
        self.assertEqual(result["timezone"], str(self.default_timezone))

    def test_get_today(self):
        """get_today() metodunu test et"""
        result = DateTimeUtils.get_today()
        self.assertIsInstance(result, dt.date)
        self.assertEqual(result, dt.datetime.now(self.default_timezone).date())

    def test_get_yesterday(self):
        """get_yesterday() metodunu test et"""
        result = DateTimeUtils.get_yesterday()
        self.assertIsInstance(result, dt.date)
        expected = (dt.datetime.now(self.default_timezone) - dt.timedelta(days=1)).date()
        self.assertEqual(result, expected)

    def test_get_tomorrow(self):
        """get_tomorrow() metodunu test et"""
        result = DateTimeUtils.get_tomorrow()
        self.assertIsInstance(result, dt.date)
        expected = (dt.datetime.now(self.default_timezone) + dt.timedelta(days=1)).date()
        self.assertEqual(result, expected)

    def test_get_this_month(self):
        """get_this_month() metodunu test et"""
        result = DateTimeUtils.get_this_month()
        self.assertIsInstance(result, dt.date)
        now = dt.datetime.now(self.default_timezone)
        self.assertEqual(result.year, now.year)
        self.assertEqual(result.month, now.month)
        self.assertEqual(result.day, 1)

    def test_get_year(self):
        """get_year() metodunu test et"""
        result = DateTimeUtils.get_year()
        self.assertIsInstance(result, dt.date)
        now = dt.datetime.now(self.default_timezone)
        self.assertEqual(result.year, now.year)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    def test_get_last_year(self):
        """get_last_year() metodunu test et"""
        result = DateTimeUtils.get_last_year()
        self.assertIsInstance(result, dt.date)
        now = dt.datetime.now(self.default_timezone)
        self.assertEqual(result.year, now.year - 1)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    def test_get_time_dam(self):
        """get_time_dam() metodunu test et"""
        result = DateTimeUtils.get_time_dam()
        self.assertIsInstance(result, dt.date)
        # Saat 14'ten önce bugün, sonra yarın döner
        now = DateTimeUtils.now()
        if now.hour < 14:
            self.assertEqual(result, DateTimeUtils.get_today())
        else:
            self.assertEqual(result, DateTimeUtils.get_tomorrow())

    def test_get_time_bpm(self):
        """get_time_bpm() metodunu test et"""
        result = DateTimeUtils.get_time_bpm()
        self.assertIsInstance(result, dt.date)
        # Saat 16'dan önce bugün, sonra yarın döner
        now = DateTimeUtils.now()
        if now.hour < 16:
            self.assertEqual(result, DateTimeUtils.get_today())
        else:
            self.assertEqual(result, DateTimeUtils.get_tomorrow())

    def test_get_settlement_date_with_tuple(self):
        """get_settlement_date() metodunu tuple ile test et"""
        result = DateTimeUtils.get_settlement_date((2024, 1, 15))
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dt.date)
        self.assertIsInstance(result[1], dt.date)
        # İlk gün ayın 1'i olmalı
        self.assertEqual(result[0].day, 1)
        # Son gün ayın son günü olmalı
        self.assertGreaterEqual(result[1].day, 28)

    def test_get_settlement_date_with_date(self):
        """get_settlement_date() metodunu date objesi ile test et"""
        date_obj = dt.date(2024, 1, 15)
        result = DateTimeUtils.get_settlement_date(date_obj)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dt.date)
        self.assertIsInstance(result[1], dt.date)

    def test_get_current_settlement_day(self):
        """get_current_settlement_day() metodunu test et"""
        result = DateTimeUtils.get_current_settlement_day()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dt.date)
        self.assertIsInstance(result[1], dt.date)
        # İlk gün son günden önce olmalı
        self.assertLessEqual(result[0], result[1])

    def test_get_current_settlement_fday(self):
        """get_current_settlement_fday() metodunu test et"""
        result = DateTimeUtils.get_current_settlement_fday()
        self.assertIsInstance(result, dt.date)
        # get_current_settlement_day ile aynı ilk günü döndürmeli
        fday, _ = DateTimeUtils.get_current_settlement_day()
        self.assertEqual(result, fday)

    def test_get_current_settlement_lday(self):
        """get_current_settlement_lday() metodunu test et"""
        result = DateTimeUtils.get_current_settlement_lday()
        self.assertIsInstance(result, dt.date)
        # get_current_settlement_day ile aynı son günü döndürmeli
        _, lday = DateTimeUtils.get_current_settlement_day()
        self.assertEqual(result, lday)

    def test_settlement_date_edge_cases(self):
        """get_settlement_date() metodunu edge case'ler ile test et"""
        # Ayın başı
        result = DateTimeUtils.get_settlement_date((2024, 1, 1))
        self.assertIsInstance(result[0], dt.date)
        self.assertIsInstance(result[1], dt.date)
        
        # Ayın sonu
        result = DateTimeUtils.get_settlement_date((2024, 1, 31))
        self.assertIsInstance(result[0], dt.date)
        self.assertIsInstance(result[1], dt.date)
        
        # Şubat (kısa ay)
        result = DateTimeUtils.get_settlement_date((2024, 2, 15))
        self.assertIsInstance(result[0], dt.date)
        self.assertIsInstance(result[1], dt.date)


def run_tests():
    """Testleri çalıştır"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDateTimeUtils))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("TEST SONUÇLARI")
    print("="*80)
    print(f"Toplam Test: {result.testsRun}")
    print(f"Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Başarısız: {len(result.failures)}")
    print(f"Hata: {len(result.errors)}")
    
    if result.failures:
        print("\nBaşarısız Testler:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nHatalı Testler:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

