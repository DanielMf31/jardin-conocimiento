---
title: Puente a NeetCode — Herramientas Python para entrevistas
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/entrevistas, programacion/algoritmos]
type: nota
status: en-progreso
source: claude-code
aliases: [puente neetcode, python entrevistas, two pointers python, two sum python]
---

# Puente a NeetCode — Herramientas Python para entrevistas

## Idea central

Los problemas de entrevista tipo LeetCode/NeetCode son, en su mayoría, combinaciones de tres patrones: **memoria con dict/set**, **dos punteros** y **recorrido lineal con acumulador**. Todo lo que aprendiste (listas, dicts, sets, slicing) ya es suficiente para resolverlos.

---

## Qué aprendes

| Concepto | Para qué |
|---|---|
| `dict` como tabla de búsqueda O(1) | Two Sum, anagramas, frecuencias |
| `set` para detectar duplicados | Contains Duplicate, unicidad |
| Dos punteros (`left`, `right`) | Palíndromos, ventana deslizante |
| Acumulador con reset | Máximo de sublista contigua (Kadane) |
| `collections.Counter` | Contar letras en una sola línea |
| Índice negativo / slicing | Invertir, comparar mitades |

---

## C vs Python

El mismo patrón "buscar un complemento en array" implementado en cada lenguaje:

| Aspecto | C | Python |
|---|---|---|
| Tabla hash manual | `struct Map { int key; int val; }` + buckets a mano | `d = {}` — dict incorporado |
| Insertar | `map[i].key = nums[i]; map[i].val = i;` | `d[nums[i]] = i` |
| Buscar | bucle `for` sobre la tabla | `if comp in d:` — O(1) promedio |
| Devolver índices | `result[0] = ...; result[1] = ...;` | `return [d[comp], i]` |
| Gestión de memoria | `malloc` / `free` explícito | automática |

```c
// C — Two Sum (simplificado, O(n²))
int* twoSum(int* nums, int n, int target, int* returnSize) {
    int* res = malloc(2 * sizeof(int));
    *returnSize = 2;
    for (int i = 0; i < n; i++)
        for (int j = i+1; j < n; j++)
            if (nums[i] + nums[j] == target) {
                res[0] = i; res[1] = j; return res;
            }
    return NULL;
}
```

```python
# Python — Two Sum O(n) con dict
def two_sum(nums, target):
    visto = {}                  # valor -> índice
    for i, n in enumerate(nums):
        comp = target - n
        if comp in visto:
            return [visto[comp], i]
        visto[n] = i
```

Clave: en C necesitas una estructura auxiliar construida a mano; en Python `dict` ya es esa estructura.

---

## Explicación

### Patrón 1 — Dict como "memoria de lo ya visto"

```
Para cada elemento x:
    calcula lo que NECESITAS (complemento, par, etc.)
    pregunta al dict si ya lo viste
    si sí -> has encontrado la respuesta
    si no -> guarda x en el dict
```

```python
# skeleton del patrón
memoria = {}
for i, x in enumerate(lista):
    necesito = f(x)          # depende del problema
    if necesito in memoria:
        # encontrado
        pass
    memoria[x] = i           # guarda posición u otro dato
```

### Patrón 2 — Dos punteros

```python
left, right = 0, len(s) - 1
while left < right:
    if condicion(s[left], s[right]):
        left += 1
        right -= 1
    else:
        return False
return True
```

Ambos punteros avanzan hacia el centro; el bucle es O(n).

### Patrón 3 — Acumulador Kadane

```
actual = primer elemento
maximo = primer elemento
Para cada elemento siguiente:
    actual = max(elemento, actual + elemento)
    maximo = max(maximo, actual)
```

Decide en cada paso si conviene empezar una nueva sublista o extender la actual.

### `collections.Counter`

```python
from collections import Counter

c = Counter("banana")   # Counter({'a': 3, 'n': 2, 'b': 1})
c['a']                  # 3
Counter("abc") == Counter("cab")  # True — muy útil para anagramas
```

`Counter` es un `dict` especializado; sabe contar y comparar por igualdad.

---

## Worked example — Valid Palindrome paso a paso

**Enunciado**: dada una cadena, ignorando lo que no sea alfanumérico y sin distinguir mayúsculas, determina si es un palíndromo.

```
Entrada: "A man, a plan, a canal: Panama"
Salida:  True
```

**Paso 1** — limpiar la cadena:

```python
s = "A man, a plan, a canal: Panama"
limpia = [c.lower() for c in s if c.isalnum()]
# ['a','m','a','n','a','p','l','a','n','a','c','a','n','a','l','p','a','n','a','m','a']
```

**Paso 2** — dos punteros:

```python
left, right = 0, len(limpia) - 1
while left < right:
    if limpia[left] != limpia[right]:
        print("No es palíndromo")
        # devolvería False
    left += 1
    right -= 1
print("Es palíndromo")  # True
```

**Por qué funciona**: avanzamos desde los extremos hacia el centro comparando cada par. Si todos coinciden, es palíndromo. Coste O(n) en tiempo y O(n) en espacio (por la lista `limpia`). Existe variante O(1) en espacio iterando directamente sobre la cadena original.

---

## Errores típicos de Python

1. **`input()` devuelve `str`** — si lees números del usuario, conviértelos:
   ```python
   n = int(input("Dame un número: "))  # no int = TypeError al sumar
   ```

2. **Indentación inconsistente** — Python usa sangría para delimitar bloques, no `{}`. Mezclar tabs y espacios da `TabError`.

3. **`list` es mutable; asignarlo copia la referencia, no el contenido**:
   ```python
   a = [1, 2, 3]
   b = a          # b apunta al mismo objeto
   b.append(4)
   print(a)       # [1, 2, 3, 4]  ← sorpresa
   # Solución: b = a.copy() o b = a[:]
   ```

4. **`IndexError` al acceder fuera de rango** — en C acceder fuera de un array es UB silencioso; en Python obtienes excepción inmediata. Verifica con `if i < len(lista)`.

5. **Comparar `Counter` con `==` vs comparar listas** — `Counter("abc") == Counter("bca")` es `True`; `list("abc") == list("bca")` es `False`. Elige según lo que quieras comparar.

---

## Ejercicios

Cada ejercicio tiene enunciado tipo LeetCode, salida esperada y dificultad.

| # | Enunciado | Dificultad |
|---|---|---|
| 01 | **Two Sum** — dado `nums` y `target`, devuelve los índices de los dos números que suman `target`. | (facil) |
| 02 | **Contains Duplicate** — devuelve `True` si algún valor aparece al menos dos veces. | (facil) |
| 03 | **Valid Palindrome** — ignora no-alfanuméricos y mayúsculas, devuelve si es palíndromo. | (facil) |
| 04 | **Maximum Subarray** — devuelve la suma de la sublista contigua con mayor suma (Kadane). | (media) |
| 05 | **Valid Anagram** — dadas dos cadenas `s` y `t`, devuelve si `t` es un anagrama de `s`. | (facil) |

### Salidas esperadas de ejemplo

```
ej01: nums=[2,7,11,15], target=9  →  [0, 1]
ej02: nums=[1,2,3,1]              →  True
ej02: nums=[1,2,3,4]              →  False
ej03: s="A man, a plan, a canal: Panama"  →  True
ej03: s="race a car"                      →  False
ej04: nums=[-2,1,-3,4,-1,2,1,-5,4]       →  6
ej05: s="anagram", t="nagaram"    →  True
ej05: s="rat", t="car"            →  False
```

Archivos de práctica en `practica/09-puente-neetcode/`:

- `ej01_practica.py` / `ej01_modelo.py`
- `ej02_practica.py` / `ej02_modelo.py`
- `ej03_practica.py` / `ej03_modelo.py`
- `ej04_practica.py` / `ej04_modelo.py`
- `ej05_practica.py` / `ej05_modelo.py`

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/08-clases-archivos]]
