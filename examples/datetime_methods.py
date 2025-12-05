# -*- coding: utf-8 -*-

"""
DateTimeUtils Metodlarını Göster

DateTimeUtils sınıfının tüm public metodlarını çağırıp sonuçlarını gösterir.
"""

import sys
import os
import datetime as dt
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.epint.utils.datetime_utils import DateTimeUtils


def print_method_result(method_name, result):
    """Metod adı ve sonucunu güzel formatta yazdır"""
    print(f"\n{'='*80}")
    print(f"Method: {method_name}")
    print(f"{'='*80}")
    
    if isinstance(result, dt.datetime):
        print(f"Result: {result}")
        print(f"Type: datetime.datetime")
        print(f"ISO Format: {DateTimeUtils.to_iso_string(result)}")
    elif isinstance(result, dt.date):
        print(f"Result: {result}")
        print(f"Type: datetime.date")
        print(f"ISO Format: {result.isoformat()}")
    elif isinstance(result, tuple):
        print(f"Result: {result}")
        print(f"Type: tuple")
        for i, item in enumerate(result):
            if isinstance(item, dt.date):
                print(f"  [{i}]: {item} ({item.isoformat()})")
            else:
                print(f"  [{i}]: {item}")
    elif isinstance(result, dict):
        print(f"Result:")
        print(f"Type: dict")
        for key, value in result.items():
            print(f"  {key}: {value}")
    elif isinstance(result, bool):
        print(f"Result: {result}")
        print(f"Type: bool")
    elif isinstance(result, str):
        print(f"Result: {result}")
        print(f"Type: str")
    else:
        print(f"Result: {result}")
        print(f"Type: {type(result).__name__}")


def main():
    """Tüm metodları çağır ve sonuçlarını göster"""
    print("\n" + "="*80)
    print("DateTimeUtils - Tüm Metodlar ve Sonuçları")
    print("="*80)
    
    # Temel metodlar
    print_method_result("now()", DateTimeUtils.now())
    print_method_result("today()", DateTimeUtils.today())
    print_method_result("utc_now()", DateTimeUtils.utc_now())
    
    # Parse metodları
    print_method_result("from_string('2024-01-15 14:30:00')", 
                       DateTimeUtils.from_string("2024-01-15 14:30:00"))
    print_method_result("from_string('2024-01-15T14:30:00+03:00')", 
                       DateTimeUtils.from_string("2024-01-15T14:30:00+03:00"))
    print_method_result("from_date_string('2024-01-15')", 
                       DateTimeUtils.from_date_string("2024-01-15"))
    
    # Format metodları
    now_dt = DateTimeUtils.now()
    print_method_result("to_string(now)", 
                       DateTimeUtils.to_string(now_dt))
    print_method_result("to_iso_string(now)", 
                       DateTimeUtils.to_iso_string(now_dt))
    
    # Zaman işlemleri
    test_dt = DateTimeUtils.from_string("2024-01-15 14:30:00")
    print_method_result("add_hours(dt, 5)", 
                       DateTimeUtils.add_hours(test_dt, 5))
    print_method_result("add_seconds(dt, 3600)", 
                       DateTimeUtils.add_seconds(test_dt, 3600))
    
    # Validasyon metodları
    past_date = (DateTimeUtils.now() - dt.timedelta(days=1)).strftime(DateTimeUtils.DATETIME_FORMAT)
    future_date = (DateTimeUtils.now() + dt.timedelta(days=1)).strftime(DateTimeUtils.DATETIME_FORMAT)
    print_method_result(f"is_expired('{past_date}')", 
                       DateTimeUtils.is_expired(past_date))
    print_method_result(f"is_expired('{future_date}')", 
                       DateTimeUtils.is_expired(future_date))
    print_method_result(f"get_validity_status('{past_date}')", 
                       DateTimeUtils.get_validity_status(past_date))
    print_method_result(f"get_validity_status('{future_date}')", 
                       DateTimeUtils.get_validity_status(future_date))
    
    # Timezone işlemleri
    print_method_result("convert_to_timezone(now, 'UTC')", 
                       DateTimeUtils.convert_to_timezone(now_dt, "UTC"))
    print_method_result("get_timezone_info()", 
                       DateTimeUtils.get_timezone_info())
    
    # Tarih metodları
    print_method_result("get_today()", DateTimeUtils.get_today())
    print_method_result("get_yesterday()", DateTimeUtils.get_yesterday())
    print_method_result("get_tomorrow()", DateTimeUtils.get_tomorrow())
    print_method_result("get_this_month()", DateTimeUtils.get_this_month())
    print_method_result("get_year()", DateTimeUtils.get_year())
    print_method_result("get_last_year()", DateTimeUtils.get_last_year())
    
    # Özel tarih metodları
    print_method_result("get_time_dam()", DateTimeUtils.get_time_dam())
    print_method_result("get_time_bpm()", DateTimeUtils.get_time_bpm())
    
    # Settlement metodları
    test_date = dt.date(2024, 1, 15)
    print_method_result(f"get_settlement_date({test_date})", 
                       DateTimeUtils.get_settlement_date(test_date))
    print_method_result("get_settlement_date((2024, 1, 15))", 
                       DateTimeUtils.get_settlement_date((2024, 1, 15)))
    print_method_result("get_current_settlement_day()", 
                       DateTimeUtils.get_current_settlement_day())
    print_method_result("get_current_settlement_fday()", 
                       DateTimeUtils.get_current_settlement_fday())
    print_method_result("get_current_settlement_lday()", 
                       DateTimeUtils.get_current_settlement_lday())
    
    print("\n" + "="*80)
    print("Tüm metodlar gösterildi!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
