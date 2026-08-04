---
title: "LeetCode 2 — Add Two Numbers"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/linked-list, patron/dummy-node, patron/carry]
type: nota
status: en-progreso
source: claude-code
aliases: [Add Two Numbers, LC 2, addTwoNumbers, Suma de números en lista]
problem_id: 2
difficulty: medium
patron: linked-list
neetcode_order: 7
---

# LeetCode 2 — Add Two Numbers

> **Séptimo problema del patrón Linked List**. Suma aritmética con **carry** simulando suma a mano. Combina dummy node + iteración con condición compuesta. Excelente práctica de manejo de "casos especiales" elegantes con bucles uniformes.

## Enunciado

Te dan dos linked lists no vacías representando enteros **no negativos**. Los dígitos están en **orden inverso** (cabeza = unidades). Cada nodo es un dígito.

Suma los dos números y devuelve el resultado como linked list.

**Ejemplo 1:**
```
Input:  l1 = [2,4,3], l2 = [5,6,4]
        (representan 342 + 465 = 807)
Output: [7,0,8]
```

**Ejemplo 2:**
```
Input:  l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
        (9999999 + 9999 = 10009998)
Output: [8,9,9,9,0,0,0,1]
```

---

## Solución — Iterativo con carry y dummy (la canónica)

```python
class Solution:
    def addTwoNumbers(self, l1, l2):
        dummy = ListNode()
        tail = dummy
        carry = 0

        while l1 or l2 or carry:
            v1 = l1.val if l1 else 0
            v2 = l2.val if l2 else 0
            total = v1 + v2 + carry
            carry, digit = divmod(total, 10)

            tail.next = ListNode(digit)
            tail = tail.next

            l1 = l1.next if l1 else None
            l2 = l2.next if l2 else None

        return dummy.next
```

**Trace mental con `[2,4,3] + [5,6,4]`** (342 + 465):

```
Iter 1: v1=2, v2=5, total=7, carry=0, digit=7
        result: 7

Iter 2: v1=4, v2=6, total=10, carry=1, digit=0
        result: 7 → 0

Iter 3: v1=3, v2=4, total=8 (3+4+1 carry), carry=0, digit=8
        result: 7 → 0 → 8

Final: 7 → 0 → 8 [OK] (= 807, que es 342+465)
```

**Análisis:**
- **Tiempo: O(max(m, n))**.
- **Espacio: O(max(m, n))** para la lista resultado.
- **Veredicto:** [OK] la canónica.

### El truco de la condición compuesta `while l1 or l2 or carry`

```python
while l1 or l2 or carry:
```

**Tres razones para seguir**:
1. `l1` aún tiene dígitos.
2. `l2` aún tiene dígitos.
3. Hay un `carry` pendiente que aún no se ha colocado.

Sin la tercera, fallarías el caso `[5] + [5] = [0,1]` (carry final).

### `divmod(total, 10)`

```python
divmod(17, 10)              # (1, 7) → carry=1, digit=7
divmod(8, 10)               # (0, 8) → carry=0, digit=8
```

Atajo pythonic para `(a // 10, a % 10)`.

---

## Variaciones

| Problema LeetCode | Variación |
|---|---|
| **445. Add Two Numbers II** | Dígitos en orden NORMAL (cabeza = más significativo) → reverse o stack |
| **989. Add to Array-Form of Integer** | Mismo patrón sobre arrays |

---

## Auto-test

1. Escribe la solución desde cero.
2. Justifica las 3 condiciones del `while`.
3. Trace mental con `[9,9,9] + [1]` (caso de carry propagado).

---

## Conexiones

- [[21-merge-two-sorted-lists]] — patrón dummy + tail.
- Próximo: [[287-find-the-duplicate-number]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita solución desde cero
- [ ] Trace mental con caso de carry propagado
- [ ] Resuelto en LeetCode con éxito
