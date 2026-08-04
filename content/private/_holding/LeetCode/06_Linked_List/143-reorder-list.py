# LeetCode 143 — reorder-list
# Patrón: 06_Linked_List
# https://leetcode.com/problems/reorder-list/

class Solution:
    def reorderList(self, head):
        if not head or not head.next:
            return

        # === FASE 1: Find middle (slow/fast) ===
        # Tras este while, slow apunta al final de la PRIMERA mitad.
        # Para n=5 (1→2→3→4→5): slow termina en 3.
        # Para n=4 (1→2→3→4):    slow termina en 2.
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        # === FASE 2: Reverse second half ===
        # Cortamos la lista por slow y revertimos lo que viene después.
        second = slow.next
        slow.next = None              # corta primera mitad → termina en None
        prev = None
        while second:
            next_temp = second.next
            second.next = prev
            prev = second
            second = next_temp
        second = prev                 # cabeza de la segunda mitad invertida

        # === FASE 3: Merge alternating (first ←→ second) ===
        # Intercalamos: first[0], second[0], first[1], second[1], ...
        # second siempre es ≤ first en longitud, así que iteramos sobre second.
        first = head
        while second:
            tmp1 = first.next
            tmp2 = second.next
            first.next = second
            second.next = tmp1
            first = tmp1
            second = tmp2
