---
title: "LeetCode 33 — Search in Rotated Sorted Array"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/binary-search, patron/array-rotado]
type: nota
status: en-progreso
source: claude-code
aliases: [Search in Rotated Sorted Array, LC 33, search rotated, Buscar en array rotado]
problem_id: 33
difficulty: medium
patron: binary-search
neetcode_order: 5
---

# LeetCode 33 — Search in Rotated Sorted Array

> **Quinto problema del patrón Binary Search**. Es la **extensión natural de [[153-find-minimum-in-rotated-sorted-array]]**: ahora no buscas el mínimo, buscas un **target específico**. La técnica clave: en cada iteración, **detectar qué mitad está ordenada** y comprobar si el target cae en ella.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Te dan un array `nums` ordenado de forma creciente con valores únicos, **rotado** entre 1 y n veces. Por ejemplo, `[0,1,2,4,5,6,7]` rotado 4 veces queda `[4,5,6,7,0,1,2]`.

Dado un `target`, devuelve su **índice** si existe en `nums`, o `-1` si no.

**Tu solución debe correr en O(log n).**

**Ejemplo 1:**
```
Input:  nums = [4, 5, 6, 7, 0, 1, 2], target = 0
Output: 4
```

**Ejemplo 2:**
```
Input:  nums = [4, 5, 6, 7, 0, 1, 2], target = 3
Output: -1
```

**Restricciones:**
- `1 <= nums.length <= 5000`.
- `-10^4 <= nums[i] <= 10^4`.
- Todos los valores son **únicos**.

**Plantilla:**
```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — índice o -1 |
| ¿Está ordenado? | Casi: rotado |
| ¿Hay duplicados? | NO en este problema |
| ¿Cómo me ayuda la rotación? | En cada paso, **una de las dos mitades** SIEMPRE está completamente ordenada |
| Edge case 1 | Array no rotado → binary search clásico |
| Edge case 2 | n=1: comparar directamente |

> **El truco mental**: cualquier mitad de un array rotado o (a) está completamente ordenada o (b) contiene el punto de rotación. Comparando `nums[left]` con `nums[mid]` puedes distinguir cuál es cuál.

---

## Solución 1 — Linear search O(n) (NO óptima)

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        for i, num in enumerate(nums):
            if num == target:
                return i
        return -1
```

[NO] Viola la restricción O(log n).

---

## Solución 2 — Binary search modificado (la canónica)

**La idea clave**: en cada iteración, identificar qué mitad está ordenada (left a mid o mid a right). Si target cae en esa mitad ordenada, descartar la otra. Si no, descartar la ordenada.

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                return mid

            # ¿Qué mitad está ordenada?
            if nums[left] <= nums[mid]:
                # Mitad IZQUIERDA ordenada
                if nums[left] <= target < nums[mid]:
                    right = mid - 1               # target está en la mitad izquierda
                else:
                    left = mid + 1                # target está en la otra mitad
            else:
                # Mitad DERECHA ordenada (porque si izq no lo está, derecha sí)
                if nums[mid] < target <= nums[right]:
                    left = mid + 1                # target está en la mitad derecha
                else:
                    right = mid - 1
        return -1
```

**Trace mental con `nums = [4, 5, 6, 7, 0, 1, 2], target = 0`**:

```
Inicial: left=0, right=6

Iter 1: mid=3, nums[3]=7
  7 != 0
  nums[left]=4 <= nums[mid]=7 → izquierda ordenada
  ¿target=0 en [4, 7)? 4 <= 0? NO → target NO en izquierda
  left = 4

Iter 2: left=4, right=6, mid=5, nums[5]=1
  1 != 0
  nums[left]=0 <= nums[mid]=1 → izquierda ordenada (sub-array [0,1])
  ¿target=0 en [0, 1)? 0 <= 0 < 1? SÍ → target en izquierda
  right = 4

Iter 3: left=4, right=4, mid=4, nums[4]=0
  0 == 0 → return 4 [OK]
```

**Análisis:**
- **Tiempo: O(log n)** — cada iteración descarta la mitad.
- **Espacio: O(1)**.
- **Veredicto:** [OK] **la canónica**.

### Por qué `nums[left] <= nums[mid]` (con `<=`)

Cuando `left == mid` (ventana de 1 o 2 elementos), `nums[left] == nums[mid]`. Sin el `=`, este caso entraría en el "else" incorrectamente. El `<=` lo cubre.

### Las 4 ramas de decisión

```
                        ¿nums[left] <= nums[mid]?
                                  /\
                              SÍ /  \ NO
                          (izq ord)  (der ord)
                            /\         /\
              ¿target en [left, mid)?  ¿target en (mid, right]?
                /\                       /\
             SÍ /  \ NO              SÍ /  \ NO
            R=m-1  L=m+1            L=m+1  R=m-1
```

Memorizar este árbol — es exactamente la estructura del código.

---

## Alternativa — Buscar pivote primero, luego binary search clásico

Una variante: aplicar [[153-find-minimum-in-rotated-sorted-array]] para encontrar el índice del mínimo, luego hacer binary search en el segmento correcto.

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        n = len(nums)
        # Paso 1: encontrar pivote (índice del min)
        left, right = 0, n - 1
        while left < right:
            mid = left + (right - left) // 2
            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid
        pivot = left

        # Paso 2: decidir en qué segmento buscar
        if pivot == 0 or target >= nums[0]:
            # target está en la "alta" (izquierda del pivote)
            return self.binary_search(nums, target, 0, pivot - 1) if pivot > 0 else self.binary_search(nums, target, 0, n - 1)
        else:
            # target está en la "baja" (derecha del pivote)
            return self.binary_search(nums, target, pivot, n - 1)

    def binary_search(self, nums, target, left, right):
        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1
```

**Análisis:** O(log n) total (dos binary searches en serie). **Más laboriosa** pero más fácil de razonar a veces. La Solución 2 es más compacta y la preferida.

---

## El patrón general — "Binary search en rotated array"

**Cuándo aplicar**:

> Cuando tienes un array rotado y necesitas O(log n). En cada iteración, **detectar la mitad ordenada** y decidir según target.

**Plantilla mental**:

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:                  # izq ordenada
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                         # der ordenada
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

**Tres señales** del patrón:

1. Array rotado (o casi-monotónico con un punto de discontinuidad).
2. Buscas un target específico.
3. La fuerza bruta es O(n) y necesitas O(log n).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **81. Search in Rotated Sorted Array II** | Mismo problema **con duplicados** → caso `nums[left] == nums[mid]`: `left += 1` |
| **153. Find Minimum in Rotated Sorted Array** | Solo encontrar el min (sin target) |
| **154. Find Min in Rotated Sorted Array II** | Min con duplicados |

---

## Conceptos a interiorizar

### "Una mitad siempre ordenada" — la propiedad clave

Después de cualquier rotación, si partes el array por la mitad, **al menos una de las dos mitades sigue ordenada**. Esto es el fundamento de la solución.

### Comparar `target` con extremos de la mitad ordenada

```python
if nums[left] <= target < nums[mid]:    # target en la mitad izq (ordenada)
    right = mid - 1
```

Es **comparación con dos extremos**: target debe estar dentro del rango `[nums[left], nums[mid])`. Si no, salta a la otra mitad.

### Cuidado con `<=` vs `<` en las comparaciones

Cuando los rangos son cerrados o abiertos importa para no incluir/excluir endpoints incorrectamente:

- `nums[left] <= target < nums[mid]` — target puede ser nums[left] pero NO nums[mid] (lo habríamos detectado al inicio si fuera).

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Linear search | O(n) | O(1) | [NO] No cumple |
| 2. **Binary search modificado** | **O(log n)** | O(1) | [OK] La canónica |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero. Es laboriosa, dale 30+ min sin frustrarte.
2. Justifica:
   - Por qué `nums[left] <= nums[mid]` (con `<=`, no `<`).
   - Por qué `[nums[left], nums[mid])` y no `(nums[left], nums[mid]]`.
   - Por qué `while left <= right` (con `<=`).
3. Trace mental con `nums = [4, 5, 6, 7, 0, 1, 2], target = 3`. ¿Por qué -1?
4. Dibuja el árbol de decisiones (4 ramas) en un papel.
5. **Bonus** — extiende a LC 81 (duplicados). Pista: caso `nums[left] == nums[mid] == nums[right]` → `left += 1, right -= 1`.

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra que una mitad siempre está ordenada."** → Por inducción sobre la rotación. Si k=0 (no rotado), todo ordenado. Si k>0, el punto de rotación cae en una de las dos mitades; la otra está completa y ordenada.
- **"¿Por qué `<=` en `nums[left] <= nums[mid]`?"** → Cuando `left == mid` (uno o dos elementos), iguales. Sin `=`, el caso degenerado falla.
- **"¿Cómo lo extenderías a duplicados (LC 81)?"** → Si `nums[left] == nums[mid] == nums[right]`, no podemos saber qué mitad está ordenada → `left += 1, right -= 1`. Peor caso O(n).
- **"¿Cuál es el peor caso de tu solución?"** → Siempre O(log n), independientemente de la rotación.

---

## Conexiones

- [[153-find-minimum-in-rotated-sorted-array]] — encontrar min, base de este.
- [[704-binary-search]] — binary search clásico.
- Próximo: [[981-time-based-key-value-store]] — binary search por timestamp en un dict.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificadas las 3 sutilezas (≤, rangos, while)
- [ ] Dibujado el árbol de 4 ramas
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
