# -*- coding: utf-8 -*-

from .__priv__ import get_version
from .endpoints import get_endpoints_dir, list_categories, get_endpoints,\
    load_category

__version__ = get_version()

# Kategori cache
_category_objects = {}


class _CategoryProxy:
    """Kategori proxy objesi - category.endpoint şeklinde erişim sağlar"""
    
    def __init__(self, category: str):
        self._category = category
    
    def __getattr__(self, name):
        endpoint = get_endpoints(self._category).get(name)
        if endpoint:
            return lambda **kwargs: endpoint
        raise AttributeError(f"'{self._category}' category has no endpoint '{name}'")


def __getattr__(name):
    ipython_methods = {
        '_ipython_canary_method_should_not_exist_',
        '_ipython_display_',
        '_repr_mimebundle_',
        '_repr_html_',
        '_repr_markdown_',
        '_repr_svg_',
        '_repr_png_',
        '_repr_pdf_',
        '_repr_jpeg_',
        '_repr_latex_',
        '_repr_json_',
        '_repr_javascript_',
    }
    
    if name in ipython_methods:
        return None
    
    # Kategori kontrolü
    if name in list_categories():
        load_category(name)  # Endpoint'leri yükle
        if name not in _category_objects:
            _category_objects[name] = _CategoryProxy(name)
        return _category_objects[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

