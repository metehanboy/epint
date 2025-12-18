# -*- coding: utf-8 -*-

"""Pagination handler module for collecting all pages of paginated API responses"""

from typing import Dict, Any, Optional, Callable
from .page_collector import collect_all_pages


class PaginationHandler:
    """Sayfalama yönetimi için handler sınıfı"""
    
    def __init__(self):
        """
        PaginationHandler oluştur
        """
        pass
    
    def has_pagination(self, response: Dict[str, Any]) -> bool:
        """
        Response'da pagination bilgisi var mı kontrol et
        
        Args:
            response: API response dict'i
            
        Returns:
            Pagination bilgisi varsa True
        """
        if not isinstance(response, dict):
            return False
        
        # page bilgisi var mı kontrol et
        page = response.get('page')
        if not isinstance(page, dict):
            return False
        
        # total ve size bilgisi var mı kontrol et
        total = page.get('total')
        size = page.get('size')
        
        if total is None or size is None:
            return False
        
        # total > size ise pagination var
        return isinstance(total, (int, float)) and isinstance(size, (int, float)) and total > size
    
    def collect_all_pages(
        self,
        first_response: Dict[str, Any],
        original_kwargs: Dict[str, Any],
        endpoint_callable: Callable
    ) -> Dict[str, Any]:
        """
        Tüm sayfaları topla ve birleştir
        
        Args:
            first_response: İlk sayfa response'u
            original_kwargs: Orijinal kwargs (page bilgisi güncellenecek)
            endpoint_callable: Endpoint çağrılabilir fonksiyonu
            
        Returns:
            Tüm sayfaların birleştirilmiş hali
        """
        return collect_all_pages(
            first_response,
            original_kwargs,
            endpoint_callable
        )


__all__ = ['PaginationHandler']

