# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

