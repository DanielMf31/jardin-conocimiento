## Solucion 1 - Fuerza bruta

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        grupos = []
        for s in strs:
            colocado = False
            for g in grupos:
                if sorted(s) == sorted(g[0]):
                    g.append(s)
                    colocado = True
                    break
            if not colocado:
                grupos.append([s])
        return grupos
    

## Solucion 2 - Dict con clave = string ordenado (la idiomática)
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        grupos = defaultdict(list)
        for s in strs:
            clave = "".join(sorted(s))
            grupos[clave].append(s)
        return list(grupos.values())
    

