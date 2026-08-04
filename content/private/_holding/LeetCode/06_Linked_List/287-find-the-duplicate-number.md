---
title: "LeetCode 287 — Find the Duplicate Number"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/linked-list, patron/floyd-cycle, patron/sin-modificar-array]
type: nota
status: en-progreso
source: claude-code
aliases: [Find the Duplicate Number, LC 287, findDuplicate, Encontrar duplicado sin modificar]
problem_id: 287
difficulty: medium
patron: linked-list
neetcode_order: 8
---

# LeetCode 287 — Find the Duplicate Number

> **Octavo problema del patrón Linked List** — y un giro brillante: aplicar **Floyd's cycle detection** (de [[141-linked-list-cycle]]) **sobre un array**, tratándolo como linked list virtual. Es uno de los problemas más elegantes de NeetCode.

## Enunciado

Te dan un array `nums` con `n+1` enteros donde cada entero está en el rango `[1, n]`. Hay **exactamente un valor repetido** (puede aparecer más de dos veces).

Encuentra el valor repetido **sin modificar el array** y usando solo **O(1) espacio extra**.

**Ejemplo 1:**
```
Input:  nums = [1,3,4,2,2]
Output: 2
```

**Ejemplo 2:**
```
Input:  nums = [3,1,3,4,2]
Output: 3
```

**Restricciones:**
- `1 <= n <= 10^5`.
- `nums.length == n + 1`.
- `1 <= nums[i] <= n`.
- Solo un valor está duplicado.

---

## Solución 1 — Hash set (no cumple O(1) espacio)

```python
class Solution:
    def findDuplicate(self, nums):
        seen = set()
        for num in nums:
            if num in seen:
                return num
            seen.add(num)
```

[NO] Viola la restricción O(1) espacio.

---

## Solución 2 — Floyd's tortoise and hare sobre el array (la canónica)

**La observación brillante**: tratar `nums` como linked list virtual donde `nums[i]` es "el next del nodo i". Como hay un duplicado, **hay un ciclo** (dos nodos tienen el mismo "next"). El **inicio del ciclo** es el duplicado.

```python
class Solution:
    def findDuplicate(self, nums):
        # Fase 1: encontrar punto de encuentro
        slow = fast = nums[0]
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break

        # Fase 2: encontrar inicio del ciclo (= duplicado)
        slow = nums[0]
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]
        return slow
```

**Por qué funciona**:
- Cada `nums[i]` se interpreta como "siguiente nodo" en una linked list virtual.
- Como hay duplicado, dos índices apuntan al mismo "siguiente" → ciclo.
- Floyd detecta el ciclo (fase 1).
- La fase 2 (matemática del algoritmo de Floyd) encuentra el **inicio** del ciclo, que corresponde al **duplicado**.

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(1)**.
- **Veredicto:** [OK] **la canónica**. Cumple ambas restricciones.

> **Es el mismo algoritmo que en [[141-linked-list-cycle]] + LC 142**, aplicado a un array como si fuera linked list. Si entendiste aquellos, este es un giro de perspectiva.

---

## Auto-test

1. Reproduce la solución sin mirar.
2. Justifica por qué ver el array como linked list "funciona" (cada índice apunta a otro).
3. Trace mental con `nums = [1,3,4,2,2]`.

---

## Conexiones

- [[141-linked-list-cycle]] — Floyd original.
- Próximo: [[146-lru-cache]] — diseño con hash + linked list.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Articulada la conexión con LC 141
- [ ] Resuelto en LeetCode con éxito
