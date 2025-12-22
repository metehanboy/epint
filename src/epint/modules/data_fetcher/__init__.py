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

"""Data fetcher module for handling pagination and date range together"""

import datetime
import threading
import queue
from typing import Dict, Any, List, Optional, Callable

from .pagination_checker import has_pagination
from .date_checker import has_date_params, extract_date_params, parse_date_value, format_date_value
from .error_detector import is_date_range_error, extract_max_days_from_error
from .result_merger import merge_results
from .recursive_fetcher import recursive_fetch, worker_thread
from .page_collector import collect_all_pages


class DataFetcher:
    """Pagination ve date range işlemlerini birlikte yöneten handler sınıfı"""

    def __init__(self, max_workers: int = 5):
        """
        DataFetcher oluştur

        Args:
            max_workers: Paralel çalışacak thread sayısı (default: 5)
        """
        self.max_workers = max_workers
        self.results_lock = threading.Lock()
        self.exceptions_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self._print_queue = None
        self._print_thread = None
        self._print_lock = threading.Lock()

    def _start_print_queue(self):
        """Print queue ve worker thread'i başlat"""
        with self._print_lock:
            if self._print_queue is None:
                self._print_queue = queue.Queue()
                self._print_thread = threading.Thread(
                    target=self._print_worker,
                    daemon=True
                )
                self._print_thread.start()

    def _stop_print_queue(self):
        """Print queue ve worker thread'i durdur"""
        with self._print_lock:
            if self._print_queue is not None:
                self._print_queue.put(None)  # Sentinel value
                if self._print_thread is not None:
                    self._print_thread.join(timeout=2)
                self._print_queue = None
                self._print_thread = None

    def _print_worker(self):
        """Print worker thread - queue'dan mesajları alıp print eder"""
        while True:
            try:
                message = self._print_queue.get(timeout=1)
                if message is None:  # Sentinel value
                    break
                print(message)
                self._print_queue.task_done()
            except queue.Empty:
                continue

    def _print(self, message: str):
        """Thread-safe print - mesajı queue'ya ekler"""
        if self._print_queue is not None:
            self._print_queue.put(message)

    def has_pagination(self, response: Dict[str, Any]) -> bool:
        """Response'da pagination bilgisi var mı kontrol et"""
        return has_pagination(response)

    def collect_all_pages(
        self,
        first_response: Dict[str, Any],
        original_kwargs: Dict[str, Any],
        endpoint_callable: Callable
    ) -> Dict[str, Any]:
        """Tüm sayfaları topla ve birleştir"""
        return collect_all_pages(first_response, original_kwargs, endpoint_callable)

    def fetch_all_data(
        self,
        original_kwargs: Dict[str, Any],
        request_model: Any,
        endpoint_callable: Callable,
        first_response: Optional[Dict[str, Any]] = None,
        max_days: int = 300,
        debug: bool = False
    ) -> Any:
        """
        Tüm verileri topla - hem pagination hem date range için

        Args:
            original_kwargs: Orijinal kwargs
            request_model: Request model objesi
            endpoint_callable: Endpoint çağrılabilir fonksiyonu
            first_response: İlk response (varsa)
            max_days: Maksimum gün sayısı (default: 300)
            debug: Debug modu (print ifadelerini gösterir)

        Returns:
            Birleştirilmiş sonuçlar
        """
        # Debug modunda print queue'yu başlat
        if debug:
            self._start_print_queue()

        try:
            # Tarih parametreleri var mı kontrol et
            date_params = extract_date_params(original_kwargs, request_model)
            has_date_range = date_params is not None

            # Pagination var mı kontrol et
            has_pag = False
            if first_response and isinstance(first_response, dict):
                has_pag = has_pagination(first_response)

            # Sadece pagination varsa
            if has_pag and not has_date_range:
                if debug:
                    self._print("[DataFetcher] Sadece pagination tespit edildi, sayfalar toplanıyor...")
                return self._handle_pagination_only(
                    first_response,
                    original_kwargs,
                    endpoint_callable,
                    debug=debug
                )

            # Sadece date range varsa
            if has_date_range and not has_pag:
                if debug:
                    self._print("[DataFetcher] Sadece tarih aralığı tespit edildi, tarih aralıkları işleniyor...")
                return self._handle_date_range_only(
                    original_kwargs,
                    request_model,
                    endpoint_callable,
                    max_days,
                    debug=debug
                )

            # Hem pagination hem date range varsa
            if has_pag and has_date_range:
                if debug:
                    self._print("[DataFetcher] Hem pagination hem tarih aralığı tespit edildi, her tarih aralığı için tüm sayfalar toplanıyor...")
                return self._handle_both(
                    original_kwargs,
                    request_model,
                    endpoint_callable,
                    first_response,
                    max_days,
                    debug=debug
                )

            # Hiçbiri yoksa direkt döndür
            return first_response if first_response else endpoint_callable(**original_kwargs)
        finally:
            # Debug modunda print queue'yu durdur ve kalan mesajları yazdır
            if debug:
                if self._print_queue is not None:
                    self._print_queue.join()  # Tüm mesajların yazdırılmasını bekle
                self._stop_print_queue()

    def _handle_pagination_only(
        self,
        first_response: Dict[str, Any],
        original_kwargs: Dict[str, Any],
        endpoint_callable: Callable,
        debug: bool = False
    ) -> Dict[str, Any]:
        """Sadece pagination için tüm sayfaları topla"""
        return collect_all_pages(
            first_response,
            original_kwargs,
            endpoint_callable,
            debug=debug,
            print_queue=self._print_queue if debug else None
        )

    def _handle_date_range_only(
        self,
        original_kwargs: Dict[str, Any],
        request_model: Any,
        endpoint_callable: Callable,
        max_days: int,
        debug: bool = False
    ) -> Any:
        """Sadece date range için tüm tarih aralıklarını işle"""
        date_params = extract_date_params(original_kwargs, request_model)
        if not date_params:
            return None

        start_dt = parse_date_value(date_params['start_value'])
        end_dt = parse_date_value(date_params['end_value'])

        if not start_dt or not end_dt:
            return None

        # Queue'lar ve thread-safe listeler oluştur
        task_queue = queue.Queue()
        results_queue = queue.Queue()
        exceptions_list = []

        # Tarih aralığını kontrol et
        total_days = (end_dt - start_dt).days

        if total_days > max_days:
            # Aralığı parçalara böl
            if debug:
                self._print(f"[DataFetcher] Tarih aralığı çok büyük ({total_days} gün), {max_days} günlük parçalara bölünüyor...")
            current_start = start_dt
            chunk_num = 1
            while current_start < end_dt:
                current_end = min(
                    current_start + datetime.timedelta(days=max_days),
                    end_dt
                )
                if debug:
                    self._print(f"[DataFetcher] Parça {chunk_num}: {current_start.strftime('%Y-%m-%d')} - {current_end.strftime('%Y-%m-%d')}")
                task_queue.put((current_start, current_end, max_days, 0, debug, self._print_queue if debug else None))
                current_start = current_end + datetime.timedelta(days=1)
                chunk_num += 1
        else:
            if debug:
                self._print(f"[DataFetcher] Tarih aralığı: {start_dt.strftime('%Y-%m-%d')} - {end_dt.strftime('%Y-%m-%d')} ({total_days} gün)")
            task_queue.put((start_dt, end_dt, max_days, 0, debug, self._print_queue if debug else None))

        # Worker thread'leri başlat (pagination_handler olmadan)
        threads = []
        for _ in range(self.max_workers):
            thread = threading.Thread(
                target=worker_thread,
                args=(
                    task_queue, results_queue, exceptions_list,
                    original_kwargs, date_params, endpoint_callable,
                    self.results_lock, self.exceptions_lock, self.progress_lock,
                    None, None, debug, self._print_queue if debug else None  # progress_bar, pagination_handler, debug, print_queue
                ),
                daemon=True
            )
            thread.start()
            threads.append(thread)

        # Tüm görevlerin tamamlanmasını bekle
        task_queue.join()

        # Thread'leri sonlandır
        for _ in range(self.max_workers):
            task_queue.put(None)

        for thread in threads:
            thread.join(timeout=5)

        # Exception kontrolü
        if exceptions_list:
            raise exceptions_list[0]

        # Sonuçları queue'dan al
        results = []
        while not results_queue.empty():
            try:
                result = results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break

        return merge_results(results)

    def _handle_both(
        self,
        original_kwargs: Dict[str, Any],
        request_model: Any,
        endpoint_callable: Callable,
        first_response: Optional[Dict[str, Any]],
        max_days: int,
        debug: bool = False
    ) -> Any:
        """Hem pagination hem date range için recursive olarak işle"""
        date_params = extract_date_params(original_kwargs, request_model)
        if not date_params:
            return first_response

        start_dt = parse_date_value(date_params['start_value'])
        end_dt = parse_date_value(date_params['end_value'])

        if not start_dt or not end_dt:
            return first_response

        # Queue'lar ve thread-safe listeler oluştur
        task_queue = queue.Queue()
        results_queue = queue.Queue()
        exceptions_list = []

        # Tarih aralığını kontrol et
        total_days = (end_dt - start_dt).days

        if total_days > max_days:
            # Aralığı parçalara böl
            if debug:
                self._print(f"[DataFetcher] Tarih aralığı çok büyük ({total_days} gün), {max_days} günlük parçalara bölünüyor...")
            current_start = start_dt
            chunk_num = 1
            while current_start < end_dt:
                current_end = min(
                    current_start + datetime.timedelta(days=max_days),
                    end_dt
                )
                if debug:
                    self._print(f"[DataFetcher] Parça {chunk_num}: {current_start.strftime('%Y-%m-%d')} - {current_end.strftime('%Y-%m-%d')}")
                task_queue.put((current_start, current_end, max_days, 0, debug, self._print_queue if debug else None))
                current_start = current_end + datetime.timedelta(days=1)
                chunk_num += 1
        else:
            if debug:
                self._print(f"[DataFetcher] Tarih aralığı: {start_dt.strftime('%Y-%m-%d')} - {end_dt.strftime('%Y-%m-%d')} ({total_days} gün)")
            task_queue.put((start_dt, end_dt, max_days, 0, debug, self._print_queue if debug else None))

        # Worker thread'leri başlat (pagination_handler ile)
        threads = []
        for _ in range(self.max_workers):
            thread = threading.Thread(
                target=worker_thread,
                args=(
                    task_queue, results_queue, exceptions_list,
                    original_kwargs, date_params, endpoint_callable,
                    self.results_lock, self.exceptions_lock, self.progress_lock,
                    None, self, debug, self._print_queue if debug else None  # progress_bar, pagination_handler, debug, print_queue
                ),
                daemon=True
            )
            thread.start()
            threads.append(thread)

        # Tüm görevlerin tamamlanmasını bekle
        task_queue.join()

        # Thread'leri sonlandır
        for _ in range(self.max_workers):
            task_queue.put(None)

        for thread in threads:
            thread.join(timeout=5)

        # Exception kontrolü
        if exceptions_list:
            raise exceptions_list[0]

        # Sonuçları queue'dan al
        results = []
        while not results_queue.empty():
            try:
                result = results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break

        return merge_results(results)

    def handle_date_range_error(
        self,
        original_kwargs: Dict[str, Any],
        request_model: Any,
        endpoint_callable: Callable,
        max_days: int = 300,
        debug: bool = False
    ) -> Any:
        """
        Tarih aralığı hatasını handle et - pagination desteği ile

        Args:
            original_kwargs: Orijinal kwargs
            request_model: Request model objesi
            endpoint_callable: Endpoint çağrılabilir fonksiyonu
            max_days: Maksimum gün sayısı
            debug: Debug modu (print ifadelerini gösterir)

        Returns:
            Birleştirilmiş sonuçlar (her tarih aralığı için tüm sayfalar dahil)
        """
        # Debug modunda print queue'yu başlat
        if debug:
            self._start_print_queue()

        try:
            date_params = extract_date_params(original_kwargs, request_model)
            if not date_params:
                return None

            start_dt = parse_date_value(date_params['start_value'])
            end_dt = parse_date_value(date_params['end_value'])

            if not start_dt or not end_dt:
                return None

            # Queue'lar ve thread-safe listeler oluştur
            task_queue = queue.Queue()
            results_queue = queue.Queue()
            exceptions_list = []

            # Tarih aralığını kontrol et
            total_days = (end_dt - start_dt).days

            if total_days > max_days:
                # Aralığı parçalara böl
                current_start = start_dt
                while current_start < end_dt:
                    current_end = min(
                        current_start + datetime.timedelta(days=max_days),
                        end_dt
                    )
                    task_queue.put((current_start, current_end, max_days, 0, debug, self._print_queue if debug else None))
                    current_start = current_end + datetime.timedelta(days=1)
            else:
                task_queue.put((start_dt, end_dt, max_days, 0, debug, self._print_queue if debug else None))

            # Worker thread'leri başlat (pagination_handler ile - her tarih aralığı için sayfaları toplar)
            threads = []
            for _ in range(self.max_workers):
                thread = threading.Thread(
                    target=worker_thread,
                    args=(
                        task_queue, results_queue, exceptions_list,
                        original_kwargs, date_params, endpoint_callable,
                        self.results_lock, self.exceptions_lock, self.progress_lock,
                        None, self, debug, self._print_queue if debug else None  # progress_bar, pagination_handler, debug, print_queue
                    ),
                    daemon=True
                )
                thread.start()
                threads.append(thread)

            # Tüm görevlerin tamamlanmasını bekle
            task_queue.join()

            # Thread'leri sonlandır
            for _ in range(self.max_workers):
                task_queue.put(None)

            for thread in threads:
                thread.join(timeout=5)

            # Exception kontrolü
            if exceptions_list:
                raise exceptions_list[0]

            # Sonuçları queue'dan al
            results = []
            while not results_queue.empty():
                try:
                    result = results_queue.get_nowait()
                    results.append(result)
                except queue.Empty:
                    break

            return merge_results(results)
        finally:
            # Debug modunda print queue'yu durdur ve kalan mesajları yazdır
            if debug:
                if self._print_queue is not None:
                    self._print_queue.join()  # Tüm mesajların yazdırılmasını bekle
                self._stop_print_queue()


__all__ = ['DataFetcher']

