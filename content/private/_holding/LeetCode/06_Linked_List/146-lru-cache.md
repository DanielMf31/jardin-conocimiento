---
title: "LeetCode 146 — LRU Cache"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/linked-list, patron/diseno-clase, patron/hash-map, patron/doubly-linked-list]
type: nota
status: en-progreso
source: claude-code
aliases: [LRU Cache, LC 146, LRUCache, Least Recently Used]
problem_id: 146
difficulty: medium
patron: linked-list
neetcode_order: 9
---

# LeetCode 146 — LRU Cache

> **Noveno problema del patrón Linked List** — y **uno de los problemas de diseño MÁS preguntados en entrevistas tecnicas** de toda la historia. La solución óptima combina **doubly linked list + hash map** para tener get/put en O(1). Es uno de los pocos problemas donde implementarlo te enseña algo de un sistema real (cachés en CPUs, Redis, sistemas operativos).

## Enunciado

Diseña una estructura LRU (Least Recently Used) cache con capacidad fija. Soporta:

- `get(key)` — devuelve el valor de la key si existe, si no `-1`. **Esto cuenta como "uso reciente"**.
- `put(key, value)` — actualiza si existe, inserta si no. Si llena, **expulsa la key menos recientemente usada**.

**Ambas operaciones deben ser O(1).**

**Ejemplo:**
```
LRUCache(capacity = 2)
put(1, 1)        # cache = {1=1}
put(2, 2)        # cache = {1=1, 2=2}
get(1)           # 1, cache = {2=2, 1=1} (1 ahora es el más reciente)
put(3, 3)        # capacidad llena, expulsa 2 → cache = {1=1, 3=3}
get(2)           # -1
put(4, 4)        # capacidad llena, expulsa 1 → cache = {3=3, 4=4}
```

**Restricciones:**
- `1 <= capacity <= 3000`.
- Hasta 2*10^5 llamadas.

---

## Solución 1 — Doubly Linked List + HashMap (la canónica)

**La idea**: necesitamos O(1) para:
- Mover un nodo al frente (más reciente). Solo es O(1) si tienes acceso directo al nodo y es **doubly linked**.
- Acceder por key. Hash map.

**Estructura mental**:

```
HashMap: key → nodo en la linked list
DLL: head ⇄ [más reciente] ⇄ ... ⇄ [menos reciente] ⇄ tail

(head y tail son DUMMY nodes para evitar casos especiales en bordes)
```

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}                              # key → Node
        self.head = Node()                           # dummy
        self.tail = Node()                           # dummy
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)                     # mover al frente (recién usado)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])

        node = Node(key, value)
        self.cache[key] = node
        self._add_to_front(node)

        if len(self.cache) > self.cap:
            # Expulsar el menos reciente (justo antes del tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

**Análisis:**
- **get / put: O(1)** ambas operaciones.
- **Espacio: O(capacity)**.
- **Veredicto:** [OK] **la canónica**. La que demuestra dominio total del problema.

### Por qué doubly linked list (no singly)

Para **eliminar un nodo en O(1)** dado el nodo (no el índice), necesitas acceso al `prev` para reconectar. Singly linked list requeriría buscar el `prev` (O(n)).

### Por qué dos dummy nodes (head, tail)

Evitan casos especiales en bordes (insertar al frente cuando lista vacía, eliminar al final cuando hay un solo nodo). Con dummies, **toda operación es uniforme**.

---

## Solución 2 — `OrderedDict` (atajo Python)

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)                   # marcar como reciente
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)            # FIFO: el más antiguo
```

**Análisis:** O(1) ambas operaciones (OrderedDict internamente usa doubly linked list + hash).

**Veredicto:** [OK] funciona y es 1/4 del código. **PERO**: en entrevista, **NO la uses**. El entrevistador quiere ver que sabes implementar LRU desde cero (que entiendes la estructura interna). Úsala solo si te lo permiten explícitamente o si ya implementaste la 1 antes.

---

## Auto-test

1. Implementa la Solución 1 desde cero. Es laboriosa, dale 1+ hora.
2. Justifica:
   - Por qué doubly linked list y no singly.
   - Por qué dos dummy nodes.
   - Por qué `_remove` y `_add_to_front` son ambas O(1).
3. Trace mental con: put(1,1), put(2,2), get(1), put(3,3), get(2).

---

## Conexiones

- [[155-min-stack]] — diseño de clase.
- Próximo: [[23-merge-k-sorted-lists]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Implementada Solución 1 desde cero (date 1+ hora)
- [ ] Justificada cada decisión de diseño
- [ ] Resuelto en LeetCode con éxito
