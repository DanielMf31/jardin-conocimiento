## Solución 1 - Ordenar ambos y comparar

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        return sorted(s) == sorted(t)
    
## Solución 2 - Dos diccionarios de frecuencia

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        
        count_s, count_t = {},{}
        for char in s:
            count_s[char] = count_s.get(char,0) + 1
        for char in t:
            count_t[char] = count_t.get(char,0) + 1
        return count_t == count_t

## Solucion 3: Un solo diccionario

class Solution:
    def isAnagram(self, s: str, t:str) -> bool:
        if len(s) != len(t):
            return False
        
        count = {}
        for char in s:
            count[char] = count.get(char,0) + 1
        for char in t:
            if char not in count or count[char] == 0:
                return False
            
            count[char] -= 1
        return True
    
## Solucion 4: Counter (Pythonica)

from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        return Counter(s) == Counter(t)
