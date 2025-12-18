# -*- coding: utf-8 -*-

"""Page collection utilities"""

from typing import Dict, Any, Callable, List


def collect_all_pages(
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
    # İlk response'dan page bilgisini al
    page_info = first_response.get('page', {})
    total = page_info.get('total', 0)
    size = page_info.get('size', 0)
    
    if not total or not size or total <= size:
        # Tek sayfa veya pagination yok, direkt döndür
        return first_response
    
    # Toplam sayfa sayısını hesapla
    total_pages = (total + size - 1) // size  # Ceiling division
    
    # İlk sayfanın items'ını al
    all_items = first_response.get('items', [])
    if not isinstance(all_items, list):
        all_items = []
    
    # Orijinal kwargs'ı kopyala
    kwargs = original_kwargs.copy()
    
    # Page bilgisini al (varsa)
    page_param = kwargs.get('page', {})
    if not isinstance(page_param, dict):
        page_param = {}
    
    # Sort bilgisini koru (varsa)
    sort_info = page_info.get('sort')
    
    # Kalan sayfaları topla
    for page_num in range(2, total_pages + 1):
        # Page parametresini güncelle
        page_param['number'] = page_num
        if sort_info:
            page_param['sort'] = sort_info.copy()
        
        kwargs['page'] = page_param.copy()
        
        # Sayfa çağrısı yap
        page_response = endpoint_callable(**kwargs)
        
        # Items'ı ekle
        page_items = page_response.get('items', [])
        if isinstance(page_items, list):
            all_items.extend(page_items)
    
    # Sonuçları birleştir
    result = {
        'items': all_items,
        'page': {
            'number': 1,
            'size': len(all_items),
            'total': total,
        }
    }
    
    # Sort bilgisini ekle (varsa)
    if sort_info:
        result['page']['sort'] = sort_info.copy()
    
    return result


__all__ = ['collect_all_pages']

