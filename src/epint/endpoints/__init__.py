# -*- coding: utf-8 -*-

import os
from typing import Dict, Any
from ..utils.endpoint_model import EndpointModel


__all__ = ['get_categories', 'get_endpoints', 'get_endpoints_dir', 'list_categories', 'load_category', 'get_swagger_file']


def get_endpoints_dir():
    """Endpoints dizinini döndür"""
    return os.path.dirname(__file__)


def list_categories():
    """Kategori listesini döndür"""
    return [d for d in os.listdir(get_endpoints_dir()) 
            if os.path.isdir(os.path.join(get_endpoints_dir(), d)) and not d.startswith('_')]


def get_swagger_file(category: str) -> str:
    """Kategori için swagger dosya yolunu döndür"""
    return os.path.join(get_endpoints_dir(), category, 'swagger.json')


def load_category(category: str):
    """Kategori endpoint'lerini yükle"""
    if category in EndpointModel.get_all_categories():
        print(f"[+] Zaten yüklü! {category}")
        return  # Zaten yüklü
    
    swagger_path = get_swagger_file(category)
    EndpointModel.load_swagger(category, swagger_path)


def get_categories() -> Dict[str, Dict[str, Any]]:
    """Tüm kategorileri döndür"""
    return EndpointModel.get_all_categories()


def get_endpoints(category: str = None) -> Dict[str, Any]:
    """Endpoint'leri döndür - kategori yoksa otomatik yükle"""
    if category:
        if category not in EndpointModel.get_all_categories():
            load_category(category)
        return EndpointModel.get_category_endpoints(category)
    return EndpointModel._endpoints
