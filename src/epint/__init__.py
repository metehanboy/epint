# -*- coding: utf-8 -*-
from .modules.version import __version__, __appname__
from .modules.search.ipython_blockage import IPYTHON_MAGIC_METHODS
from .modules.search.method_name_decorator import to_python_method_name
from .modules.search.find_closest import find_closest_match
from .modules.category_proxy import CategoryProxy
from .endpoints import get_endpoints_dir, list_categories
from .models.endpoint import EndpointModel
import os


# Kategori cache
_category_objects = {}

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
    
    normalized_name = to_python_method_name(name)
    normalized_categories = {to_python_method_name(cat): cat for cat in categories}
    
    # 2. Normalize edilmiş isimle tam eşleşme kontrolü
    if normalized_name in normalized_categories:
        category = normalized_categories[normalized_name]
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    
    # 3. Normalize edilmiş isimle fuzzy matching (düşük öncelik)
    closest_normalized = find_closest_match(normalized_name, list(normalized_categories.keys()), threshold=0.6)
    if closest_normalized:
        category = normalized_categories[closest_normalized]
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    
    # 4. Orijinal kategori isimleriyle fuzzy matching (en düşük öncelik)
    closest = find_closest_match(normalized_name, categories, threshold=0.6)
    if closest:
        load_category(closest)
        if closest not in _category_objects:
            _category_objects[closest] = CategoryProxy(closest)
        return _category_objects[closest]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


