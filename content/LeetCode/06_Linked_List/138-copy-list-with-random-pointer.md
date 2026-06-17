---
title: "LeetCode 138 — Copy List with Random Pointer"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/linked-list, patron/hash-map, patron/deep-copy]
type: nota
status: en-progreso
source: claude-code
aliases: [Copy List Random Pointer, LC 138, copyRandomList, Copia profunda lista]
problem_id: 138
difficulty: medium
patron: linked-list
neetcode_order: 6
---

# LeetCode 138 — Copy List with Random Pointer

> **Sexto problema del patrón Linked List**. Es el **caso clásico de deep copy** con punteros que apuntan a sitios "arbitrarios". El truco mental: **separar creación de nodos de creación de relaciones** mediante un mapa old→new.

## Enunciado

Una linked list con nodos de la forma `Node(val, next, random)`, donde `random` puede apuntar a cualquier nodo de la lista (o `None`).

Construye una **deep copy** de la lista. Ningún nodo de la copia debe ser el mismo objeto que un nodo del original — todos los punteros (next y random) deben apuntar a nodos NUEVOS.

**Ejemplo:**
```
Input:  [[7,null], [13,0], [11,4], [10,2], [1,0]]
        (cada par es [val, índice del random; null si None])
Output: copia profunda con misma estructura
```

---

## Solución 1 — Hash map old → new (la canónica)

**Idea**: dos pasadas:
1. Crear todos los nodos nuevos y mapear `old → new` en un dict.
2. Conectar `next` y `random` de cada nuevo usando el dict.

```python
class Solution:
    def copyRandomList(self, head):
        if not head:
            return None

        # Pasada 1: crear nodos y mapear
        old_to_new = {}
        curr = head
        while curr:
            old_to_new[curr] = Node(curr.val)
            curr = curr.next

        # Pasada 2: conectar next y random
        curr = head
        while curr:
            old_to_new[curr].next = old_to_new.get(curr.next)
            old_to_new[curr].random = old_to_new.get(curr.random)
            curr = curr.next

        return old_to_new[head]
```

**Análisis:**
- **Tiempo: O(n)** — dos pasadas.
- **Espacio: O(n)** — el dict.
- **Veredicto:** [OK] **la canónica**. Limpia y fácil.

> **`dict.get(curr.next)`** devuelve `None` si `curr.next` es `None`, evitando KeyError.

---

## Solución 2 — One-pass con defaultdict pythonic

```python
from collections import defaultdict

class Solution:
    def copyRandomList(self, head):
        old_to_new = defaultdict(lambda: Node(0))
        old_to_new[None] = None                      # mapeo especial

        curr = head
        while curr:
            old_to_new[curr].val = curr.val
            old_to_new[curr].next = old_to_new[curr.next]
            old_to_new[curr].random = old_to_new[curr.random]
            curr = curr.next

        return old_to_new[head]
```

**Análisis:** mismo O(n). Más compacta. **Trampa**: el `defaultdict` crea nodos sobre la marcha.

---

## Solución 3 — Interleaving (O(1) espacio extra)

**La idea brillante**: en lugar de un dict, intercalar cada nodo nuevo justo después del original:

```
Antes:  A → B → C
Tras paso 1:  A → A' → B → B' → C → C'
```

Después, los `random` se asignan: `A'.random = A.random.next`. Luego se separan las dos listas.

```python
class Solution:
    def copyRandomList(self, head):
        if not head: return None

        # Paso 1: crear copia entrelazada
        curr = head
        while curr:
            new = Node(curr.val, curr.next)
            curr.next = new
            curr = new.next

        # Paso 2: asignar random
        curr = head
        while curr:
            if curr.random:
                curr.next.random = curr.random.next
            curr = curr.next.next

        # Paso 3: separar las dos listas
        new_head = head.next
        curr = head
        while curr:
            new = curr.next
            curr.next = new.next
            new.next = new.next.next if new.next else None
            curr = curr.next

        return new_head
```

**Análisis:** O(n) tiempo, **O(1) espacio** extra (excluyendo la lista de salida).

**Veredicto:** elegante pero **más fácil de bug**. La Solución 1 (hash map) es preferida en entrevista por claridad.

---

## Auto-test

1. Escribe la Solución 1 desde cero.
2. Justifica las dos pasadas (¿por qué no se puede en una?).
3. Justifica el `dict.get(curr.next)` en lugar de `dict[curr.next]`.

---

## Conexiones

- [[1-two-sum]] — primer encuentro con dict como mapa.
- Próximo: [[2-add-two-numbers]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 1 desde cero
- [ ] Resuelto en LeetCode con éxito
