---
title: "LeetCode 141 — Linked List Cycle"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/linked-list, patron/slow-fast, patron/floyd-cycle]
type: nota
status: en-progreso
source: claude-code
aliases: [Linked List Cycle, LC 141, hasCycle, Detectar ciclo en lista, Floyd tortuga liebre]
problem_id: 141
difficulty: easy
patron: linked-list
neetcode_order: 3
---

# LeetCode 141 — Linked List Cycle

> **Tercer problema del patrón Linked List** y la introducción al **algoritmo de Floyd (tortoise and hare)** — uno de los algoritmos más bonitos de toda la informática. Lo verás también en [[287-find-the-duplicate-number]] y [[143-reorder-list]].

## Enunciado

Dada la cabeza de una linked list, determina si tiene un **ciclo**.

Hay ciclo si algún nodo en la lista puede ser alcanzado **siguiendo punteros next repetidamente**. (Internamente, hay un nodo cuyo `next` apunta a otro nodo anterior en la lista en lugar de a `None`.)

**Ejemplo 1:**
```
Input: 3 → 2 → 0 → -4 ┐
              ↑       │
              └───────┘
Output: True (hay ciclo)
```

**Ejemplo 2:**
```
Input: 1 → 2 → None
Output: False
```

**Plantilla:**
```python
class Solution:
    def hasCycle(self, head):
        ...
```

---

## Solución 1 — Hash set de visitados

```python
class Solution:
    def hasCycle(self, head):
        seen = set()
        while head:
            if head in seen:
                return True
            seen.add(head)
            head = head.next
        return False
```

**Análisis:**
- **Tiempo: O(n)**, **Espacio: O(n)**.
- **Veredicto:** funciona, fácil. Pero NO óptima en espacio.

---

## Solución 2 — Floyd's tortoise and hare (la canónica)

**La idea brillante**: dos punteros `slow` y `fast`. `slow` avanza 1 paso, `fast` avanza 2. Si hay ciclo, `fast` "alcanzará" a `slow` dentro del ciclo. Si no hay ciclo, `fast` llegará a `None`.

```python
class Solution:
    def hasCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True
        return False
```

**Por qué funciona**: imagina dos corredores en una pista circular, uno al doble de velocidad. Si la pista es circular (ciclo), el rápido **siempre alcanza** al lento dentro del primer giro. Si la pista es recta (sin ciclo), el rápido se sale del extremo (`None`) primero.

**Análisis:**
- **Tiempo: O(n)** — el rápido llega al final o alcanza al lento en O(n).
- **Espacio: O(1)** — solo dos punteros.
- **Veredicto:** [OK] **la canónica**. La que demuestra dominio del problema.

### Las dos guardias críticas

```python
while fast and fast.next:
```

- `fast` puede ser None (lista vacía o llega al final).
- `fast.next` puede ser None (un solo paso antes del final).

Sin estas guardias, `fast.next.next` daría error en listas sin ciclo.

---

## Variante — LC 142: dónde empieza el ciclo

LC 142 pide el nodo donde empieza el ciclo (no solo si existe). Tras la detección con Floyd:

```python
# Después de encontrar el punto de encuentro (slow == fast):
ptr1 = head
ptr2 = slow                                 # punto de encuentro
while ptr1 != ptr2:
    ptr1 = ptr1.next
    ptr2 = ptr2.next
return ptr1                                  # inicio del ciclo
```

Es **matemática pura**: la distancia desde head al inicio del ciclo es igual a la distancia desde el punto de encuentro al inicio del ciclo. Resolver en papel para entenderlo.

---

## El patrón general — "Slow / fast pointers"

**Cuándo aplicar**:

> Cuando trabajas con linked lists y necesitas detectar ciclos, encontrar la mitad, o el k-ésimo desde el final.

**Aplicaciones**:

| Problema | Uso de slow/fast |
|---|---|
| LC 141 / 142 — Cycle detection | Detectar / encontrar inicio |
| LC 876 — Middle of Linked List | Slow llega al medio cuando fast llega al final |
| LC 19 — Remove Nth from end | Fast avanza n primero, después juntos |
| LC 287 — Find Duplicate | Detección de ciclo en array |

---

## Auto-test

1. Escribe la Solución 2 desde cero.
2. Justifica las dos guardias `fast and fast.next`.
3. Demuestra (informalmente) por qué fast siempre alcanza a slow si hay ciclo.
4. **Bonus** — implementa LC 142 (encontrar inicio del ciclo).

---

## Conexiones

- Próximo: [[143-reorder-list]] — slow/fast + reverse.
- [[287-find-the-duplicate-number]] — Floyd sobre array.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificadas las guardias
- [ ] Resuelto en LeetCode con éxito
