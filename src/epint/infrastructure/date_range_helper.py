# -*- coding: utf-8 -*-

"""
Tarih aralığı hatası için otomatik veri toplama helper fonksiyonları
"""

from typing import Callable, Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
import math
from .exceptions import DateRangeError
from .datetime_utils import DateTimeUtils
from .progress_bar import ProgressBar


def auto_split_date_range(
    endpoint_func: Callable,
    start_param: str = "start",
    end_param: str = "end",
    max_range: Optional[str] = None,
    merge_results: bool = True,
    total_count_service: Optional[Callable] = None,
    _recursion_depth: int = 0,
    _max_recursion_depth: int = 10,
    **kwargs
) -> Any:
    """
    Tarih aralığı hatası olduğunda otomatik olarak tarih aralığını bölerek
    tüm veriyi toplayan wrapper fonksiyon.
    
    Args:
        endpoint_func: Çağrılacak endpoint fonksiyonu
        start_param: Başlangıç tarihi parametre adı (varsayılan: "start")
        end_param: Bitiş tarihi parametre adı (varsayılan: "end")
        max_range: Maksimum tarih aralığı (örn: "1 YEAR", "1 MONTH"). 
                   None ise hata mesajından otomatik algılanır
        merge_results: Sonuçları birleştir (True) veya liste olarak döndür (False)
        total_count_service: Toplam kayıt sayısını almak için kullanılacak servis (opsiyonel)
                          Bazı servislerde (grid, pre-invoice vs) page.total sayfadaki öğe sayısını gösterir,
                          gerçek toplam kayıt sayısı için ayrı bir count servisi gerekir.
        **kwargs: Endpoint fonksiyonuna geçirilecek parametreler
        
    Returns:
        Birleştirilmiş sonuç veya sonuç listesi
        
    Example:
        >>> from epint import auto_split_date_range
        >>> # Normal kullanım
        >>> data = ep.seffaflik_electricity.mcp_data(start='2020-01-01', end='2025-11-27')
        >>> # Otomatik bölme ile kullanım
        >>> data = auto_split_date_range(
        ...     ep.seffaflik_electricity.mcp_data,
        ...     start='2020-01-01',
        ...     end='2025-11-27'
        ... )
        >>> # Total count service ile kullanım (grid servisleri için)
        >>> data = auto_split_date_range(
        ...     ep.grid.meter_query,
        ...     total_count_service=ep.grid.meter_count,
        ...     periodDateStart='2025-11-01T00:00:00+03:00',
        ...     periodDateEnd='2025-11-30T00:00:00+03:00'
        ... )
    """
    start_date_str = kwargs.get(start_param)
    end_date_str = kwargs.get(end_param)
    
    
    if not start_date_str or not end_date_str:
        # Tarih parametreleri yoksa normal çağrı yap
        # Ama sayfalama kontrolü yapılabilir
        result = endpoint_func(**kwargs)
        # Sayfalama kontrolü
        has_page_info = False
        if isinstance(result, dict):
            if "page" in result:
                has_page_info = True
            elif "body" in result and isinstance(result["body"], dict):
                if "content" in result["body"] and isinstance(result["body"]["content"], dict):
                    if "page" in result["body"]["content"]:
                        has_page_info = True
        if has_page_info:
            result = _fetch_all_pages(endpoint_func, result, kwargs, total_count_service=total_count_service)
        return result
    
    # Tarihleri parse et
    try:
        start_date = DateTimeUtils.from_date_string(start_date_str) if isinstance(start_date_str, str) else start_date_str
        end_date = DateTimeUtils.from_date_string(end_date_str) if isinstance(end_date_str, str) else end_date_str
        
        # datetime değilse date'e çevir
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
    except Exception as e:
        # Parse edilemezse normal çağrı yap ama sayfalama kontrolü yapılabilir
        result = endpoint_func(**kwargs)
        # Sayfalama kontrolü
        has_page_info = False
        if isinstance(result, dict):
            if "page" in result:
                has_page_info = True
            elif "body" in result and isinstance(result["body"], dict):
                if "content" in result["body"] and isinstance(result["body"]["content"], dict):
                    if "page" in result["body"]["content"]:
                        has_page_info = True
        if has_page_info:
            result = _fetch_all_pages(endpoint_func, result, kwargs, total_count_service=total_count_service)
        return result
    
    try:
        # İlk deneme - normal çağrı
        result = endpoint_func(**kwargs)
        
        # Sayfalama kontrolü - eğer page bilgisi varsa ve tüm sayfalar alınmamışsa
        # Format 1: result['page'] (seffaflik gibi)
        # Format 2: result['body']['content']['page'] (grid gibi)
        has_page_info = False
        if isinstance(result, dict):
            if "page" in result:
                has_page_info = True
            elif "body" in result and isinstance(result["body"], dict):
                if "content" in result["body"] and isinstance(result["body"]["content"], dict):
                    if "page" in result["body"]["content"]:
                        has_page_info = True
        
        if has_page_info:
            result = _fetch_all_pages(endpoint_func, result, kwargs, total_count_service=total_count_service)
        
        return result
    except Exception as e:
        # DateRangeError kontrolü
        error_msg = str(e).lower()
        is_date_range_error = (
            isinstance(e, DateRangeError) or
            ("tarih" in error_msg and "aralık" in error_msg and 
             ("month" in error_msg or "year" in error_msg or "week" in error_msg or "day" in error_msg))
        )
        
        if is_date_range_error:
            # max_range'i exception'dan al veya hata mesajından parse et
            error_msg_full = str(e)
            detected_max_range = max_range
            
            # Önce exception'dan al
            if hasattr(e, 'max_range') and e.max_range:
                detected_max_range = e.max_range
            
            # Hata mesajından parse et: "(\d+ MONTH)" formatını ara
            if not detected_max_range:
                general_match = re.search(r'\((\d+\s*(?:MONTH|YEAR|WEEK|DAY))\)', error_msg_full, re.IGNORECASE)
                if general_match:
                    detected_max_range = general_match.group(1).upper()
            
            if not detected_max_range:
                raise
            
            # Tarih aralığını böl
            date_ranges = _split_date_range(start_date, end_date, detected_max_range)
            
            # Progress bar başlat (sadece en üst seviyede)
            progress = None
            if _recursion_depth == 0:
                progress = ProgressBar(total=len(date_ranges), desc="📊 Tarih aralığı otomatik bölünüyor")
            
            # Her aralık için veri topla
            results = []
            for idx, (range_start, range_end) in enumerate(date_ranges):
                if progress:
                    progress.set_description(f"📊 Tarih aralığı {idx+1}/{len(date_ranges)} işleniyor ({range_start} - {range_end})")
                
                new_kwargs = kwargs.copy()
                new_kwargs[start_param] = range_start.isoformat()
                new_kwargs[end_param] = range_end.isoformat()
                
                # Recursive çağrı veya direkt çağrı
                if _recursion_depth >= _max_recursion_depth:
                    result = endpoint_func(**new_kwargs)
                    # Sayfalama kontrolü
                    if isinstance(result, dict) and "page" in result:
                        result = _fetch_all_pages(endpoint_func, result, new_kwargs, total_count_service=total_count_service)
                    results.append(result)
                else:
                    try:
                        result = auto_split_date_range(
                            endpoint_func,
                            start_param=start_param,
                            end_param=end_param,
                            max_range=detected_max_range,
                            merge_results=False,
                            total_count_service=total_count_service,
                            _recursion_depth=_recursion_depth + 1,
                            _max_recursion_depth=_max_recursion_depth,
                            **new_kwargs
                        )
                        # Sayfalama kontrolü (recursive çağrı sonucu için)
                        if isinstance(result, dict) and "page" in result:
                            result = _fetch_all_pages(endpoint_func, result, new_kwargs, total_count_service=total_count_service)
                        results.append(result)
                    except DateRangeError:
                        # Hala hata varsa, direkt çağrı yap
                        result = endpoint_func(**new_kwargs)
                        # Sayfalama kontrolü
                        if isinstance(result, dict) and "page" in result:
                            result = _fetch_all_pages(endpoint_func, result, new_kwargs, total_count_service=total_count_service)
                        results.append(result)
                
                # Progress güncelle
                if progress:
                    progress.update(1)
            
            # Progress bar'ı kapat
            if progress:
                progress.close()
            
            # Sonuçları birleştir
            if merge_results:
                return _merge_results(results)
            else:
                return results
        else:
            # DateRangeError değilse, diğer hatalar için normal exception fırlat
            raise


def _split_date_range(
    start_date: Any,
    end_date: Any,
    max_range: str
) -> List[Tuple[Any, Any]]:
    """
    Tarih aralığını maksimum aralığa göre böler
    
    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
        max_range: Maksimum aralık ("1 YEAR", "1 MONTH", "1 WEEK", "1 DAY")
        
    Returns:
        Tarih aralıkları listesi [(start, end), ...]
    """
    ranges = []
    current_start = start_date
    
    # Maksimum aralığı timedelta'ya çevir
    max_delta = _parse_max_range(max_range)
    
    while current_start < end_date:
        current_end = min(current_start + max_delta, end_date)
        ranges.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)  # Bir sonraki gün başla
    
    return ranges


def _parse_max_range(max_range: str) -> timedelta:
    """
    Maksimum aralık string'ini timedelta'ya çevirir
    
    Args:
        max_range: "1 YEAR", "1 MONTH", "1 WEEK", "1 DAY"
        
    Returns:
        timedelta objesi
    """
    max_range_upper = max_range.upper().strip()
    
    if "YEAR" in max_range_upper:
        # 1 yıl = 365 gün (yaklaşık)
        return timedelta(days=365)
    elif "MONTH" in max_range_upper:
        # Ay sayısını parse et (örn: "3 MONTH" -> 3)
        month_match = re.search(r'(\d+)\s*MONTH', max_range_upper)
        if month_match:
            months = int(month_match.group(1))
        else:
            months = 1
        # Ay başına 30 gün (yaklaşık)
        return timedelta(days=30 * months)
    elif "WEEK" in max_range_upper:
        # 1 hafta = 7 gün
        return timedelta(days=7)
    elif "DAY" in max_range_upper:
        # 1 gün
        return timedelta(days=1)
    else:
        # Varsayılan: 1 yıl
        return timedelta(days=365)


def _merge_results(results: List[Any]) -> Any:
    """
    Birden fazla sonucu birleştirir
    
    Args:
        results: Sonuç listesi
        
    Returns:
        Birleştirilmiş sonuç
    """
    if not results:
        return None
    
    if len(results) == 1:
        return results[0]
    
    # İlk sonucun yapısına göre birleştir
    first_result = results[0]
    
    if isinstance(first_result, dict):
        # Dict ise items/liste alanlarını birleştir
        merged = {}
        
        # Tüm key'leri topla
        all_keys = set()
        for result in results:
            if isinstance(result, dict):
                all_keys.update(result.keys())
        
        # Her key için birleştirme yap
        for key in all_keys:
            values = [r.get(key) for r in results if isinstance(r, dict) and key in r]
            
            if not values:
                continue
            
            # None değerleri filtrele
            values = [v for v in values if v is not None]
            
            if not values:
                merged[key] = None
            elif isinstance(values[0], list):
                # Liste ise birleştir
                merged_list = []
                for v in values:
                    if isinstance(v, list):
                        merged_list.extend(v)
                    else:
                        merged_list.append(v)
                merged[key] = merged_list
            elif isinstance(values[0], dict):
                # Dict ise recursive merge (basit versiyon)
                # Genelde page bilgisi gibi nested dict'ler için
                if key == "page":
                    # Page bilgisini birleştir: total ve size korunur, number son sayfadan alınır
                    merged_page = values[-1].copy()
                    # Toplam item sayısını hesapla (tüm sayfalardan)
                    if "total" in merged_page:
                        # total zaten toplam item sayısını gösteriyor, koru
                        pass
                    # number'ı son sayfadan al
                    if "number" in merged_page:
                        merged_page["number"] = values[-1].get("number", 1)
                    merged[key] = merged_page
                else:
                    # Diğer dict'ler için birleştirme
                    merged[key] = values[-1]  # Son değeri kullan
            else:
                # Diğer tipler için son değeri kullan
                merged[key] = values[-1]
        
        return merged
    elif isinstance(first_result, list):
        # Liste ise birleştir
        merged_list = []
        for result in results:
            if isinstance(result, list):
                merged_list.extend(result)
            else:
                merged_list.append(result)
        return merged_list
    else:
        # Diğer tipler için liste olarak döndür
        return results


def _fetch_all_pages(
    endpoint_func: Callable,
    first_result: Dict[str, Any],
    base_kwargs: Dict[str, Any],
    total_count_service: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Sayfalama varsa tüm sayfaları tarar ve birleştirir
    
    Args:
        endpoint_func: Endpoint fonksiyonu
        first_result: İlk sayfa sonucu
        base_kwargs: Temel parametreler
        total_count_service: Toplam kayıt sayısını almak için kullanılacak servis (opsiyonel)
        
    Returns:
        Tüm sayfalar birleştirilmiş sonuç
    """
    # Farklı response formatlarını destekle
    # Format 1: result['page'] (seffaflik gibi)
    # Format 2: result['body']['content']['page'] (grid gibi)
    page_info = first_result.get("page")
    content = None
    
    if not isinstance(page_info, dict):
        # Grid formatını kontrol et: body.content.page
        if "body" in first_result and isinstance(first_result["body"], dict):
            if "content" in first_result["body"] and isinstance(first_result["body"]["content"], dict):
                content = first_result["body"]["content"]
                page_info = content.get("page")
    
    if not isinstance(page_info, dict):
        # Sayfalama bilgisi yoksa direkt döndür
        return first_result
    
    current_page = page_info.get("number", 1)
    page_size = page_info.get("size", 20)
    total_items = page_info.get("total", 0)
    
    # Eğer total_count_service verilmişse, gerçek toplam kayıt sayısını al
    if total_count_service is not None:
        try:
            # page parametrelerini temizle (count servisi için gerekli değil)
            count_kwargs = base_kwargs.copy()
            
            # page parametrelerini kaldır (count servisi için gerekli değil)
            if "page" in count_kwargs:
                del count_kwargs["page"]
            if "pageNumber" in count_kwargs:
                del count_kwargs["pageNumber"]
            if "pageInfo" in count_kwargs:
                # pageInfo içindeki sayfalama parametrelerini kaldır
                if isinstance(count_kwargs["pageInfo"], dict):
                    page_info_copy = count_kwargs["pageInfo"].copy()
                    # Sayfalama ile ilgili parametreleri kaldır
                    for key in ["page", "number", "size", "total", "sort"]:
                        if key in page_info_copy:
                            del page_info_copy[key]
                    # Eğer pageInfo boş kaldıysa tamamen kaldır
                    if not page_info_copy:
                        del count_kwargs["pageInfo"]
                    else:
                        count_kwargs["pageInfo"] = page_info_copy
                else:
                    del count_kwargs["pageInfo"]
            
            # Count servisini çağır
            count_result = total_count_service(**count_kwargs)
            
            # Count sonucundan toplam kayıt sayısını al
            # Farklı response formatları için kontrol et
            if isinstance(count_result, dict):
                # body.content.count formatı (grid servisleri için)
                if "body" in count_result and isinstance(count_result["body"], dict):
                    if "content" in count_result["body"] and isinstance(count_result["body"]["content"], dict):
                        if "count" in count_result["body"]["content"]:
                            total_items = int(count_result["body"]["content"]["count"])
                        elif "total" in count_result["body"]["content"]:
                            total_items = int(count_result["body"]["content"]["total"])
                    elif "count" in count_result["body"]:
                        total_items = int(count_result["body"]["count"])
                # Direkt content.count formatı
                elif "content" in count_result and isinstance(count_result["content"], dict):
                    if "count" in count_result["content"]:
                        total_items = int(count_result["content"]["count"])
                    elif "total" in count_result["content"]:
                        total_items = int(count_result["content"]["total"])
                # Direkt count formatı
                elif "count" in count_result:
                    total_items = int(count_result["count"])
                elif "total" in count_result:
                    total_items = int(count_result["total"])
        except Exception as e:
            # Count servisi başarısız olursa, mevcut total'i kullan
            import sys
            print(f"WARNING: Count servisi hatası: {e}", file=sys.stderr)
            pass
    
    # Toplam sayfa sayısını hesapla
    if total_items <= 0 or page_size <= 0:
        return first_result
    
    total_pages = math.ceil(total_items / page_size)
    
    # Eğer tek sayfa varsa direkt döndür
    if total_pages <= 1:
        return first_result
    
    # Progress bar oluştur
    progress = ProgressBar(
        total=total_pages,
        desc=f"📄 Sayfalar çekiliyor (Toplam {total_items} kayıt, {total_pages} sayfa)"
    )
    
    # İlk sayfa zaten alındı
    progress.update(1)
    
    # Tüm sayfaları topla
    all_results = [first_result]
    
    # Sayfa parametrelerini bul (page, pageNumber, pageInfo.page, vb.)
    page_param = None
    
    # Olası parametre isimlerini kontrol et
    possible_page_params = ["page", "pageNumber"]
    
    for param in possible_page_params:
        if param in base_kwargs:
            page_param = param
            break
    
    # Eğer page parametresi yoksa, pageInfo.page formatını kontrol et
    if not page_param and "pageInfo" in base_kwargs:
        if isinstance(base_kwargs["pageInfo"], dict):
            page_param = "pageInfo"
    
    # Diğer sayfaları al
    for page_num in range(2, total_pages + 1):
        # Progress bar güncelle
        progress.set_description(f"📄 Sayfa {page_num}/{total_pages} çekiliyor...")
        page_kwargs = base_kwargs.copy()
        
        if page_param == "pageInfo" and isinstance(page_kwargs.get("pageInfo"), dict):
            # pageInfo.page formatı
            page_kwargs["pageInfo"]["page"] = page_num
        elif page_param == "page" and isinstance(page_kwargs.get("page"), dict):
            # page dict formatı: {"number": 1, "size": 10, ...}
            page_kwargs["page"] = page_kwargs["page"].copy()
            page_kwargs["page"]["number"] = page_num
        elif page_param:
            # Direkt page parametresi (sayı olarak)
            page_kwargs[page_param] = page_num
        else:
            # Parametre bulunamadı, page dict formatını dene
            if "page" not in page_kwargs:
                # İlk sayfadan page yapısını kopyala
                if isinstance(first_result, dict):
                    first_page = first_result.get("page")
                    if isinstance(first_page, dict):
                        page_kwargs["page"] = first_page.copy()
                        page_kwargs["page"]["number"] = page_num
                    else:
                        # Grid formatı: body.content.page
                        if "body" in first_result and isinstance(first_result["body"], dict):
                            if "content" in first_result["body"] and isinstance(first_result["body"]["content"], dict):
                                first_page = first_result["body"]["content"].get("page")
                                if isinstance(first_page, dict):
                                    page_kwargs["page"] = first_page.copy()
                                    page_kwargs["page"]["number"] = page_num
            elif isinstance(page_kwargs.get("page"), dict):
                # page zaten dict formatında, sadece number'ı güncelle
                page_kwargs["page"] = page_kwargs["page"].copy()
                page_kwargs["page"]["number"] = page_num
            else:
                # pageInfo.page formatını dene
                if "pageInfo" not in page_kwargs:
                    page_kwargs["pageInfo"] = {}
                if isinstance(page_kwargs["pageInfo"], dict):
                    page_kwargs["pageInfo"]["page"] = page_num
                else:
                    # pageInfo dict değilse, direkt page parametresi ekle
                    page_kwargs["page"] = page_num
        
        try:
            page_result = endpoint_func(**page_kwargs)
            if isinstance(page_result, dict):
                all_results.append(page_result)
                # Progress bar güncelle
                progress.update(1)
        except Exception:
            # Sayfa alınamazsa devam et
            progress.close()
            break
    
    # Progress bar'ı kapat
    progress.close()
    
    # Tüm sayfaları birleştir
    merged_result = _merge_results(all_results)
    
    # Eğer grid formatındaysa (body.content.items), items'ı birleştir
    if isinstance(merged_result, dict) and "body" in merged_result:
        if isinstance(merged_result["body"], dict) and "content" in merged_result["body"]:
            if isinstance(merged_result["body"]["content"], dict) and "items" in merged_result["body"]["content"]:
                # Tüm sayfalardan items'ı topla
                all_items = []
                for result in all_results:
                    if isinstance(result, dict) and "body" in result:
                        if isinstance(result["body"], dict) and "content" in result["body"]:
                            if isinstance(result["body"]["content"], dict) and "items" in result["body"]["content"]:
                                items = result["body"]["content"]["items"]
                                if isinstance(items, list):
                                    all_items.extend(items)
                
                # Birleştirilmiş items'ı yerleştir
                merged_result["body"]["content"]["items"] = all_items
                
                # Page bilgisini güncelle
                if "page" in merged_result["body"]["content"]:
                    merged_result["body"]["content"]["page"]["total"] = len(all_items)
                    merged_result["body"]["content"]["page"]["number"] = total_pages
    
    return merged_result


def with_auto_date_range_split(
    start_param: str = "start",
    end_param: str = "end",
    max_range: Optional[str] = None,
    total_count_service: Optional[Callable] = None
):
    """
    Decorator: Endpoint fonksiyonunu otomatik tarih aralığı bölme ile sarmalar
    
    Args:
        start_param: Başlangıç tarihi parametre adı
        end_param: Bitiş tarihi parametre adı
        max_range: Maksimum tarih aralığı
        total_count_service: Toplam kayıt sayısını almak için kullanılacak servis (opsiyonel)
                          Bazı servislerde (grid, pre-invoice vs) page.total sayfadaki öğe sayısını gösterir,
                          gerçek toplam kayıt sayısı için ayrı bir count servisi gerekir.
        
    Example:
        >>> @with_auto_date_range_split()
        >>> def my_endpoint(**kwargs):
        ...     return ep.seffaflik_electricity.mcp_data(**kwargs)
        
        >>> # Total count service ile kullanım
        >>> @with_auto_date_range_split(total_count_service=ep.grid.meter_count)
        >>> def get_meters(**kwargs):
        ...     return ep.grid.meter_query(**kwargs)
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(**kwargs):
            return auto_split_date_range(
                func,
                start_param=start_param,
                end_param=end_param,
                max_range=max_range,
                total_count_service=total_count_service,
                **kwargs
            )
        return wrapper
    return decorator

