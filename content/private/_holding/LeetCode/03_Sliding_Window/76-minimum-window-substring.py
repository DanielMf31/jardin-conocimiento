# LeetCode 76 — minimum-window-substring
# Patrón: 03_Sliding_Window
# https://leetcode.com/problems/minimum-window-substring/

from collections import Counter, defaultdict


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if len(t) > len(s):
            return ""

        target = Counter(t)        # frecuencia objetivo: {char: count}
        need = len(target)         # número de caracteres DISTINTOS que cubrir
        have = 0                   # cuántos chars distintos ya cubiertos en cantidad correcta

        window = defaultdict(int)  # ⚠️ era defaultdict(dict) — debe ser int para contador
        left = 0
        best = (-1, 0, 0)          # (length, left_idx, right_idx); -1 = no encontrado aún

        for right, char in enumerate(s):
            # Expandir ventana añadiendo char por la derecha
            window[char] += 1
            if char in target and window[char] == target[char]:
                have += 1

            # Mientras la ventana cubra todo, intenta encogerla por la izquierda
            while have == need:
                # Actualizar best si esta ventana es más pequeña
                if best[0] == -1 or (right - left + 1) < best[0]:
                    best = (right - left + 1, left, right)

                # ⚠️ ESTAS 4 LÍNEAS DEBEN ESTAR AL MISMO NIVEL QUE EL `if best` ⚠️
                # En tu versión estaban DENTRO del if → solo encogías cuando mejorabas best
                # → bucle infinito cuando have == need pero la ventana no era mejor.
                window[s[left]] -= 1
                if s[left] in target and window[s[left]] < target[s[left]]:
                    have -= 1
                left += 1

        if best[0] == -1:
            return ""
        l, r = best[1], best[2]
        return s[l:r+1]
