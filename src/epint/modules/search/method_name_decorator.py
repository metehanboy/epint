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

import re
import unicodedata


def to_python_method_name(name: str) -> str:
    """Herhangi bir ifadeyi Python method ismine çevirir.
    
    Özellikler:
    - Unicode karakterleri normalize eder (Türkçe karakterler dahil)
    - CamelCase'i snake_case'e çevirir
    - Kebab-case, space, underscore'ı normalize eder
    - Özel karakterleri temizler
    - Python keyword'lerini kontrol eder
    - Başta sayı varsa alt çizgi ekler
    
    Örnekler:
        "getUserData" → "get_user_data"
        "brg-query" → "brg_query"
        "BRG Query" → "brg_query"
        "get_user_data" → "get_user_data"
        "/collateral/organization/" → "collateral_organization"
        "123method" → "_123method"
        "class" → "class_endpoint"
    
    Args:
        name: Dönüştürülecek ifade
        
    Returns:
        str: Python method ismi olarak kullanılabilir string
    """
    if not name:
        return ""
    
    # Unicode normalize (Türkçe karakterler için: ç→c, ş→s, ğ→g, vb.)
    name = unicodedata.normalize('NFKD', str(name))
    name = name.encode('ascii', 'ignore').decode('ascii')
    
    # CamelCase'i tespit et ve snake_case'e çevir
    # Büyük harften önce küçük harf varsa alt çizgi ekle
    name = re.sub(r'(?<!^)(?<!_)([A-Z][a-z]+)', r'_\1', name)
    # Ardışık büyük harfleri (kısaltmalar) koru ama sonrasında küçük harf varsa ayır
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    
    # Küçük harfe çevir
    name = name.lower()
    
    # Path ayırıcılarını (/) alt çizgiye çevir
    name = name.replace('/', '_')
    
    # Özel karakterleri temizle (sadece harf, rakam, tire, underscore, boşluk bırak)
    name = re.sub(r'[^\w\s-]', '', name)
    
    # Boşluk, tire, underscore'ı normalize et (hepsini alt çizgiye çevir)
    name = re.sub(r'[\s\-_]+', '_', name)
    
    # Çoklu alt çizgileri tek yap
    name = re.sub(r'_+', '_', name)
    
    # Başta/sonda alt çizgi varsa temizle
    name = name.strip('_')
    
    # Boş ise
    if not name:
        return ""
    
    # Başta sayı varsa alt çizgi ekle (Python'da değişken ismi sayıyla başlayamaz)
    if name[0].isdigit():
        name = f"_{name}"
    
    # Python keyword'leri kontrolü
    python_keywords = {
        'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
        'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',
        'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
        'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
        'False', 'None', 'True'
    }
    
    if name in python_keywords:
        name = f"{name}_endpoint"
    
    return name