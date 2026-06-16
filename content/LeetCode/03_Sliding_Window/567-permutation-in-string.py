## Solución 1 - Generar todas las permutaciones de s1 (No óptimas)

from itertools import permutations

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        for p in permutations(s1):
            if "".join(p) in s2:
                return True
            return False
        
# Solución 2 - Sliding Window de tramaño fijo + Counter

from collections import Counter

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        n, m = len(s1), len(s2)
        if n > m:
            return False
        
        target = Counter(s1)
        window = Counter(s2[:n])

        if window == target:
            return True
        
        for right in range(n, m):
            window[s2[right]] += 1
            window[s2[right - n]] -= 1
            if window[s2[right]] == 0:
                del window[s2[right - n]]
            if window == target:
                return True
        return False
    
    