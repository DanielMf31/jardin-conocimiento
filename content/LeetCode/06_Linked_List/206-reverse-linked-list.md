---
title: "LeetCode 206 — Reverse Linked List"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/linked-list, patron/punteros]
type: nota
status: en-progreso
source: claude-code
aliases: [Reverse Linked List, LC 206, reverseList, Invertir lista enlazada]
problem_id: 206
difficulty: easy
patron: linked-list
neetcode_order: 1
---

# LeetCode 206 — Reverse Linked List

> **Primer problema del patrón Linked List** — y **el más importante del bloque**. Reverse Linked List aparece como sub-rutina en muchos problemas posteriores (LC 143 Reorder List, LC 25 Reverse Nodes in K-Group, LC 234 Palindrome Linked List). Si lo dominas, te ahorra trabajo en 3-4 problemas más adelante.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Recordatorio: la estructura `ListNode`

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

Un nodo tiene un valor (`val`) y un puntero al siguiente (`next`). El último nodo apunta a `None`.

```
1 → 2 → 3 → 4 → 5 → None
```

## Enunciado

Dada la cabeza (`head`) de una lista enlazada simple, **invierte la lista** y devuelve la nueva cabeza.

**Ejemplo 1:**
```
Input:  1 → 2 → 3 → 4 → 5 → None
Output: 5 → 4 → 3 → 2 → 1 → None
```

**Ejemplo 2:**
```
Input:  1 → 2 → None
Output: 2 → 1 → None
```

**Ejemplo 3:**
```
Input:  None
Output: None
```

**Restricciones:**
- Número de nodos en `[0, 5000]`.
- `-5000 <= Node.val <= 5000`.

**Plantilla:**
```python
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        ...
```

---

## Solución 1 — Iterativo con 3 punteros (la canónica)

**La idea**: mantener 3 punteros (`prev`, `curr`, `next_temp`) y "voltear" cada `next` mientras avanzas.

```python
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev = None
        curr = head
        while curr:
            next_temp = curr.next       # 1. guardar el siguiente
            curr.next = prev            # 2. invertir el puntero
            prev = curr                 # 3. avanzar prev
            curr = next_temp            # 4. avanzar curr
        return prev                     # prev es la nueva cabeza
```

**Trace mental con `1 → 2 → 3 → None`**:

```
Inicial: prev=None, curr=1

Iter 1: next_temp=2, 1.next=None, prev=1, curr=2
        Estado: None ← 1   2 → 3 → None
                       prev curr

Iter 2: next_temp=3, 2.next=1, prev=2, curr=3
        Estado: None ← 1 ← 2   3 → None
                            prev curr

Iter 3: next_temp=None, 3.next=2, prev=3, curr=None
        Estado: None ← 1 ← 2 ← 3
                              prev

Loop termina. Return prev = 3.

Lista resultante: 3 → 2 → 1 → None [OK]
```

**Análisis:**
- **Tiempo: O(n)** — un recorrido.
- **Espacio: O(1)** — tres punteros.
- **Veredicto:** [OK] **la canónica**.

### Las 4 líneas del bucle — memorízalas

```python
next_temp = curr.next       # GUARDAR (sin esto, perdemos el resto)
curr.next = prev            # INVERTIR (lo que cambia el rumbo)
prev = curr                 # AVANZAR prev
curr = next_temp            # AVANZAR curr
```

El orden importa: si haces `curr.next = prev` ANTES de guardar `next_temp`, pierdes el resto de la lista.

---

## Solución 2 — Recursivo (también canónica, alternativa)

```python
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return head                              # base: 0 o 1 nodo

        new_head = self.reverseList(head.next)       # invertir el resto
        head.next.next = head                        # nodo siguiente apunta a head
        head.next = None                             # head apunta a None (será el último)
        return new_head
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(n)** — call stack de recursión (¡no es O(1)!).
- **Veredicto:** [OK] elegante. **Pero**: en entrevista, prefiere la iterativa por el O(1) espacio.

---

## El patrón general — "3-pointer reverse"

**Cuándo aplicar**:

> Cuando necesitas invertir una linked list (entera o un segmento), o avanzar en una lista mientras modificas punteros.

**Plantilla mental**:

```python
def reverse(head):
    prev = None
    curr = head
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    return prev
```

**Memorízala** — la vas a usar 4-5 veces más en LeetCode.

---

## Variaciones / problemas que la usan internamente

| Problema | Cómo usa reverse |
|---|---|
| **LC 92. Reverse Linked List II** | Invierte solo un segmento entre posiciones m y n |
| **LC 143. Reorder List** | Reverse la segunda mitad |
| **LC 234. Palindrome Linked List** | Reverse para comparar |
| **LC 25. Reverse Nodes in K-Group** | Reverse en bloques de k |

---

## Auto-test

1. Escribe la **Solución 1** desde cero **5 veces** sin equivocarte (es la base de muchas otras).
2. Justifica por qué guardar `next_temp` antes de hacer `curr.next = prev`.
3. Trace mental con `1 → 2 → None`.
4. **Bonus** — implementa "reverse from position m to n" (LC 92).

---

## Solución en C++ — contraste con Python

> Añadido para ver las diferencias de lenguaje. **Aquí es donde C++ más diverge de Python**: punteros crudos y gestión de memoria. Código compilable en [`206-reverse-linked-list.cpp`](206-reverse-linked-list.cpp).

```cpp
struct ListNode { int val; ListNode* next; };

class Solution {
 public:
  ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    while (head != nullptr) {
      ListNode* next = head->next;   // guardar antes de reapuntar
      head->next = prev;             // invertir el enlace
      prev = head;
      head = next;
    }
    return prev;
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(1) — igual que el Python iterativo.

**Diferencias clave Python ↔ C++:**
- El nodo es `ListNode*` (puntero crudo); `node.next` → `node->next` (flecha para desreferenciar puntero).
- `None` → `nullptr`. `while head:` → `while (head != nullptr)`.
- El algoritmo es idéntico, pero en C++ **tú gestionas la memoria**: en producción no usarías `new`/`delete` crudos sino `std::unique_ptr<ListNode>` (ownership). En Python el GC libera los nodos solo.
- Reasignar 3 punteros (`prev/next/head`) es la misma "danza" que en Python; la diferencia es semántica de puntero, no el algoritmo.

---

## Conexiones

- [[MOC_NeetCode_150]].
- Próximo: [[21-merge-two-sorted-lists]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 1 desde cero 5 veces
- [ ] Trace mental con 3 nodos
- [ ] Resuelto en LeetCode con éxito
