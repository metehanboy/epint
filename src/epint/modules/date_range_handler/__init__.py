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

"""Date range handler module for handling date range errors in API calls"""

import datetime
import threading
import queue
from typing import Dict, Any, List, Optional, Callable

from .error_detector import is_date_range_error
from .date_parser import extract_date_params, parse_date_value, format_date_value, DATE_PARAM_NAMES
from .result_merger import merge_results
from .data_fetcher import recursive_fetch, worker_thread


class DateRangeHandler:
    """Tarih aralığı hatası yönetimi için handler sınıfı"""
    
    def __init__(self, max_workers: int = 5):
        """
        DateRangeHandler oluştur
        
        Args:
            max_workers: Paralel çalışacak thread sayısı (default: 5)
        """
        self.date_param_names = DATE_PARAM_NAMES
        self.max_workers = max_workers
        self.results_lock = threading.Lock()
        self.exceptions_lock = threading.Lock()
        self.progress_lock = threading.Lock()
    
    def is_date_range_error(self, exception: Exception) -> bool:
        """Tarih aralığı hatası olup olmadığını kontrol et"""
        return is_date_range_error(exception)
    
    def extract_date_params(self, kwargs: Dict[str, Any], request_model: Any) -> Optional[Dict[str, Any]]:
        """Tarih parametrelerini çıkar"""
        return extract_date_params(kwargs, request_model)
    
    def parse_date_value(self, value: Any) -> Optional[datetime.datetime]:
        """Tarih değerini parse et"""
        return parse_date_value(value)
    
    def format_date_value(self, dt: datetime.datetime, original_value: Any) -> Any:
        """Orijinal format'a göre tarih değerini formatla"""
        return format_date_value(dt, original_value)
    
    def merge_results(self, results: List[Any]) -> Any:
        """Sonuçları birleştir"""
        return merge_results(results)
    
    def _recursive_fetch(
        self,
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
        original_kwargs: Dict[str, Any],
        date_params: Dict[str, Any],
        endpoint_callable: Callable,
        max_days: int,
        results_queue: queue.Queue,
        task_queue: queue.Queue,
        exceptions_list: List[Exception],
        progress_bar: Any = None,
        depth: int = 0
    ) -> None:
        """Recursive olarak tarih aralığını böl ve verileri topla"""
        return recursive_fetch(
            start_dt, end_dt,
            original_kwargs, date_params,
            endpoint_callable, max_days,
            results_queue, task_queue, exceptions_list,
            self.results_lock, self.exceptions_lock, self.progress_lock,
            progress_bar, depth
        )
    
    def _worker_thread(
        self,
        task_queue: queue.Queue,
        results_queue: queue.Queue,
        exceptions_list: List[Exception],
        original_kwargs: Dict[str, Any],
        date_params: Dict[str, Any],
        endpoint_callable: Callable,
        progress_bar: Any = None
    ) -> None:
        """Worker thread fonksiyonu - task queue'dan görev alır ve işler"""
        return worker_thread(
            task_queue, results_queue, exceptions_list,
            original_kwargs, date_params, endpoint_callable,
            self.results_lock, self.exceptions_lock, self.progress_lock,
            progress_bar
        )
    
    def handle_date_range_error(
        self,
        original_kwargs: Dict[str, Any],
        request_model: Any,
        endpoint_callable: Callable,
        max_days: int = 300
    ) -> Any:
        """
        Tarih aralığı hatasını handle et - recursive ve paralel olarak verileri topla
        
        Args:
            original_kwargs: Orijinal kwargs
            request_model: Request model objesi
            endpoint_callable: Endpoint çağrılabilir fonksiyonu
            max_days: Maksimum gün sayısı (default: 300, API limiti 1 yıl ama güvenlik için 300 gün kullanıyoruz)
        
        Returns:
            Birleştirilmiş sonuçlar
        """
        # Tarih parametrelerini çıkar
        date_params = self.extract_date_params(original_kwargs, request_model)
        if not date_params:
            return None
        
        # Tarih değerlerini parse et
        start_dt = self.parse_date_value(date_params['start_value'])
        end_dt = self.parse_date_value(date_params['end_value'])
        
        if not start_dt or not end_dt:
            return None
        
        # Tarih aralığını kontrol et - eğer max_days'den fazlaysa direkt böl
        total_days = (end_dt - start_dt).days
        
        # Queue'lar ve thread-safe listeler oluştur
        task_queue = queue.Queue()
        results_queue = queue.Queue()
        exceptions_list = []
        
        # Eğer tarih aralığı max_days'den fazlaysa, direkt olarak böl
        if total_days > max_days:
            # Aralığı parçalara böl
            current_start = start_dt
            while current_start < end_dt:
                current_end = min(
                    current_start + datetime.timedelta(days=max_days),
                    end_dt
                )
                task_queue.put((current_start, current_end, max_days, 0))
                current_start = current_end + datetime.timedelta(days=1)
        else:
            # İlk görevi ekle (recursive yapı gerektiğinde bölecek)
            task_queue.put((start_dt, end_dt, max_days, 0))
        
        # Worker thread'leri başlat
        threads = []
        for _ in range(self.max_workers):
            thread = threading.Thread(
                target=self._worker_thread,
                args=(
                    task_queue, results_queue, exceptions_list,
                    original_kwargs, date_params, endpoint_callable, None
                ),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Tüm görevlerin tamamlanmasını bekle
        task_queue.join()
        
        # Thread'leri sonlandır (sentinel gönder)
        for _ in range(self.max_workers):
            task_queue.put(None)
        
        # Thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5)
        
        # Exception kontrolü
        if exceptions_list:
            # İlk exception'ı fırlat
            raise exceptions_list[0]
        
        # Sonuçları queue'dan al
        results = []
        while not results_queue.empty():
            try:
                result = results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break
        
        # Sonuçları birleştir
        return self.merge_results(results)


__all__ = ['DateRangeHandler']
