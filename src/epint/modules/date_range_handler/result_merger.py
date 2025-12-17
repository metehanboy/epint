# -*- coding: utf-8 -*-

"""Result merging utilities"""

from typing import List, Any


def merge_results(results: List[Any]) -> Any:
    """
    Sonuçları birleştir
    
    Args:
        results: Birleştirilecek sonuçlar listesi
    
    Returns:
        Birleştirilmiş sonuç
    """
    if not results:
        return None
    
    if len(results) == 1:
        return results[0]
    
    # İlk sonucun tipine göre birleştirme stratejisi belirle
    first_result = results[0]
    
    if isinstance(first_result, list):
        # Liste ise extend et
        merged = []
        for result in results:
            if isinstance(result, list):
                merged.extend(result)
            else:
                merged.append(result)
        return merged
    elif isinstance(first_result, dict):
        # Dict ise merge et (array field'ları extend et)
        merged = {}
        for result in results:
            if isinstance(result, dict):
                for key, value in result.items():
                    if key in merged:
                        if isinstance(merged[key], list) and isinstance(value, list):
                            merged[key].extend(value)
                        elif isinstance(merged[key], list):
                            merged[key].append(value)
                        elif isinstance(value, list):
                            merged[key] = [merged[key]] + value
                        else:
                            # Son değer kazanır
                            merged[key] = value
                    else:
                        merged[key] = value
            else:
                # Dict değilse ekle
                if 'items' not in merged:
                    merged['items'] = []
                merged['items'].append(result)
        return merged
    else:
        # Diğer tipler için liste olarak döndür
        return results


__all__ = ['merge_results']

