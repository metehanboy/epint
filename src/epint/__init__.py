# -*- coding: utf-8 -*-
from .modules.version import __version__, __appname__, __fullname__
from .modules.search.ipython_blockage import IPYTHON_MAGIC_METHODS
from .modules.search.method_name_decorator import to_python_method_name
from .modules.search.find_closest import find_closest_match
from .modules.category_proxy import CategoryProxy
from .endpoints import get_endpoints_dir, list_categories
from .models.endpoint import EndpointModel
import os


# Kategori cache
_category_objects = {}

# Kategori alternatif isimleri (alias'lar)
CATEGORY_ALIASES = {
    'transparency': 'seffaflik-electricity',
    'naturalgas': 'seffaflik-natural-gas',
    'cng': 'seffaflik-natural-gas',
    'dogalgaz': 'seffaflik-natural-gas',
    'reporting': 'seffaflik-reporting',
    'invoice': 'reconciliation-invoice',
    'bpm': 'reconciliation-bpm',
    'imbalance': 'reconciliation-imbalance',
    'market': 'reconciliation-market',
    'mof': 'reconciliation-mof',
    'res': 'reconciliation-res',
}

_username: str = None
_password: str = None
_mode: str = "prod"

def set_auth(username: str, password: str) -> None:
    """Kullanıcı adı ve şifre ayarla"""
    global _username
    global _password

    _username = username
    _password = password

def set_mode(mode: str) -> None:
    """Runtime mode ayarla (prod/test)"""
    global _mode

    _mode = "test" if mode.lower() != "prod" else "prod"

def _check_auth():
    """Auth bilgilerinin set edilip edilmediğini kontrol et"""
    if _username is None or _password is None:
        raise RuntimeError(
            "Authentication bilgileri set edilmemiş. "
            "Lütfen önce 'epint.set_auth(username, password)' çağrısı yapın."
        )

def load_category(category: str):
    if category in EndpointModel.get_all_categories():
        return  # daha önce çağırıldı ise tekrar yüklemeyelim.
    
    swagger_path = os.path.join(get_endpoints_dir(), category, "swagger.json")
    
    if os.path.exists(swagger_path):
        EndpointModel.load_swagger(category, swagger_path)

def get_endpoints(category: str):
    """Kategori endpoint'lerini döndür"""
    return EndpointModel.get_category_endpoints(category)

def __getattr__(name):
    if name in IPYTHON_MAGIC_METHODS:
        raise AttributeError(f"'{__name__}' module has blocked attribute '{name}'")
    
    categories = list_categories()
    
    # 1. Önce orijinal isimle tam eşleşme kontrolü (en yüksek öncelik)
    if name in categories:
        load_category(name)
        if name not in _category_objects:
            _category_objects[name] = CategoryProxy(name)
        return _category_objects[name]
    
    # 2. Alternatif isimlerle (alias) eşleşme kontrolü
    if name in CATEGORY_ALIASES:
        category = CATEGORY_ALIASES[name]
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    
    # 2b. Alternatif isimlerle (alias) fuzzy matching
    normalized_name = to_python_method_name(name)
    alias_keys = list(CATEGORY_ALIASES.keys())
    closest_alias = find_closest_match(normalized_name, alias_keys, threshold=0.6)
    if closest_alias:
        category = CATEGORY_ALIASES[closest_alias]
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    normalized_categories = {to_python_method_name(cat): cat for cat in categories}
    
    # 3. Seffaflik kategorileri için prefix'i yoksayarak arama
    # Örnek: "seffalik", "seffaflik" -> "seffaflik-electricity", "seffaflik-natural-gas", vb.
    if normalized_name not in normalized_categories:
        seffaflik_categories = [cat for cat in categories if cat.startswith('seffaflik-')]
        if seffaflik_categories:
            # "seffaflik" veya "seffalik" gibi yazımları kontrol et
            name_lower = name.lower()
            if 'seffaflik' in name_lower or 'seffalik' in name_lower:
                # Eğer sadece "seffaflik" veya "seffalik" yazılmışsa, en yaygın olanı döndür
                if normalized_name in ['seffaflik', 'seffalik'] or name_lower in ['seffaflik', 'seffalik']:
                    # Varsayılan olarak seffaflik-electricity'yi döndür
                    category = 'seffaflik-electricity'
                    load_category(category)
                    if category not in _category_objects:
                        _category_objects[category] = CategoryProxy(category)
                    return _category_objects[category]
                else:
                    # Alt kategori ismi varsa (örn: "electricity", "naturalgas") fuzzy matching yap
                    for cat in seffaflik_categories:
                        suffix = cat.replace('seffaflik-', '')
                        normalized_suffix = to_python_method_name(suffix)
                        if normalized_name == normalized_suffix:
                            category = cat
                            load_category(category)
                            if category not in _category_objects:
                                _category_objects[category] = CategoryProxy(category)
                            return _category_objects[category]
                    # Fuzzy matching ile en yakın seffaflik kategorisini bul
                    closest_seffaflik = find_closest_match(normalized_name, [to_python_method_name(cat.replace('seffaflik-', '')) for cat in seffaflik_categories], threshold=0.6)
                    if closest_seffaflik:
                        for cat in seffaflik_categories:
                            if to_python_method_name(cat.replace('seffaflik-', '')) == closest_seffaflik:
                                category = cat
                                load_category(category)
                                if category not in _category_objects:
                                    _category_objects[category] = CategoryProxy(category)
                                return _category_objects[category]
    
    # 4. Reconciliation kategorileri için prefix'i yoksayarak arama
    # Örnek: "invoice" -> "reconciliation-invoice"
    if normalized_name not in normalized_categories:
        for cat in categories:
            if cat.startswith('reconciliation-'):
                # reconciliation- prefix'ini kaldır ve normalize et
                suffix = cat.replace('reconciliation-', '')
                normalized_suffix = to_python_method_name(suffix)
                if normalized_name == normalized_suffix:
                    category = cat
                    load_category(category)
                    if category not in _category_objects:
                        _category_objects[category] = CategoryProxy(category)
                    return _category_objects[category]

    # 4. Normalize edilmiş isimle tam eşleşme kontrolü
    if normalized_name in normalized_categories:
        category = normalized_categories[normalized_name]
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    
    # 5. Normalize edilmiş isimle fuzzy matching
    closest_normalized = find_closest_match(normalized_name, list(normalized_categories.keys()), threshold=0.6)
    if closest_normalized:
        category = normalized_categories[closest_normalized]
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    
    # 6. Orijinal kategori isimleriyle fuzzy matching (en düşük öncelik)
    closest = find_closest_match(normalized_name, categories, threshold=0.6)
    if closest:
        load_category(closest)
        if closest not in _category_objects:
            _category_objects[closest] = CategoryProxy(closest)
        return _category_objects[closest]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


