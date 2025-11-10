# -*- coding: utf-8 -*-

__version__ = "0.1.0"
__author__ = "metehanboy"
__email__ = "m3t3-han@hotmail.com"
__description__ = "EPIAS API Integration Package for Turkish Energy Market"

import os
import difflib
import re
import unicodedata
import yaml
import time
from .infrastructure.endpoint_manager import EndpointManager
from .resources import get_resources_dir
from .infrastructure.logger import (
    get_logger,
    performance_timer,
    log_operation,
    log_performance,
    log_error,
)


class AuthenticationError(Exception):

    def __init__(
        self,
        message="Kullanmadan önce set_auth(username, password) ile kimlik bilgilerinizi tanımlamanız gerekiyor.",
    ):
        self.message = message
        super().__init__(self.message)


_endpoint_search_index = {}
_endpoint_cache = {}
_endpoint_categories = {}
_endpoint_data = {}  # endpoint_name -> endpoint_data mapping
_normalized_index = {}  # Normalize edilmiş isimler için indeks
_keyword_index = {}  # Kelime bazlı indeks
_INITIALIZED = False

_username = None
_password = None
_auth_configured = False
_current_mode = "prod"  # Default prod mode

# Yaygın kısaltmalar ve alias'lar
_ALIASES = {
    # EPİAŞ kısaltmaları
    'smf': 'smp_average',
    'smp': 'smp_average',
    'aof': 'aof_average',
    'mcp': 'mcp_average',
    'dgp': 'dgp',
    'gop': 'gop',
    'gip': 'gip',
    'vep': 'vep',
    'yekg': 'yekg',
    'prices': 'daily_prices',
    'fiyat': 'prices',
    'fiyatlar': 'prices',
    # Türkçe kelimeler
    'günlük': 'daily',
    'gunluk': 'daily',
    'haftalık': 'weekly',
    'haftalik': 'weekly',
    'aylık': 'monthly',
    'aylik': 'monthly',
    'yıllık': 'yearly',
    'yillik': 'yearly',
    'rapor': 'report',
    'liste': 'list',
    'sorgu': 'query',
    'sorgula': 'query',
}


def normalize_search_term(name):
    """Arama terimini normalize et (Türkçe karakter, tire, underscore)"""
    if not isinstance(name, str):
        return str(name).lower()
    
    # Türkçe karakterleri normalize et
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    
    # Küçük harfe çevir
    name = name.lower()
    
    # Tire ve boşlukları underscore'a çevir
    name = name.replace('-', '_').replace(' ', '_')
    
    # Çoklu underscore'ları tek yap
    while '__' in name:
        name = name.replace('__', '_')
    
    # Başta/sonda underscore varsa temizle
    name = name.strip('_')
    
    return name


def _build_search_indexes():
    """Arama indekslerini oluştur (normalized, keyword)"""
    global _normalized_index, _keyword_index
    
    _normalized_index.clear()
    _keyword_index.clear()
    
    for endpoint_key in _endpoint_search_index.keys():
        # Normalized index
        normalized = normalize_search_term(endpoint_key)
        if normalized and normalized != endpoint_key:
            _normalized_index[normalized] = endpoint_key
        
        # Keyword index - her kelime için mapping
        words = endpoint_key.lower().replace('-', '_').split('_')
        for word in words:
            if len(word) > 2:  # 2 karakterden uzun kelimeler
                if word not in _keyword_index:
                    _keyword_index[word] = []
                if endpoint_key not in _keyword_index[word]:
                    _keyword_index[word].append(endpoint_key)


def _apply_aliases(name):
    """Alias'ları uygula"""
    name_lower = name.lower()
    
    # Tam eşleşme
    if name_lower in _ALIASES:
        return _ALIASES[name_lower]
    
    # Kısmi eşleşme - alias'ı kelime olarak ara
    words = name_lower.split('_')
    new_words = []
    for word in words:
        if word in _ALIASES:
            new_words.append(_ALIASES[word])
        else:
            new_words.append(word)
    
    result = '_'.join(new_words)
    return result if result != name_lower else name


def _keyword_search(name, max_results=10):
    """Kelime bazlı arama"""
    name_lower = name.lower().replace('-', '_')
    words = [w for w in name_lower.split('_') if len(w) > 2]
    
    if not words:
        return []
    
    # Her kelime için endpoint'leri bul
    candidates = {}
    for word in words:
        if word in _keyword_index:
            for endpoint_key in _keyword_index[word]:
                if endpoint_key not in candidates:
                    candidates[endpoint_key] = 0
                candidates[endpoint_key] += 1
    
    # En çok eşleşen kelimeye sahip endpoint'leri döndür
    if not candidates:
        return []
    
    # Sırala ve en iyi sonuçları döndür
    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    
    # En az %50 kelime eşleşmesi olmalı
    min_matches = max(1, len(words) * 0.5)
    results = [k for k, v in sorted_candidates if v >= min_matches]
    
    return results[:max_results]


def _get_smart_suggestions(name, limit=10):
    """Akıllı öneriler"""
    suggestions = []
    
    # 1. Normalized arama
    normalized = normalize_search_term(name)
    if normalized in _normalized_index:
        suggestions.append(_normalized_index[normalized])
    
    # 2. Keyword arama
    keyword_results = _keyword_search(name, max_results=5)
    suggestions.extend(keyword_results)
    
    # 3. Fuzzy search (düşük threshold)
    name_lower = name.lower()
    fuzzy_results = []
    for search_key in list(_endpoint_search_index.keys())[:100]:
        score = difflib.SequenceMatcher(None, name_lower, search_key.lower()).ratio()
        if score > 0.4:
            fuzzy_results.append((search_key, score))
    
    fuzzy_results.sort(key=lambda x: x[1], reverse=True)
    suggestions.extend([k for k, s in fuzzy_results[:5]])
    
    # Duplicate'leri temizle, sırayı koru
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique_suggestions.append(s)
    
    return unique_suggestions[:limit]


def _load_all_endpoints():
    global _INITIALIZED
    if _INITIALIZED:
        return

    start_time = time.time()
    log_operation("_load_all_endpoints_start")

    try:
        _load_endpoints_from_directory()
        
        # Arama indekslerini oluştur
        _build_search_indexes()
        
        _INITIALIZED = True

        duration = time.time() - start_time
        log_performance(
            "_load_all_endpoints", duration, endpoint_count=len(_endpoint_search_index)
        )
        log_operation(
            "_load_all_endpoints_complete", 
            endpoint_count=len(_endpoint_search_index),
            normalized_count=len(_normalized_index),
            keyword_count=len(_keyword_index)
        )

    except Exception as e:
        duration = time.time() - start_time
        log_error("_load_all_endpoints_error", error_msg=str(e), duration=duration)
        print(f"Uyarı: Endpoint'ler yüklenirken hata oluştu: {str(e)}")
        pass


def set_auth(username, password):
    global _username, _password, _auth_configured, _endpoint_cache

    if not username or not password:
        raise ValueError("Username ve password boş olamaz")

    # Eğer kullanıcı değişiyorsa cache'i temizle
    if _username != username or _password != password:
        _endpoint_cache.clear()
        log_operation(
            "auth_changed_cache_cleared",
            old_user=_username,
            new_user=username,
            cache_cleared=True,
        )

    _username = username
    _password = password
    _auth_configured = True
    print("Kimlik bilgileri başarıyla ayarlandı")


def set_mode(mode: str) -> None:
    """Test veya prod modunu ayarla

    Args:
        mode: 'test' veya 'prod'
    """
    global _current_mode
    if mode.lower() in ["test", "prod"]:
        _current_mode = mode.lower()
        get_logger().log_operation("mode_changed", mode=_current_mode)
        print(f"🔧 Mode değiştirildi: {_current_mode.upper()}")
    else:
        raise ValueError("Mode 'test' veya 'prod' olmalıdır")


def get_current_mode() -> str:
    """Mevcut modu döndür"""
    return _current_mode


def clear_cache():
    endpoints_dir = get_resources_dir()
    cache_file = os.path.join(endpoints_dir, ".endpoint_cache.json")

    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("Cache dosyası temizlendi")
    else:
        print("Cache dosyası bulunamadı")


def _load_endpoints_from_directory():
    endpoints_dir = get_resources_dir()

    if not os.path.exists(endpoints_dir):
        return

    cache_file = os.path.join(endpoints_dir, ".endpoint_cache.json")

    if _try_load_from_cache(cache_file):
        return

    _load_from_yaml_files(endpoints_dir)

    _save_to_cache(cache_file)


def _try_load_from_cache(cache_file):
    if not os.path.exists(cache_file):
        return False

    try:
        import json
        import time

        cache_age_days = (time.time() - os.path.getmtime(cache_file)) / (24 * 60 * 60)
        CACHE_EXPIRE_DAYS = 30

        if cache_age_days < CACHE_EXPIRE_DAYS:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            global _endpoint_search_index, _endpoint_categories, _endpoint_data
            _endpoint_search_index = cache_data.get("search_index", {})
            _endpoint_categories = cache_data.get("categories", {})
            
            # _endpoint_data'yı _endpoint_categories'den oluştur
            _endpoint_data.clear()
            for category_name, endpoints in _endpoint_categories.items():
                for endpoint_name, endpoint_info in endpoints.items():
                    endpoint_data = endpoint_info.get("data", {})
                    if isinstance(endpoint_data, dict):
                        endpoint_data_with_category = endpoint_data.copy()
                        endpoint_data_with_category['category'] = category_name
                        _endpoint_data[endpoint_name] = endpoint_data_with_category
            
            print(f"Cache dosyası yüklendi (yaş: {cache_age_days:.1f} gün)")
            return True
        else:
            print(
                f"Cache dosyası eski (yaş: {cache_age_days:.1f} gün), yeniden oluşturuluyor..."
            )
            os.remove(cache_file)
            return False
    except Exception:
        print("Cache dosyası okunamadı")
        return False


def _load_from_yaml_files(endpoints_dir):
    start_time = time.time()
    log_operation("_load_from_yaml_files_start", directory=endpoints_dir)
    print("YAML dosyaları işleniyor...")

    yaml_files = _find_yaml_files(endpoints_dir)
    log_operation("_load_from_yaml_files_found", file_count=len(yaml_files))

    for yaml_path in yaml_files:
        _process_yaml_file(yaml_path)

    duration = time.time() - start_time
    log_performance("_load_from_yaml_files", duration, file_count=len(yaml_files))


def _save_to_cache(cache_file):
    try:
        import json
        import time

        cache_data = {
            "search_index": _endpoint_search_index,
            "categories": _endpoint_categories,
            "created_at": time.time(),
            "expire_days": 30,
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"Cache dosyası oluşturuldu: {len(_endpoint_search_index)} endpoint")
    except Exception:
        print("Cache dosyası yazılamadı")


def _find_yaml_files(endpoints_dir):
    yaml_files = []
    for root, _, files in os.walk(endpoints_dir):
        for file in files:
            if (
                file.endswith(".yaml") or file.endswith(".yml")
            ) and "service-params" not in file:
                yaml_files.append(os.path.join(root, file))
    return yaml_files


def _extract_category_from_path(yaml_path):
    path_parts = yaml_path.split(os.sep)
    endpoints_idx = -1
    for i, part in enumerate(path_parts):
        if part == "endpoints":
            endpoints_idx = i
            break

    if endpoints_idx >= 0 and endpoints_idx + 1 < len(path_parts):
        return path_parts[endpoints_idx + 1]
    return ""


def _process_yaml_file(yaml_path):
    start_time = time.time()

    try:
        import yaml

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not data or not isinstance(data, dict):
                return

            category_name = _extract_category_from_path(yaml_path)

            _process_endpoints_from_data(data, category_name)

            duration = time.time() - start_time
            log_performance(
                "_process_yaml_file", duration, file=yaml_path, category=category_name
            )

    except Exception as e:
        duration = time.time() - start_time
        log_error(
            "_process_yaml_file_error",
            file=yaml_path,
            error_msg=str(e),
            duration=duration,
        )
        print(f"YAML dosyası işlenemedi {yaml_path}")


def _process_endpoints_from_data(data, category_name):
    if "endpoints" in data and isinstance(data["endpoints"], dict):
        _process_endpoints(data["endpoints"], category_name)

    for key, value in data.items():
        if key != "endpoints" and isinstance(value, dict) and "endpoint" in value:
            _process_endpoints({key: value}, category_name)


def _process_yaml_file_fast(yaml_path):
    try:
        import yaml

        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()

            import re

            endpoints_match = re.search(
                r"endpoints:\s*\n(.*?)(?=\n\w+:|$)", content, re.DOTALL
            )
            if not endpoints_match:
                return

            endpoints_content = "endpoints:\n" + endpoints_match.group(1)

            data = yaml.safe_load(endpoints_content)
            if not data or not isinstance(data, dict) or "endpoints" not in data:
                return

            category_name = _extract_category_from_path(yaml_path)
            _process_endpoints(data["endpoints"], category_name)

    except Exception:
        _process_yaml_file(yaml_path)


def _process_endpoints(endpoints, category_name=""):
    for endpoint_name, endpoint_data in endpoints.items():
        if not isinstance(endpoint_data, dict):
            continue

        _endpoint_search_index[endpoint_name] = endpoint_name
        
        # Endpoint data'yı kategorisi ile birlikte sakla
        global _endpoint_data
        endpoint_data_with_category = endpoint_data.copy()
        endpoint_data_with_category['category'] = category_name
        _endpoint_data[endpoint_name] = endpoint_data_with_category

        global _endpoint_categories
        if category_name not in _endpoint_categories:
            _endpoint_categories[category_name] = {}
        _endpoint_categories[category_name][endpoint_name] = {
            "file_path": "",  # Bu daha sonra set edilecek
            "data": endpoint_data,
        }

        sanitized_name = _sanitize_endpoint_name(endpoint_data)
        if sanitized_name and sanitized_name != endpoint_name:
            _endpoint_search_index[sanitized_name] = endpoint_name

        _create_search_keys(endpoint_name, endpoint_data)


def sanitize(text, **kwargs):
    __converter = r"\W*:,\_:,\-:,I:i,İ:i,ı:i,Ş:s,ş:s,Ö:o,ö:o,Ğ:g,ğ:g,Ü:u,ü:u,Ç:c,ç:c"

    cleanspace = kwargs.get("cleanspace", True)
    if not cleanspace:
        __converter = r"\_:,\-:,I:i,İ:i,ı:i,Ş:s,ş:s,Ö:o,ö:o,Ğ:g,ğ:g,Ü:u,ü:u,Ç:c,ç:c,[^a-zA-Z0-9\s]:"

    __converter = __converter.split(",")

    if text is None or text == "":
        return None
    encoded = (
        unicodedata.normalize("NFKD", text)
        .encode("utf-8", "ignore")
        .decode("utf-8", "ignore")
    )
    for sub in __converter:
        compiled = re.compile(sub.split(":")[0], re.IGNORECASE | re.DOTALL)
        encoded = re.sub(compiled, sub.split(":")[1], encoded)

    encoded = encoded.lower()
    if not cleanspace:
        encoded = re.sub(r"\s{2,}", " ", encoded).strip()
    return encoded


def _sanitize_endpoint_name(endpoint_data):
    name_sources = [
        endpoint_data.get("short_name", ""),
        endpoint_data.get("short_name_tr", ""),
        endpoint_data.get("summary", ""),
        endpoint_data.get("description", ""),
    ]

    for name in name_sources:
        if name and isinstance(name, str):
            sanitized = sanitize(name, cleanspace=True)
            if sanitized:
                sanitized = re.sub(r"\s+", "_", sanitized.strip())
                return sanitized

    return ""


def _create_search_keys(endpoint_name, endpoint_data):
    search_fields = [
        endpoint_data.get("short_name", ""),
        endpoint_data.get("short_name_tr", ""),
        endpoint_data.get("summary", ""),
        endpoint_data.get("description", ""),
    ]

    for field_value in search_fields:
        if field_value and isinstance(field_value, str):
            sanitized_field = sanitize(field_value, cleanspace=True)
            if sanitized_field:
                sanitized_field = re.sub(r"\s+", "_", sanitized_field.strip())

                if (
                    sanitized_field != endpoint_name
                    and sanitized_field not in _endpoint_search_index
                ):
                    _endpoint_search_index[sanitized_field] = endpoint_name


def _get_endpoint(endpoint_key):
    if endpoint_key in _endpoint_cache:
        return _endpoint_cache[endpoint_key]

    # Endpoint'i kategorilerden bul - dolu olan endpoint'i tercih et
    endpoint_data = None
    category = ""
    fallback_data = None
    fallback_category = ""

    for cat_name, endpoints in _endpoint_categories.items():
        if endpoint_key in endpoints:
            candidate_data = endpoints[endpoint_key]["data"]
            # Eğer var_type veya params dolu ise bunu tercih et
            if candidate_data.get("var_type") or candidate_data.get("params"):
                endpoint_data = candidate_data
                category = cat_name
                break  # Dolu olanı bulduğumuzda dur
            elif not fallback_data:  # Boş olanı fallback olarak sakla
                fallback_data = candidate_data
                fallback_category = cat_name

    # Eğer dolu olan bulunamadıysa fallback'i kullan
    if not endpoint_data and fallback_data:
        endpoint_data = fallback_data
        category = fallback_category

    if not endpoint_data:
        # Fallback: YAML'dan yükle
        endpoint_data = _load_endpoint_from_yaml(endpoint_key)
        if endpoint_data:
            category = ""

    if endpoint_data:
        username = _username or ""
        password = _password or ""
        current_mode = _current_mode

        manager = EndpointManager(
            endpoint_key,
            endpoint_data,
            username=username,
            password=password,
            category=category,
            mode=current_mode,
        )
        _endpoint_cache[endpoint_key] = manager
        return manager

    return None


def _load_endpoint_from_yaml(endpoint_key):
    endpoints_dir = get_resources_dir()
    yaml_files = _find_yaml_files(endpoints_dir)

    for yaml_path in yaml_files:
        endpoint_data = _search_endpoint_in_yaml_file(yaml_path, endpoint_key)
        if endpoint_data:
            return endpoint_data

    return None


def _search_endpoint_in_yaml_file(yaml_path, endpoint_key):
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

            if "endpoints" in data:
                endpoints = data["endpoints"]
                if endpoint_key in endpoints:
                    return endpoints[endpoint_key]

            if (
                endpoint_key in data
                and isinstance(data[endpoint_key], dict)
                and "endpoint" in data[endpoint_key]
            ):
                return data[endpoint_key]

    except Exception:
        pass

    return None


def __dir__():
    if not _INITIALIZED:
        _load_all_endpoints()

    return sorted(_endpoint_search_index.keys()) if _endpoint_search_index else []


def _handle_direct_match(name, start_time):
    """Direct match işlemini yönet"""
    duration = time.time() - start_time
    log_performance(
        "__getattr___direct_match",
        duration,
        endpoint=name,
        match_type="direct",
    )
    return _get_endpoint(_endpoint_search_index[name])


def _handle_fuzzy_match(name, start_time):
    """Fuzzy match işlemini yönet"""
    best_match = _fuzzy_search(name)
    if best_match:
        duration = time.time() - start_time
        log_performance(
            "__getattr__fuzzy_match",
            duration,
            endpoint=name,
            match_type="fuzzy",
            matched=best_match,
        )
        return best_match
    return None


def _handle_no_match(name, start_time):
    """No match durumunu yönet"""
    duration = time.time() - start_time
    available = list(_endpoint_search_index.keys())[:10]
    log_performance(
        "__getattr__no_match",
        duration,
        endpoint=name,
        match_type="none",
        available_count=len(available),
    )
    raise AttributeError(f"'{name}' endpoint bulunamadı. Mevcut: {available}")


def _handle_enhanced_no_match(name, start_time):
    """Gelişmiş hata mesajı ile no match durumunu yönet"""
    duration = time.time() - start_time
    
    # Akıllı öneriler al
    suggestions = _get_smart_suggestions(name, limit=5)
    
    log_performance(
        "__getattr__enhanced_no_match",
        duration,
        endpoint=name,
        match_type="none",
        suggestion_count=len(suggestions),
    )
    
    # Hata mesajı
    error_msg = f"\n{'='*80}\n"
    error_msg += f"❌ '{name}' endpoint bulunamadı\n"
    error_msg += f"{'='*80}\n\n"
    
    if suggestions:
        error_msg += "💡 ÖNERİLER:\n"
        for i, suggestion in enumerate(suggestions, 1):
            # Endpoint bilgisini al
            endpoint_info = _endpoint_data.get(suggestion, {})
            short_name = endpoint_info.get('short_name_tr', '') or endpoint_info.get('short_name', '')
            
            error_msg += f"   {i}. {suggestion}"
            if short_name:
                error_msg += f" → {short_name}"
            error_msg += "\n"
    
    error_msg += "\n📚 YARDIMCI FONKSİYONLAR:\n"
    error_msg += "   • ep.search('keyword')           → Kelime içeren endpoint'ler\n"
    error_msg += "   • ep.list_by_category('gop')     → Kategori bazlı listeleme\n"
    error_msg += "   • ep.list_endpoints()            → Tüm endpoint'ler\n"
    error_msg += f"\n{'='*80}\n"
    
    raise AttributeError(error_msg)


def _validate_getattr_input(name):
    """__getattr__ için giriş validasyonu"""
    if name.startswith(("_ipython_", "_repr_")):
        raise AttributeError(f"'{name}' not found")
    if not _auth_configured:
        raise AuthenticationError()
    if not _INITIALIZED:
        _load_all_endpoints()


def __getattr__(name):
    start_time = time.time()

    try:
        _validate_getattr_input(name)

        # 1. Direct match (tam eşleşme)
        if name in _endpoint_search_index:
            return _handle_direct_match(name, start_time)

        # 2. Normalized match (tire/underscore normalize)
        normalized = normalize_search_term(name)
        if normalized in _endpoint_search_index:
            duration = time.time() - start_time
            log_performance("__getattr__normalized_match", duration, 
                          endpoint=name, matched=normalized, match_type="normalized")
            return _get_endpoint(_endpoint_search_index[normalized])
        
        if normalized in _normalized_index:
            matched_key = _normalized_index[normalized]
            duration = time.time() - start_time
            log_performance("__getattr__normalized_index_match", duration,
                          endpoint=name, matched=matched_key, match_type="normalized_index")
            return _get_endpoint(_endpoint_search_index[matched_key])

        # 3. Alias match (kısaltmalar)
        aliased = _apply_aliases(name)
        if aliased != name and aliased in _endpoint_search_index:
            duration = time.time() - start_time
            log_performance("__getattr__alias_match", duration,
                          endpoint=name, matched=aliased, match_type="alias")
            return _get_endpoint(_endpoint_search_index[aliased])

        # 4. Keyword match (kelime bazlı)
        keyword_results = _keyword_search(name, max_results=1)
        if keyword_results:
            matched_key = keyword_results[0]
            duration = time.time() - start_time
            log_performance("__getattr__keyword_match", duration,
                          endpoint=name, matched=matched_key, match_type="keyword")
            return _get_endpoint(_endpoint_search_index[matched_key])

        # 5. Fuzzy search (benzerlik skoru - threshold artırıldı)
        result = _handle_fuzzy_match(name, start_time)
        if result:
            return result

        # 6. No match found - akıllı önerilerle
        _handle_enhanced_no_match(name, start_time)

    except Exception as e:
        duration = time.time() - start_time
        log_error(
            "__getattr__error", endpoint=name, error_msg=str(e), duration=duration
        )
        raise


def _get_search_candidates(name_words):
    """Arama adaylarını bul"""
    candidates = []
    for search_key, endpoint_key in _endpoint_search_index.items():
        search_key_lower = search_key.lower()
        search_words = set(search_key_lower.replace("_", " ").split())

        # En az bir kelime eşleşiyorsa aday olarak ekle
        if name_words.intersection(search_words):
            candidates.append((search_key, endpoint_key))

    # Eğer çok fazla aday varsa, sadece ilk 100'ünü kontrol et
    if len(candidates) > 100:
        candidates = candidates[:100]

    return candidates


def _find_best_fuzzy_match(name_lower, candidates):
    """En iyi fuzzy match'i bul"""
    best_score = 0.0
    best_match = None

    for search_key, endpoint_key in candidates:
        score = difflib.SequenceMatcher(None, name_lower, search_key.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = endpoint_key

    return best_match, best_score


def _fuzzy_search(name):
    name_lower = name.lower()
    name_words = set(name_lower.replace("_", " ").split())

    # Hızlı filtreleme: en az bir kelime eşleşen endpoint'leri kontrol et
    candidates = _get_search_candidates(name_words)

    # Sadece adaylar arasında fuzzy search yap
    best_match, best_score = _find_best_fuzzy_match(name_lower, candidates)

    # Threshold artırıldı: 0.5 → 0.7 (daha iyi eşleşme için)
    if best_match and best_score > 0.7:
        return _get_endpoint(best_match)

    return None


def _calculate_search_score(name, search_info):
    scores = []

    scores.append(
        difflib.SequenceMatcher(None, name, search_info["endpoint_key"].lower()).ratio()
    )

    if search_info["url_path"]:
        scores.append(
            difflib.SequenceMatcher(None, name, search_info["url_path"].lower()).ratio()
        )

    if search_info["short_name"]:
        scores.append(_calculate_text_score(name, search_info["short_name"]))

    if search_info["short_name_tr"]:
        scores.append(_calculate_text_score(name, search_info["short_name_tr"]))

    if search_info["summary"]:
        scores.append(_calculate_text_score(name, search_info["summary"]))

    if search_info["description"]:
        scores.append(_calculate_text_score(name, search_info["description"]))

    return max(scores) if scores else 0.0


def _calculate_text_score(name, text):
    if not text:
        return 0.0
    text_lower = text.lower()
    score = difflib.SequenceMatcher(None, name, text_lower).ratio()
    if name == text_lower:
        score = 1.0
    return score


def _calculate_word_bonus(name, endpoint_name):
    name_words = set(name.split("_"))
    endpoint_words = set(endpoint_name.lower().split("_"))
    common_words = name_words.intersection(endpoint_words)
    return len(common_words) * 0.1 if common_words else 0.0


# ============================================================================
# PUBLIC HELPER FUNCTIONS - Kullanıcı için yardımcı fonksiyonlar
# ============================================================================

def search(keyword, category=None, limit=20):
    """Kelime içeren endpoint'leri ara
    
    Args:
        keyword: Aranacak kelime/ifade
        category: Kategoriye göre filtrele (opsiyonel)
        limit: Maksimum sonuç sayısı (varsayılan: 20)
    
    Returns:
        list: Eşleşen endpoint isimleri
    
    Örnek:
        >>> ep.search('daily')
        >>> ep.search('mcp', category='seffaflik-reporting')
    """
    if not _INITIALIZED:
        _load_all_endpoints()
    
    keyword_lower = keyword.lower().replace('-', '_').replace(' ', '_')
    keyword_words = keyword_lower.split('_')
    results = []
    seen = set()
    
    for endpoint_key, endpoint_info in _endpoint_data.items():
        # Kategori filtresi
        if category and endpoint_info.get('category') != category:
            continue
        
        endpoint_key_lower = endpoint_key.lower()
        
        # Tam eşleşme
        if keyword_lower in endpoint_key_lower:
            if endpoint_key not in seen:
                results.append({
                    'name': endpoint_key,
                    'category': endpoint_info.get('category', ''),
                    'short_name': endpoint_info.get('short_name', ''),
                    'short_name_tr': endpoint_info.get('short_name_tr', ''),
                    'score': 100
                })
                seen.add(endpoint_key)
        
        # Kelime bazlı eşleşme (tire/underscore normalize)
        elif any(word in endpoint_key_lower for word in keyword_words if len(word) > 2):
            if endpoint_key not in seen:
                # Skor hesapla
                matches = sum(1 for word in keyword_words if word in endpoint_key_lower)
                score = (matches / len(keyword_words)) * 50
                
                results.append({
                    'name': endpoint_key,
                    'category': endpoint_info.get('category', ''),
                    'short_name': endpoint_info.get('short_name', ''),
                    'short_name_tr': endpoint_info.get('short_name_tr', ''),
                    'score': score
                })
                seen.add(endpoint_key)
        
        # Short name'de ara
        short_name_tr = endpoint_info.get('short_name_tr', '').lower()
        if keyword_lower in short_name_tr or any(word in short_name_tr for word in keyword_words if len(word) > 2):
            if endpoint_key not in seen:
                results.append({
                    'name': endpoint_key,
                    'category': endpoint_info.get('category', ''),
                    'short_name': endpoint_info.get('short_name', ''),
                    'short_name_tr': endpoint_info.get('short_name_tr', ''),
                    'score': 30
                })
                seen.add(endpoint_key)
    
    # Skora göre sırala
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    results = results[:limit]
    
    # Sonuçları yazdır
    print(f"\n{'='*80}")
    print(f"🔍 '{keyword}' için {len(results)} sonuç bulundu")
    if category:
        print(f"📁 Kategori: {category}")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i:2}. {result['name']}")
        if result['short_name_tr']:
            print(f"    └─ {result['short_name_tr']}")
        print(f"    📂 {result['category']}")
        if i < len(results):
            print()
    
    print(f"{'='*80}\n")
    
    return [r['name'] for r in results]


def list_by_category(category):
    """Kategoriye göre endpoint'leri listele
    
    Args:
        category: Kategori adı (örn: 'gop', 'seffaflik-reporting')
    
    Returns:
        list: Kategorideki tüm endpoint isimleri
    
    Örnek:
        >>> ep.list_by_category('gop')
        >>> ep.list_by_category('seffaflik-reporting')
    """
    if not _INITIALIZED:
        _load_all_endpoints()
    
    results = []
    
    for endpoint_key, endpoint_info in _endpoint_data.items():
        if endpoint_info.get('category') == category:
            results.append({
                'name': endpoint_key,
                'short_name': endpoint_info.get('short_name', ''),
                'short_name_tr': endpoint_info.get('short_name_tr', ''),
            })
    
    # Sonuçları yazdır
    print(f"\n{'='*80}")
    print(f"📁 '{category}' kategorisinde {len(results)} endpoint bulundu")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i:2}. {result['name']}")
        if result['short_name_tr']:
            print(f"    └─ {result['short_name_tr']}")
        if i < len(results):
            print()
    
    print(f"{'='*80}\n")
    
    return [r['name'] for r in results]


def list_endpoints(pattern=None):
    """Tüm endpoint'leri listele
    
    Args:
        pattern: Regex pattern (opsiyonel, örn: 'mcp.*daily')
    
    Returns:
        dict: Kategorilere göre gruplanmış endpoint'ler
    
    Örnek:
        >>> ep.list_endpoints()
        >>> ep.list_endpoints(pattern='mcp.*')
    """
    if not _INITIALIZED:
        _load_all_endpoints()
    
    # Kategorilere göre grupla
    by_category = {}
    
    for endpoint_key, endpoint_info in _endpoint_data.items():
        # Pattern filtresi
        if pattern:
            import re
            if not re.search(pattern, endpoint_key):
                continue
        
        category = endpoint_info.get('category', 'uncategorized')
        if category not in by_category:
            by_category[category] = []
        
        by_category[category].append({
            'name': endpoint_key,
            'short_name_tr': endpoint_info.get('short_name_tr', ''),
        })
    
    # Sonuçları yazdır
    print(f"\n{'='*80}")
    print(f"📚 TÜML ENDPOINT'LER")
    if pattern:
        print(f"🔍 Pattern: {pattern}")
    print(f"{'='*80}\n")
    
    total = 0
    for category in sorted(by_category.keys()):
        endpoints = by_category[category]
        total += len(endpoints)
        print(f"\n📁 {category} ({len(endpoints)} endpoint)")
        print(f"{'─'*80}")
        
        for i, ep in enumerate(endpoints[:5], 1):  # İlk 5'i göster
            print(f"   {i}. {ep['name']}")
            if ep['short_name_tr']:
                print(f"      └─ {ep['short_name_tr']}")
        
        if len(endpoints) > 5:
            print(f"   ... ve {len(endpoints)-5} tane daha")
    
    print(f"\n{'='*80}")
    print(f"📊 Toplam: {total} endpoint, {len(by_category)} kategori")
    print(f"{'='*80}\n")
    
    return by_category


def list_categories():
    """Tüm kategorileri listele
    
    Returns:
        dict: Kategoriler ve endpoint sayıları
    
    Örnek:
        >>> ep.list_categories()
    """
    if not _INITIALIZED:
        _load_all_endpoints()
    
    categories = {}
    for endpoint_info in _endpoint_data.values():
        category = endpoint_info.get('category', 'uncategorized')
        categories[category] = categories.get(category, 0) + 1
    
    print(f"\n{'='*80}")
    print(f"📂 TÜM KATEGORİLER")
    print(f"{'='*80}\n")
    
    for i, (category, count) in enumerate(sorted(categories.items()), 1):
        print(f"{i:2}. {category:40} ({count:4} endpoint)")
    
    print(f"\n{'='*80}")
    print(f"📊 Toplam: {len(categories)} kategori")
    print(f"{'='*80}\n")
    
    return categories


def __repr__():
    return f"<module 'epint' v{__version__}>"


__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "EndpointManager",
    "clear_cache",
    "set_auth",
    "set_mode",
    "AuthenticationError",
    # Yeni yardımcı fonksiyonlar
    "search",
    "list_by_category",
    "list_endpoints",
    "list_categories",
    "normalize_search_term",
]

_load_all_endpoints()
