# -*- coding: utf-8 -*-

"""Data fetching utilities with parallel processing"""

import datetime
import threading
import queue
from typing import Dict, Any, List, Callable

from .error_detector import is_date_range_error
from .date_parser import format_date_value


def recursive_fetch(
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    original_kwargs: Dict[str, Any],
    date_params: Dict[str, Any],
    endpoint_callable: Callable,
    max_days: int,
    results_queue: queue.Queue,
    task_queue: queue.Queue,
    exceptions_list: List[Exception],
    results_lock: threading.Lock,
    exceptions_lock: threading.Lock,
    progress_lock: threading.Lock,
    progress_bar: Any = None,
    depth: int = 0
) -> None:
    """
    Recursive olarak tarih aralığını böl ve verileri topla
    
    Args:
        start_dt: Başlangıç tarihi
        end_dt: Bitiş tarihi
        original_kwargs: Orijinal kwargs
        date_params: Tarih parametreleri bilgisi
        endpoint_callable: Endpoint çağrılabilir fonksiyonu
        max_days: Maksimum gün sayısı
        results_queue: Sonuçların ekleneceği queue
        task_queue: Yeni task'ların ekleneceği queue
        exceptions_list: Exception'ların ekleneceği liste
        results_lock: Results için thread lock
        exceptions_lock: Exceptions için thread lock
        progress_lock: Progress bar için thread lock
        progress_bar: İlerleme çubuğu (opsiyonel)
        depth: Recursive derinlik (max 3 seviye)
    """
    # Maksimum derinlik kontrolü
    if depth > 3:
        with exceptions_lock:
            exceptions_list.append(
                Exception(f"Maximum recursion depth reached for date range: {start_dt} to {end_dt}")
            )
        return
    
    # Tek bir aralık için istek yapmayı dene
    try:
        new_kwargs = original_kwargs.copy()
        start_param = date_params['start_param']
        end_param = date_params['end_param']
        original_start_value = date_params['start_value']
        original_end_value = date_params['end_value']
        
        # Tarih değerlerini formatla
        formatted_start = format_date_value(start_dt, original_start_value)
        formatted_end = format_date_value(end_dt, original_end_value)
        
        # kwargs'a ekle
        new_kwargs[start_param] = formatted_start
        new_kwargs[end_param] = formatted_end
        
        # Endpoint çağrısı yap
        result = endpoint_callable(**new_kwargs)
        
        # Başarılı sonucu queue'ya ekle
        with results_lock:
            results_queue.put(result)
        
        # İlerleme güncelle
        if progress_bar is not None:
            with progress_lock:
                try:
                    # alive_progress'te progress_bar bir callable objesi
                    # Bazı versiyonlarda progress_bar() çağrısı increment yapar
                    # Bazı versiyonlarda progress_bar(1) çağrısı gerekir
                    # ContextDecorator hatası alınırsa, progress bar'ı güncellemeyi atla
                    if hasattr(progress_bar, 'current'):
                        # current attribute varsa, direkt increment yap
                        progress_bar.current += 1
                    elif callable(progress_bar):
                        # Callable ise, argümanlı veya argümansız çağır
                        try:
                            progress_bar(1)
                        except TypeError:
                            try:
                                progress_bar()
                            except TypeError:
                                # ContextDecorator hatası - progress bar'ı güncellemeyi atla
                                pass
                except (TypeError, AttributeError):
                    # Hata durumunda sessizce devam et
                    pass
        
    except Exception as e:
        # Tarih aralığı hatası kontrolü
        if is_date_range_error(e):
            # Daha küçük parçalara böl
            next_max_days = max_days // 2
            if next_max_days < 30:
                next_max_days = 30  # Minimum 30 gün
            
            # Aralığı ikiye böl
            total_days = (end_dt - start_dt).days
            if total_days <= 1:
                # Çok küçük aralık, exception fırlat
                with exceptions_lock:
                    exceptions_list.append(
                        Exception(f"Date range too small to split: {start_dt} to {end_dt}")
                    )
                return
            
            mid_point = start_dt + datetime.timedelta(days=total_days // 2)
            mid_point = mid_point.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # İki parçayı task queue'ya ekle (paralel işlenmesi için)
            with results_lock:
                task_queue.put((start_dt, mid_point, next_max_days, depth + 1))
                next_start = mid_point + datetime.timedelta(days=1)
                if next_start < end_dt:
                    task_queue.put((next_start, end_dt, next_max_days, depth + 1))
        else:
            # Tarih aralığı hatası değilse exception'ı kaydet
            with exceptions_lock:
                exceptions_list.append(e)


def worker_thread(
    task_queue: queue.Queue,
    results_queue: queue.Queue,
    exceptions_list: List[Exception],
    original_kwargs: Dict[str, Any],
    date_params: Dict[str, Any],
    endpoint_callable: Callable,
    results_lock: threading.Lock,
    exceptions_lock: threading.Lock,
    progress_lock: threading.Lock,
    progress_bar: Any = None
) -> None:
    """
    Worker thread fonksiyonu - task queue'dan görev alır ve işler
    
    Args:
        task_queue: İşlenecek görevlerin olduğu queue
        results_queue: Sonuçların ekleneceği queue
        exceptions_list: Exception'ların ekleneceği liste
        original_kwargs: Orijinal kwargs
        date_params: Tarih parametreleri bilgisi
        endpoint_callable: Endpoint çağrılabilir fonksiyonu
        results_lock: Results için thread lock
        exceptions_lock: Exceptions için thread lock
        progress_lock: Progress bar için thread lock
        progress_bar: İlerleme çubuğu (opsiyonel)
    """
    while True:
        try:
            # Task queue'dan görev al (timeout ile)
            task = task_queue.get(timeout=1)
            
            # Sentinel değeri kontrolü (thread'i sonlandır)
            if task is None:
                break
            
            # Task formatı: (start_dt, end_dt, max_days, depth)
            if len(task) == 4:
                start_dt, end_dt, max_days, depth = task
            else:
                # Eski format desteği (geriye uyumluluk)
                start_dt, end_dt = task
                max_days = 365
                depth = 0
            
            # Recursive fetch çağrısı
            recursive_fetch(
                start_dt, end_dt,
                original_kwargs, date_params,
                endpoint_callable, max_days,
                results_queue, task_queue, exceptions_list,
                results_lock, exceptions_lock, progress_lock,
                progress_bar, depth
            )
            
            # Task tamamlandı
            task_queue.task_done()
            
        except queue.Empty:
            # Timeout - devam et
            continue
        except Exception as e:
            # Beklenmeyen hata
            with exceptions_lock:
                exceptions_list.append(e)
            try:
                task_queue.task_done()
            except ValueError:
                # Task zaten done edilmiş
                pass


__all__ = ['recursive_fetch', 'worker_thread']

