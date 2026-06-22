from collections import Counter
from math import log2

def shannonEntropy(data:bytes) -> float:
    # Prevent zero divition error
    if not data:
        return 0.0
    fr = Counter(data)
    total = len(data)
    
    return -sum(
        (c /total) * log2(c/total)
        for c in fr.values()
    )