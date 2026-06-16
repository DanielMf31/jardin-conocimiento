---
title: "LeetCode 21 — Merge Two Sorted Lists"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/linked-list, patron/dummy-node]
type: nota
status: en-progreso
source: claude-code
aliases: [Merge Two Sorted Lists, LC 21, mergeTwoLists, Fusionar dos listas ordenadas]
problem_id: 21
difficulty: easy
patron: linked-list
neetcode_order: 2
---

# LeetCode 21 — Merge Two Sorted Lists

> 🎯 **Segundo problema del patrón Linked List**. Introduce el **dummy node** (nodo centinela), un truco fundamental para evitar casos especiales al construir una lista. **Es la sub-rutina** de LC 23 (Merge K Sorted Lists) y LC 148 (Sort List).

## Enunciado

Te dan las cabezas de **dos listas enlazadas ordenadas** `list1` y `list2`. Fusiónalas en una sola lista ordenada y devuelve su cabeza.

**Ejemplo 1:**
```
Input:  list1 = 1 → 2 → 4
        list2 = 1 → 3 → 4
Output: 1 → 1 → 2 → 3 → 4 → 4
```

**Restricciones:**
- Nodos en `[0, 50]`.
- `-100 <= Node.val <= 100`.
- Ambas listas están **ordenadas crecientes**.

**Plantilla:**
```python
class Solution:
    def mergeTwoLists(self, list1, list2):
        ...
```

---

## Entender linked lists antes de codear (sección de fondo)

> 📚 **Si las linked lists todavía te confunden, lee esto antes de las soluciones**. Una vez tienes el modelo mental de "variables como flechas" y dominas el dummy node, todos los problemas del patrón Linked List (11 en total) se vuelven mecánicos. Esta sección sirve para los 3 primeros (206, 21, 141) — los que interiorizan el modelo.

### 1. Qué es una linked list realmente (modelo mental)

Una **linked list NO es como un array**. Olvida los índices. Piensa en **cajas conectadas con flechas**.

```
ARRAY [1, 2, 4]:
  Memoria contigua, accedes por índice

  ┌───┬───┬───┐
  │ 1 │ 2 │ 4 │
  └───┴───┴───┘
   [0] [1] [2]


LINKED LIST 1 → 2 → 4:
  Cajas en cualquier sitio de memoria,
  cada una contiene UN VALOR + UNA FLECHA al siguiente

  ┌───┬───┐    ┌───┬───┐    ┌───┬───┐
  │ 1 │ ●─┼───→│ 2 │ ●─┼───→│ 4 │ ●─┼───→ None
  └───┴───┘    └───┴───┘    └───┴───┘
```

Cada caja se llama **nodo** y tiene 2 atributos:
- `node.val` → el valor (el número)
- `node.next` → la flecha al siguiente (otro nodo, o `None`)

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

**Lo que confunde**: cuando "tienes la lista" en realidad **solo tienes el primer nodo** (la "cabeza", `head`). Para llegar al resto, tienes que **caminar** siguiendo las flechas: `head.next.next.next...`. No hay índices. No hay `len()` directo.

**Operaciones básicas**:
```
"Avanzar al siguiente":   curr = curr.next
"Leer el valor actual":   curr.val
"Conectar A → B":         A.next = B
"Cortar la conexión":     A.next = None
"¿Es el final?":          curr is None
```

### 2. La clave del éxito: visualizar punteros como variables-flecha

Esta es **LA MEJOR RECETA mental** para no perderte:

> **Una variable que apunta a un nodo NO es el nodo. Es una flecha que apunta al nodo.**

```
Si tienes:
    list1 = (nodo con valor 1)

Visualízalo así:
    list1 ──→ ┌───┬───┐
              │ 1 │ ●─┼──→ ...
              └───┴───┘

NO así:
    list1 = ┌───┬───┐
            │ 1 │ ●─┼──→ ...
            └───┴───┘
```

Cuando haces `list1 = list1.next`, **NO mueves el nodo** — mueves la flecha de la variable a otro nodo:

```
ANTES:
    list1 ──→ ┌───┬───┐    ┌───┬───┐    ┌───┬───┐
              │ 1 │ ●─┼───→│ 2 │ ●─┼───→│ 4 │ ●─┼──→ None
              └───┴───┘    └───┴───┘    └───┴───┘

list1 = list1.next:
    list1 ─────────────────→ ┌───┬───┐    ┌───┬───┐
                             │ 2 │ ●─┼───→│ 4 │ ●─┼──→ None
                             └───┴───┘    └───┴───┘
              (el nodo 1 sigue existiendo en memoria,
               solo que list1 ya no apunta a él)
```

Si entiendes esto, ya está. El resto es coreografía de flechas.

### 3. Visualización del problema 21

```
Input:
    list1 ──→ ┌───┬───┐    ┌───┬───┐    ┌───┬───┐
              │ 1 │ ●─┼───→│ 2 │ ●─┼───→│ 4 │ ●─┼──→ None
              └───┴───┘    └───┴───┘    └───┴───┘

    list2 ──→ ┌───┬───┐    ┌───┬───┐    ┌───┬───┐
              │ 1 │ ●─┼───→│ 3 │ ●─┼───→│ 4 │ ●─┼──→ None
              └───┴───┘    └───┴───┘    └───┴───┘

Output (UNA sola lista, ordenada):
              ┌───┬───┐  ┌───┬───┐  ┌───┬───┐  ┌───┬───┐  ┌───┬───┐  ┌───┬───┐
    head ──→  │ 1 │ ●┼─→│ 1 │ ●┼─→│ 2 │ ●┼─→│ 3 │ ●┼─→│ 4 │ ●┼─→│ 4 │ ●┼─→ None
              └───┴───┘  └───┴───┘  └───┴───┘  └───┴───┘  └───┴───┘  └───┴───┘
```

**El truco mental**: NO creas nodos nuevos. **Reutilizas los nodos que ya tienes**, simplemente **cambias hacia dónde apuntan sus flechas**. Es como cambiar las vías de un tren para que los vagones queden en el orden correcto.

### 4. La idea: dos punteros que avanzan + un puntero que construye

```
ESTRATEGIA:
  1. Pones un dedo en list1 y otro en list2 (al inicio de cada una).
  2. Comparas los valores en los dedos.
  3. El menor lo "enganchas" al final de tu nueva lista.
  4. Avanzas el dedo de la lista de la que cogiste.
  5. Repites hasta que un dedo llegue al final.
  6. Lo que quede de la otra lista lo enganchas entero al final.

PROBLEMA AL CONSTRUIR LA NUEVA LISTA:
  Necesitas saber DÓNDE acabar de enganchar.
  → Para eso usas el puntero "tail" (cola).

PROBLEMA CON EL PRIMER NODO:
  La primera vez que enganchas, no tienes "anterior" todavía.
  → ¿De dónde sale la cabeza de la nueva lista?
  → Aquí entra el dummy node (el truco del genio).
```

### 5. El dummy node — el truco que lo hace todo uniforme

**Sin dummy** tendrías que escribir código así de feo:

```python
# Sin dummy — caso especial para la primera iteración
if list1.val <= list2.val:
    head = list1            # primera vez es distinta
    list1 = list1.next
else:
    head = list2
    list2 = list2.next
tail = head
while list1 and list2:
    # ... lógica de las siguientes ...
```

**Con dummy** todas las iteraciones son IDÉNTICAS:

```python
dummy = ListNode()    # nodo "fantasma" con val=0, no significa nada
tail = dummy          # tail empieza apuntando al fantasma

# Ahora todas las iteraciones funcionan igual
while list1 and list2:
    if list1.val <= list2.val:
        tail.next = list1   # el fantasma se "convierte" en padre del primero
        list1 = list1.next
    else:
        tail.next = list2
        list2 = list2.next
    tail = tail.next

# Al final, tu respuesta es lo que viene DESPUÉS del fantasma
return dummy.next  # ignoras el fantasma
```

**Visualización del dummy en acción**:

```
INICIAL:
    dummy ──→ ┌───┬───┐
              │ 0 │ ●─┼──→ None       (nodo fantasma, val=0 da igual)
              └───┴───┘

    tail ─────↑  (apunta al mismo sitio que dummy)

    list1 ──→ 1 → 2 → 4
    list2 ──→ 1 → 3 → 4

TRAS PRIMERA ITERACIÓN (1 ≤ 1, cogemos de list1):
    dummy ──→ ┌───┬───┐    ┌───┬───┐
              │ 0 │ ●─┼───→│ 1 │ ●─┼──→ 2 → 4
              └───┴───┘    └───┴───┘
                            ↑
                           tail

    list1 ──→ 2 → 4
    list2 ──→ 1 → 3 → 4

✨ El dummy nunca cambia, sigue apuntando al fantasma.
   tail va avanzando por la lista nueva.
```

### 6. Trace COMPLETO con flechas — `list1=[1,2,4]`, `list2=[1,3,4]`

Lee este trace despacio. Es lo que de verdad enseña.

```
═══════════════════════════════════════════════════════════════
ESTADO INICIAL
═══════════════════════════════════════════════════════════════

    dummy ──→ [0|●] ──→ None
              ↑
             tail

    list1 ──→ [1|●] ──→ [2|●] ──→ [4|●] ──→ None
    list2 ──→ [1|●] ──→ [3|●] ──→ [4|●] ──→ None


═══════════════════════════════════════════════════════════════
ITERACIÓN 1: list1.val=1, list2.val=1, 1 ≤ 1 → cogemos de list1
═══════════════════════════════════════════════════════════════

Paso A: tail.next = list1
   (la flecha de tail apunta ahora al nodo 1 de list1)

    dummy ──→ [0|●] ──→ [1|●] ──→ [2|●] ──→ [4|●] ──→ None
              ↑
             tail        list1 ──→ [1|●] ──→ [2|●] ──→ [4|●] ──→ None
                                   (mismo nodo de arriba — UN solo nodo,
                                    dos variables apuntándole)

Paso B: list1 = list1.next
   (la flecha de list1 avanza al nodo 2)

    dummy ──→ [0|●] ──→ [1|●] ──→ [2|●] ──→ [4|●] ──→ None
              ↑                    ↑
             tail                 list1

Paso C: tail = tail.next
   (la flecha de tail avanza también al nodo 1)

    dummy ──→ [0|●] ──→ [1|●] ──→ [2|●] ──→ [4|●] ──→ None
                        ↑          ↑
                       tail       list1

    list2 ──→ [1|●] ──→ [3|●] ──→ [4|●] ──→ None     (sin tocar)


═══════════════════════════════════════════════════════════════
ITERACIÓN 2: list1.val=2, list2.val=1, 2 > 1 → cogemos de list2
═══════════════════════════════════════════════════════════════

Paso A: tail.next = list2
   (la flecha de tail (nodo 1 de list1) ahora apunta al nodo 1 de list2)

                                    ╭──→ [1|●] ──→ [3|●] ──→ [4|●] → None
    dummy ──→ [0|●] ──→ [1|●] ──→ ──╯       ↑
                        ↑                  list2
                       tail
                                    [2|●] ──→ [4|●] ──→ None  (huérfano!)
                                     ↑
                                    list1

   ⚠️ ¡OJO! El nodo 2 quedó "desconectado" temporalmente,
   pero list1 todavía lo apunta. Lo recogeremos en la próxima iter.

Paso B: list2 = list2.next

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [3|●] ──→ [4|●] → None
                                              ↑
                                             list2

Paso C: tail = tail.next

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [3|●] ──→ [4|●] → None
                                  ↑           ↑
                                 tail        list2

   list1 sigue apuntando a [2|●]


═══════════════════════════════════════════════════════════════
ITERACIÓN 3: list1.val=2, list2.val=3, 2 ≤ 3 → cogemos de list1
═══════════════════════════════════════════════════════════════

Paso A: tail.next = list1

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [2|●] ──→ [4|●] → None
                                              ↑
                                            (tail antes)

   ✨ ¡Importante! Al hacer tail.next = list1, REEMPLAZAMOS la flecha
   anterior que iba al [3|●]. El nodo 3 sigue existiendo y list2 lo apunta.

Paso B y C: list1 y tail avanzan

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [2|●] ──→ [4|●] → None
                                              ↑          ↑
                                             tail       list1

   list2 sigue apuntando a [3|●] ──→ [4|●] ──→ None


═══════════════════════════════════════════════════════════════
ITERACIÓN 4: list1.val=4, list2.val=3, 4 > 3 → cogemos de list2
═══════════════════════════════════════════════════════════════

Tras los 3 pasos:

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [2|●] ──→ [3|●] ──→ [4|●] → None
                                                         ↑          ↑
                                                       tail       list2
   list1 sigue apuntando a [4|●]


═══════════════════════════════════════════════════════════════
ITERACIÓN 5: list1.val=4, list2.val=4, 4 ≤ 4 → cogemos de list1
═══════════════════════════════════════════════════════════════

Tras los 3 pasos:

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [2|●] ──→ [3|●] ──→ [4|●] → None
                                                                  ↑
                                                                 tail
   list1 = None
   list2 sigue apuntando a [4|●]


═══════════════════════════════════════════════════════════════
SALE DEL WHILE (list1 es None)
═══════════════════════════════════════════════════════════════

Línea: tail.next = list1 if list1 else list2
       → list1 es None, así que: tail.next = list2

    dummy ──→ [0|●] ──→ [1|●] ──→ [1|●] ──→ [2|●] ──→ [3|●] ──→ [4|●] ──→ [4|●] → None
                                                                            ↑
                                                                          (lo que quedaba de list2)


═══════════════════════════════════════════════════════════════
RETURN dummy.next
═══════════════════════════════════════════════════════════════

dummy.next es el primer [1|●], así que la lista resultado es:

    [1|●] ──→ [1|●] ──→ [2|●] ──→ [3|●] ──→ [4|●] ──→ [4|●] ──→ None  ✅
```

**Lo importante a notar**:
1. **No creamos nodos nuevos** — todos los 6 nodos de la salida son los 6 nodos originales de las dos listas. Solo **cambiamos las flechas** entre ellos.
2. El **dummy** sigue ahí al final (lo descartamos con `dummy.next`), pero nunca le tocamos su valor — es un pivote temporal.
3. El **tail** es como una "pluma" que va escribiendo al final de la lista. Siempre apunta al **último nodo añadido**.

### 7. La trampa que se elimina — `tail.next = list1 if list1 else list2`

Esta línea final parece misteriosa pero hace algo elegante. Cuando salimos del while, **una de las dos listas se acabó**, pero la otra **todavía tiene nodos**. Esos nodos ya están conectados entre sí (la lista venía ordenada), así que basta con **engancharlos en bloque** al final.

```
Si list1 quedó vacía y list2 = [4]:

   La lista nueva: ... → [4|●] (último añadido) → None
                                    ↑
                                   tail

   Linea: tail.next = list2

   Resultado: ... → [4|●] ──→ [4|●] ──→ None
                              ↑
                       (lo que quedaba — engancha en cadena)

NO HAY QUE COPIAR uno por uno. Una sola asignación engancha
TODO el resto de la cola, porque ya estaba ordenado.
```

Esto explota la propiedad de las linked lists: **enganchar `tail.next = otro_nodo` engancha implícitamente todo lo que cuelga de `otro_nodo`**.

### 8. Trampas típicas que producen bugs

```
TRAMPA 1 — Olvidar avanzar tail:
   while list1 and list2:
       if ...
           tail.next = list1
           list1 = list1.next
           # ⚠️ FALTA: tail = tail.next
       else:
           ...

   → Bug: tail siempre apunta al dummy, todos los enganches
     se sobrescriben mutuamente. Lista final tiene 1 elemento.

TRAMPA 2 — Olvidar conectar el resto al final:
   while list1 and list2:
       ...
   # ⚠️ FALTA: tail.next = list1 if list1 else list2
   return dummy.next

   → Bug: la lista se corta en cuanto una de las dos se acaba.
     Pierdes los nodos restantes de la otra.

TRAMPA 3 — Hacer < en vez de <=:
   if list1.val < list2.val:    # debería ser <=
       ...

   → Estable vs no estable. En este problema no afecta al output
     pero en problemas relacionados (sort estable) sí. Costumbre <=.

TRAMPA 4 — Crear nodos nuevos en vez de reusar:
   tail.next = ListNode(list1.val)    # ⚠️ MAL

   → Funciona pero usa O(m+n) extra de memoria innecesariamente.
     La elegancia de este algoritmo es REUSAR nodos.
```

### 9. Por qué este problema es FUNDAMENTAL

Aprender bien el patrón "**dummy + tail + while two pointers**" desbloquea muchos otros:

| LeetCode | Cómo se relaciona |
|---|---|
| **23. Merge K Sorted Lists** | Aplicas `mergeTwoLists` k veces, o con heap |
| **148. Sort List** | Merge sort sobre linked list — usa esta función como sub-rutina |
| **2. Add Two Numbers** | Mismo patrón dummy+tail, pero sumando con carry |
| **86. Partition List** | Dummy node para construir 2 sublistas, luego concatenar |
| **24. Swap Nodes in Pairs** | Dummy + manipulación de punteros |
| **92. Reverse Linked List II** | Dummy para evitar caso especial al revertir desde head |

**Si dominas el dummy node, has dominado el patrón maestro de construcción de linked lists.**

### 10. Receta mental de cierre — para no liarte nunca con linked lists

```
LAS 5 REGLAS DE ORO:

1. Visualiza variables como FLECHAS, no como nodos.
   "list1 = list1.next" NO mueve el nodo. Mueve la flecha.

2. Cuando construyes una lista nueva: usa SIEMPRE dummy + tail.
   No hay caso especial para el primer nodo. Todo uniforme.

3. Cuando avances un puntero (tail = tail.next): hazlo SIEMPRE
   AL FINAL de la iteración, no al principio.

4. Cuando una operación pueda romper conexiones (next = otro_nodo):
   guarda lo que vas a perder ANTES, en una variable temporal.
   Ejemplo de 206: next_temp = curr.next antes de curr.next = prev.

5. "Caminar la lista" = bucle while curr: ... curr = curr.next.
   Termina cuando curr is None.
```

---

## Solución 1 — Iterativo con dummy node (la canónica)

**La idea clave**: crear un **nodo dummy** que actúa como "cabeza falsa". Construir la lista enganchando nodos a este dummy. Al final, la respuesta es `dummy.next`.

**Por qué dummy**: sin él, tendrías un caso especial al elegir la primera cabeza (¿es de list1 o list2?). Con dummy, **toda iteración es uniforme**.

```python
class Solution:
    def mergeTwoLists(self, list1, list2):
        dummy = ListNode()              # nodo falso
        tail = dummy

        while list1 and list2:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next

        # Anexar lo que quede
        tail.next = list1 if list1 else list2

        return dummy.next                # saltar el dummy
```

**Trace mental con `[1,2,4]` y `[1,3,4]`**:

```
dummy = (0) → None
tail = dummy

Iter 1: 1 ≤ 1 → tail.next = list1(1), list1=2, tail=1
        Estado: dummy → 1 → 2 → 4

Iter 2: 2 > 1 → tail.next = list2(1), list2=3, tail=1(b)
        Estado: dummy → 1 → 1 → 3 → 4

Iter 3: 2 ≤ 3 → tail.next = list1(2), list1=4, tail=2
        ...

Final: dummy → 1 → 1 → 2 → 3 → 4 → 4
return dummy.next ✅
```

**Análisis:**
- **Tiempo: O(m + n)**.
- **Espacio: O(1)** — solo dummy y tail.
- **Veredicto:** ✅ **la canónica**.

### Por qué `dummy = ListNode()` y `return dummy.next`

```python
dummy = ListNode()                  # crea nodo con val=0, next=None
# ... construyes lista enganchando a dummy.next ...
return dummy.next                   # devuelves saltándote el dummy
```

El dummy **nunca aparece en la salida** — es solo un pivote interno para no tener caso especial con la cabeza.

---

## Solución 2 — Recursivo (alternativa elegante)

```python
class Solution:
    def mergeTwoLists(self, list1, list2):
        if not list1: return list2
        if not list2: return list1
        if list1.val <= list2.val:
            list1.next = self.mergeTwoLists(list1.next, list2)
            return list1
        else:
            list2.next = self.mergeTwoLists(list1, list2.next)
            return list2
```

**Análisis:**
- **Tiempo: O(m + n)**.
- **Espacio: O(m + n)** — call stack.
- **Veredicto:** elegante pero gasta más memoria. La iterativa es preferible.

---

## El patrón general — "Dummy node + tail pointer"

**Cuándo aplicar**:

> Cuando construyes una linked list iterativamente y no quieres tratar el caso especial de "la primera vez que añado un nodo".

**Plantilla mental**:

```python
dummy = ListNode()
tail = dummy
while condicion:
    tail.next = nuevo_nodo
    tail = tail.next
return dummy.next
```

Aparece en: LC 21, LC 23, LC 2, LC 24, LC 92, LC 86 — la mayoría de problemas que construyen listas.

---

## Auto-test

1. Escribe la Solución 1 desde cero.
2. Justifica el rol del dummy node.
3. Trace mental con `[1,2]` y `[3,4]`.
4. **Bonus** — implementa LC 23 (Merge K Sorted Lists) usando esta función como sub-rutina.

---

## Conexiones

- [[206-reverse-linked-list]] — patrón anterior.
- Próximo: [[141-linked-list-cycle]].
- [[23-merge-k-sorted-lists]] — generalización.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 1 desde cero
- [ ] Justificado el dummy node
- [ ] Resuelto en LeetCode con éxito
