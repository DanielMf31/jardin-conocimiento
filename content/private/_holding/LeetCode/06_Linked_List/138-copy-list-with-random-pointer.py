# LeetCode 138 — copy-list-with-random-pointer
# Patrón: 06_Linked_List
# https://leetcode.com/problems/copy-list-with-random-pointer/

"""
# Definition for a Node.
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random
"""

class Solution:
    def copyRandomList(self, head):
        if not head:
            return None

        old_to_new = {}

        # === FASE 1: crear todos los nodos nuevos sin conexiones ===
        # Tras este while, old_to_new tiene TODOS los nodos mapeados.
        # Esto es CRÍTICO: el random pointer puede saltar a cualquier nodo,
        # así que necesitamos que TODOS existan antes de empezar a conectarlos.
        curr = head
        while curr:
            old_to_new[curr] = Node(curr.val)
            curr = curr.next

        # === FASE 2: conectar next y random en los nodos nuevos ===
        # Ahora sí podemos buscar cualquier nodo en old_to_new y existirá.
        # .get() devuelve None si la clave no está (caso curr.next o curr.random == None).
        curr = head
        while curr:
            old_to_new[curr].next = old_to_new.get(curr.next)
            old_to_new[curr].random = old_to_new.get(curr.random)
            curr = curr.next

        return old_to_new[head]
