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
_INITIALIZED = False

_username = None
_password = None
_auth_configured = False
_current_mode = "prod"  # Default prod mode


def _load_all_endpoints():
    global _INITIALIZED
    if _INITIALIZED:
        return

    start_time = time.time()
    log_operation("_load_all_endpoints_start")

    try:
        _load_endpoints_from_directory()
        _INITIALIZED = True

        duration = time.time() - start_time
        log_performance(
            "_load_all_endpoints", duration, endpoint_count=len(_endpoint_search_index)
        )
        log_operation(
            "_load_all_endpoints_complete", endpoint_count=len(_endpoint_search_index)
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

            global _endpoint_search_index, _endpoint_categories
            _endpoint_search_index = cache_data.get("search_index", {})
            _endpoint_categories = cache_data.get("categories", {})
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

        # Direct match
        if name in _endpoint_search_index:
            return _handle_direct_match(name, start_time)

        # Fuzzy search
        result = _handle_fuzzy_match(name, start_time)
        if result:
            return result

        # No match found
        _handle_no_match(name, start_time)

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

    if best_match and best_score > 0.5:
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
    "AuthenticationError",
]

_load_all_endpoints()
