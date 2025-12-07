# -*- coding: utf-8 -*-
from .modules.version import __version__
from .modules.search.ipython_blockage import IPYTHON_MAGIC_METHODS
from .modules.search.method_name_decorator import to_python_method_name
from .modules.search.find_closest import find_closest_match
from .modules.category_proxy import CategoryProxy
from .endpoints import get_endpoints_dir, list_categories
from .models.endpoint import EndpointModel
import os


# Kategori cache
_category_objects = {}


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
    
    normalized_name = to_python_method_name(name)
    
    categories = list_categories()
    normalized_categories = {to_python_method_name(cat): cat for cat in categories}
    closest_normalized = find_closest_match(normalized_name, list(normalized_categories.keys()), threshold=0.6)
    
    if closest_normalized:
        category = normalized_categories[closest_normalized]
        
        load_category(category)
        if category not in _category_objects:
            _category_objects[category] = CategoryProxy(category)
        return _category_objects[category]
    
    # Orijinal isimle tam eşleşme
    if name in categories:
        load_category(name)
        if name not in _category_objects:
            _category_objects[name] = CategoryProxy(name)
        return _category_objects[name]
    
    # find_closest ile yakın eşleşme ara (orijinal kategori isimleriyle)
    closest = find_closest_match(normalized_name, categories, threshold=0.6)
    if closest:
        load_category(closest)
        if closest not in _category_objects:
            _category_objects[closest] = CategoryProxy(closest)
        return _category_objects[closest]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


