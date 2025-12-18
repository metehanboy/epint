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

from difflib import SequenceMatcher
from typing import List, Optional

def find_closest_match(target: str, candidates: List[str], threshold: float = 0.6) -> Optional[str]:
    """
    Fuzzy matching ile en yakın eşleşmeyi bul
    
    Args:
        target: Aranacak string
        candidates: Aday string listesi
        threshold: Minimum benzerlik oranı (0.0-1.0)
    
    Returns:
        En yakın eşleşen string veya None
    """
    if not target or not candidates:
        return None
    
    # Önce direkt eşleşme kontrol et (case-insensitive)
    target_lower = target.lower()
    for candidate in candidates:
        if candidate.lower() == target_lower:
            return candidate
    
    # Direkt eşleşme yoksa fuzzy matching yap
    target_norm = target
    
    best_match = None
    best_ratio = 0.0
    for candidate in candidates:
        cand_norm = candidate
        ratio = SequenceMatcher(None, target_norm, cand_norm).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = candidate
    return best_match