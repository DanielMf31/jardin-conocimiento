# LeetCode 3 — longest-substring-without-repeating-characters
# Patrón: 03_Sliding_Window
# https://leetcode.com/problems/longest-substring-without-repeating-characters/


# ============================================================
# Solución 1 — Fuerza bruta O(n²) (NO la canónica, solo referencia)
# ============================================================
# Para cada par (i, j), comprueba si s[i:j+1] tiene caracteres únicos.
# Pasa los tests pero TLE para inputs grandes.
class SolutionBruteForce:
    def lengthOfLongestSubstring(self, s: str) -> int:
        n = len(s)
        best = 0
        for i in range(n):
            for j in range(i, n):                    # ⚠️ era range(1, n) — empezaba mal
                if len(set(s[i:j+1])) == j - i + 1:
                    best = max(best, j - i + 1)
        return best


# ============================================================
# Solución 2 — Sliding window con set (LA CANÓNICA, O(n))
# ============================================================
class Solution:                                       # ⚠️ era "SOlution"
    def lengthOfLongestSubstring(self, s: str) -> int:  # ⚠️ era "lenghtSubstring"
        seen = set()
        left = 0
        best = 0                                      # ⚠️ FALTABA — undefined antes del max
        for right, char in enumerate(s):
            # Si el char ya está en la ventana, encoge desde la izquierda
            # hasta sacarlo. (while, no if — pueden ser varios pasos.)
            while char in seen:
                seen.remove(s[left])
                left += 1
            seen.add(char)
            best = max(best, right - left + 1)
        return best
