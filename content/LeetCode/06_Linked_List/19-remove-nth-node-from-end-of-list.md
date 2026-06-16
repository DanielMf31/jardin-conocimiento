---
title: "LeetCode 19 — Remove Nth Node From End of List"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/linked-list, patron/two-pointers-offset, patron/dummy-node]
type: nota
status: en-progreso
source: claude-code
aliases: [Remove Nth From End, LC 19, removeNthFromEnd, Eliminar n-ésimo desde el final]
problem_id: 19
difficulty: medium
patron: linked-list
neetcode_order: 5
---

# LeetCode 19 — Remove Nth Node From End of List

> 🎯 **Quinto problema del patrón Linked List**. Introduce el **two-pointer con offset**: dos punteros separados por una distancia fija que avanzan al mismo ritmo. Patrón muy útil para "k-ésimo desde el final" sin pasar dos veces por la lista.

## Enunciado

Dada la cabeza de una linked list, **elimina el n-ésimo nodo desde el final** y devuelve la cabeza.

**Ejemplo 1:**
```
Input:  1 → 2 → 3 → 4 → 5, n = 2
Output: 1 → 2 → 3 → 5 (eliminado el 4)
```

**Ejemplo 2:**
```
Input:  1, n = 1
Output: None (lista vacía)
```

**Restricciones:**
- Número de nodos en `[1, 30]`.
- `1 <= n <= sz` (n siempre válido).

---

## Solución 1 — Two-pass (longitud + eliminar)

```python
class Solution:
    def removeNthFromEnd(self, head, n):
        # Pasada 1: contar
        length = 0
        curr = head
        while curr:
            length += 1
            curr = curr.next

        # Pasada 2: eliminar el (length-n)-ésimo desde el principio
        target = length - n
        if target == 0:
            return head.next                 # eliminar la cabeza

        curr = head
        for _ in range(target - 1):
            curr = curr.next
        curr.next = curr.next.next            # saltar el target

        return head
```

**Análisis:** O(n) tiempo, O(1) espacio. Funciona pero **dos pasadas**.

---

## Solución 2 — One-pass con dos punteros (la canónica)

**La idea**: dos punteros separados por `n+1` nodos. Cuando el rápido llegue al final (None), el lento estará justo **antes** del nodo a eliminar.

```python
class Solution:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head)            # dummy para manejar caso "eliminar cabeza"
        slow = fast = dummy

        # Avanzar fast n+1 pasos
        for _ in range(n + 1):
            fast = fast.next

        # Avanzar ambos hasta que fast sea None
        while fast:
            slow = slow.next
            fast = fast.next

        # slow está justo antes del nodo a eliminar
        slow.next = slow.next.next

        return dummy.next
```

**Trace mental con `1 → 2 → 3 → 4 → 5, n = 2`**:

```
dummy → 1 → 2 → 3 → 4 → 5

Avanzar fast n+1=3 pasos:
slow=dummy, fast=3

Avanzar ambos hasta fast=None:
slow=1, fast=4
slow=2, fast=5
slow=3, fast=None  ← slow está antes del nodo a eliminar (4)

slow.next = slow.next.next  →  3.next = 5

Resultado: dummy → 1 → 2 → 3 → 5 ✅
```

**Análisis:**
- **Tiempo: O(n)** — una sola pasada.
- **Espacio: O(1)**.
- **Veredicto:** ✅ **la canónica**.

### Por qué `n + 1` y no `n`

Necesitamos que `slow` quede en el nodo **anterior** al que eliminamos (para hacer `slow.next = slow.next.next`). El offset `n+1` lo garantiza.

### Por qué `dummy`

Si eliminamos la cabeza (`n == length`), sin dummy tendríamos que tratar caso especial. Con dummy, `dummy.next` siempre es la cabeza correcta al final.

---

## El patrón general — "Two pointers con offset"

**Cuándo aplicar**:

> Cuando necesitas el k-ésimo elemento desde el final (o desde una posición dinámica) de una linked list, sin recorrer dos veces.

**Plantilla mental**:

```python
slow = fast = dummy
for _ in range(offset):
    fast = fast.next
while fast:
    slow = slow.next
    fast = fast.next
# slow está en posición offset desde el final
```

---

## Auto-test

1. Escribe la Solución 2 desde cero.
2. Justifica el `n + 1` (no `n`).
3. Justifica el dummy node.
4. Trace mental con n=1 (eliminar último), n=length (eliminar cabeza).

---

## Conexiones

- [[206-reverse-linked-list]], [[141-linked-list-cycle]] — patrones de slow/fast.
- Próximo: [[138-copy-list-with-random-pointer]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificado n+1 y dummy
- [ ] Resuelto en LeetCode con éxito
