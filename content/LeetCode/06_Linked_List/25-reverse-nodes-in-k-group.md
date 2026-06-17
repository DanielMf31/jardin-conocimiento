---
title: "LeetCode 25 — Reverse Nodes in K-Group"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/linked-list, patron/reverse-segmento]
type: nota
status: en-progreso
source: claude-code
aliases: [Reverse Nodes in K-Group, LC 25, reverseKGroup, Invertir en grupos de k]
problem_id: 25
difficulty: hard
patron: linked-list
neetcode_order: 11
---

# LeetCode 25 — Reverse Nodes in K-Group

> **Undécimo y último problema del patrón Linked List — segundo Hard**. Combina [[206-reverse-linked-list]] (reverse) con división en bloques. Es el problema con **más manejo manual de punteros** del bloque. Si lo dominas, has cerrado linked lists.

## Enunciado

Dada la cabeza de una linked list, **invierte cada grupo de k nodos** consecutivos. Si el último grupo tiene menos de k nodos, **déjalo como está**.

**Ejemplo 1:**
```
Input:  1 → 2 → 3 → 4 → 5, k = 2
Output: 2 → 1 → 4 → 3 → 5  (último grupo "5" se queda)
```

**Ejemplo 2:**
```
Input:  1 → 2 → 3 → 4 → 5, k = 3
Output: 3 → 2 → 1 → 4 → 5
```

**Restricciones:**
- Nodos en `[1, 5000]`.
- `1 <= k <= n`.
- **Tu solución debe ser O(1) memoria extra** (no contar la lista output).

---

## Solución — Iterativa con dummy + reverse en bloques (la canónica)

**Idea**: usar un `group_prev` (puntero al nodo justo antes del grupo a invertir). Para cada grupo:
1. Localizar el `kth` (k-ésimo nodo del grupo). Si no llega → terminar.
2. Invertir el grupo (mismo patrón que [[206-reverse-linked-list]]).
3. Reconectar con el resto.

```python
class Solution:
    def reverseKGroup(self, head, k):
        dummy = ListNode(0, head)
        group_prev = dummy

        while True:
            kth = self.get_kth(group_prev, k)
            if not kth:
                break
            group_next = kth.next

            # Invertir grupo entre (group_prev.next) y kth
            prev = group_next
            curr = group_prev.next
            while curr != group_next:
                tmp = curr.next
                curr.next = prev
                prev = curr
                curr = tmp

            # Reconectar
            tmp = group_prev.next                    # antiguo primero, ahora último del grupo
            group_prev.next = kth                    # nuevo primero del grupo
            group_prev = tmp                         # nuevo group_prev para siguiente iteración

        return dummy.next

    def get_kth(self, node, k):
        while node and k > 0:
            node = node.next
            k -= 1
        return node
```

**Análisis:**
- **Tiempo: O(n)** — cada nodo se visita una vez para localización y una vez en la inversión.
- **Espacio: O(1)**.
- **Veredicto:** [OK] la canónica.

### Por qué dummy node

Para tener un `group_prev` inicial. Sin dummy, tratar el primer grupo (que cambia la cabeza) requiere caso especial.

### Por qué `get_kth` separado

Es más claro que un contador inline. Devuelve el k-ésimo desde un nodo, o `None` si no hay suficientes (lo cual indica "último grupo incompleto, no invertir").

---

## Auto-test

1. Implementa la solución desde cero. Es **el más complejo del patrón** — date 1+ hora.
2. Justifica:
   - Por qué `prev = group_next` al inicio del while interno.
   - Por qué `group_prev = tmp` al final (el antiguo primero del grupo es el nuevo group_prev).
3. Trace mental con `1 → 2 → 3 → 4 → 5, k = 2`.

---

## Cierre del patrón Linked List

| # | Problema | Variante | Idea distintiva |
|---|---|---|---|
| 1 | [[206-reverse-linked-list]] | Reverse iterativo | 3 punteros (prev/curr/next) |
| 2 | [[21-merge-two-sorted-lists]] | Merge | Dummy + tail |
| 3 | [[141-linked-list-cycle]] | Floyd's tortoise & hare | Slow/fast pointers |
| 4 | [[143-reorder-list]] | Composición de patrones | Mid + reverse + merge |
| 5 | [[19-remove-nth-node-from-end-of-list]] | Two pointers con offset | k+1 de separación |
| 6 | [[138-copy-list-with-random-pointer]] | Deep copy | Hash old→new |
| 7 | [[2-add-two-numbers]] | Suma con carry | Dummy + while con OR |
| 8 | [[287-find-the-duplicate-number]] | Floyd sobre array | Array como linked list virtual |
| 9 | [[146-lru-cache]] | Diseño | DLL + hash, get/put O(1) |
| 10 | [[23-merge-k-sorted-lists]] | K-way merge | Heap o divide-and-conquer |
| 11 | **Este** | Reverse en bloques | Localizar + invertir + reconectar |

**Próximos patrones**:
- **Trees** (15) — recursión + BFS con `deque` (que ya viste).
- **Tries** (3) — árboles de prefijos.

---

## Conexiones

- [[206-reverse-linked-list]] — sub-rutina central.
- [[MOC_NeetCode_150]] — índice general.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Implementada solución desde cero
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
- [ ] **Patrón Linked List cerrado** [OK]
