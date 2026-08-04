---
title: "LeetCode 143 — Reorder List"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/linked-list, patron/slow-fast, patron/reverse]
type: nota
status: en-progreso
source: claude-code
aliases: [Reorder List, LC 143, reorderList, Reorganizar lista]
problem_id: 143
difficulty: medium
patron: linked-list
neetcode_order: 4
---

# LeetCode 143 — Reorder List

> **Cuarto problema del patrón Linked List**. **Combina 3 sub-rutinas** ya conocidas en una sola solución: encontrar la mitad (slow/fast de [[141-linked-list-cycle]]), invertir lista ([[206-reverse-linked-list]]) y mergear alternando. Aprenderlo ilustra cómo problemas Medium se resuelven **componiendo** patrones simples.

## Enunciado

Te dan la cabeza de una lista enlazada `L: L0 → L1 → ... → Ln-1 → Ln`.

Reordénala in-place a: `L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → ...`

**Ejemplo 1:**
```
Input:  1 → 2 → 3 → 4
Output: 1 → 4 → 2 → 3
```

**Ejemplo 2:**
```
Input:  1 → 2 → 3 → 4 → 5
Output: 1 → 5 → 2 → 4 → 3
```

**Restricciones:**
- Nodos en `[1, 5*10^4]`.
- `1 <= Node.val <= 1000`.

---

## Solución — Mitad + Reverse + Merge alternado (la canónica)

**Tres pasos**:

1. **Encontrar la mitad** con slow/fast.
2. **Invertir la segunda mitad**.
3. **Mergear las dos mitades alternando**.

```python
class Solution:
    def reorderList(self, head):
        if not head or not head.next:
            return

        # Paso 1: encontrar la mitad
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        # slow apunta al final de la primera mitad

        # Paso 2: invertir la segunda mitad
        second = slow.next
        slow.next = None                    # cortar
        prev = None
        while second:
            next_temp = second.next
            second.next = prev
            prev = second
            second = next_temp
        second = prev                        # nueva cabeza de la segunda mitad invertida

        # Paso 3: merge alternando
        first = head
        while second:
            tmp1 = first.next
            tmp2 = second.next
            first.next = second
            second.next = tmp1
            first = tmp1
            second = tmp2
```

**Trace mental con `1 → 2 → 3 → 4`**:

```
Paso 1: slow=2, fast=4 → mitad termina en 2
        first half: 1 → 2
        second half: 3 → 4

Paso 2: invertir 3→4 → 4→3
        first half: 1 → 2
        second half (invertida): 4 → 3

Paso 3: merge alternando
        1 → 4 → 2 → 3 [OK]
```

**Análisis:**
- **Tiempo: O(n)** — tres pasadas lineales.
- **Espacio: O(1)** — todo in-place.
- **Veredicto:** [OK] la canónica.

---

## Auto-test

1. Implementa los 3 pasos por separado primero (función para cada uno), luego combínalos.
2. Justifica por qué `slow.next = None` (cortar) antes del paso 2.
3. Trace mental con `1 → 2 → 3 → 4 → 5` (impar).
4. **Bonus** — implementa LC 234 (Palindrome Linked List) — mismo patrón pero comparando.

---

## Conexiones

- [[206-reverse-linked-list]] — sub-rutina paso 2.
- [[141-linked-list-cycle]] — slow/fast del paso 1.
- Próximo: [[19-remove-nth-node-from-end-of-list]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Implementados los 3 pasos como funciones separadas
- [ ] Combinados en una solución
- [ ] Resuelto en LeetCode con éxito
