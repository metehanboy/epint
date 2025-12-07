from difflib import SequenceMatcher
from typing import List, Optional

def find_closest_match(target: str, candidates: List[str], threshold: float = 0.6) -> Optional[str]:
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