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