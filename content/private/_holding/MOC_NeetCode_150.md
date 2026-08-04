---
title: MOC NeetCode 150 — Entrenamiento algorítmico
date: 2026-05-07
tags: [moc, programacion, programacion/leetcode, programacion/algoritmos, neetcode-150, entrenamiento-tecnico, carrera/preparacion-entrevistas]
type: moc
status: permanente
aliases: [MOC NeetCode 150, MOC LeetCode, NeetCode 150 Index, Entrenamiento algorítmico]
---

# MOC NeetCode 150 — Entrenamiento algorítmico

> **Punto de entrada único** al entrenamiento algorítmico siguiendo la lista curada [NeetCode 150](https://neetcode.io/roadmap). 150 problemas organizados en **18 patrones** que cubren los fundamentos de coding interviews.
>
> **Estado actual**: **150 / 150 problemas documentados — TODOS LOS PATRONES COMPLETOS**
>
> **Referencia rápida de Python**: [[00_python-syntax-cheatsheet|Python Syntax Cheatsheet]] — todas las estructuras (list, set, dict, Counter, defaultdict, deque, heapq), métodos con complejidad, ejemplos cortos, trampas comunes y patrones por tipo de problema. **Ten esta pestaña abierta mientras resuelves**.
>
> **Formato de cada nota**: worked example primero, patrón abstraído, replicar sin mirar. Ver memoria `feedback_learning_style_algorithmic.md`.

## Resumen de progreso

| Patrón | Total | [OK] Hecho | Pendiente | % |
|---|---|---|---|---|
| 01. Arrays & Hashing | 9 | **9** | 0 | **100%** |
| 02. Two Pointers | 5 | **5** | 0 | **100%** |
| 03. Sliding Window | 6 | **6** | 0 | **100%** |
| 04. Stack | 7 | **7** | 0 | **100%** |
| 05. Binary Search | 7 | **7** | 0 | **100%** |
| 06. Linked List | 11 | **11** | 0 | **100%** |
| 07. Trees | 15 | **15** | 0 | **100%** |
| 08. Tries | 3 | **3** | 0 | **100%** |
| 09. Heap / Priority Queue | 7 | **7** | 0 | **100%** |
| 10. Backtracking | 9 | **9** | 0 | **100%** |
| 11. Graphs | 13 | **13** | 0 | **100%** |
| 12. Advanced Graphs | 6 | **6** | 0 | **100%** |
| 13. 1-D Dynamic Programming | 12 | **12** | 0 | **100%** |
| 14. 2-D Dynamic Programming | 11 | **11** | 0 | **100%** |
| 15. Greedy | 8 | **8** | 0 | **100%** |
| 16. Intervals | 6 | **6** | 0 | **100%** |
| 17. Math & Geometry | 8 | **8** | 0 | **100%** |
| 18. Bit Manipulation | 7 | **7** | 0 | **100%** |
| **TOTAL** | **150** | **150** | **0** | **100%** [OK] |

> **Convención de iconos en este índice**: [OK] archivo creado y wikilink activo · pendiente de crear · número LeetCode oficial · recomendado especialmente · (facil) Easy · (media) Medium · (dificil) Hard.

---

## Problemas con solución C++ añadida (contraste de lenguaje)

> Estos 10 problemas tienen además una **solución en C++** dentro de su `.md`
> (sección "Solución en C++ — contraste con Python") + un `.cpp` hermano
> compilable. Resueltos para estudiar las diferencias Python ↔ C++ en variedad de
> patrones (hash, two pointers, stack, binary search, punteros de lista, recursión
> de árbol). Marcados con `C++` en las tablas. Conecta con
> (`Build_Things/10_cpp_learning/`).

- [[217-contains-duplicate]] · [[1-two-sum]] · [[49-group-anagrams]]
- [[125-valid-palindrome]] · [[15-3sum]] · [[121-best-time-to-buy-and-sell-stock]]
- [[20-valid-parentheses]] · [[704-binary-search]] · [[206-reverse-linked-list]]
- [[226-invert-binary-tree]]

---

## 01. Arrays & Hashing — [OK] COMPLETO

> **Idea central del patrón**: el dict/set como "memoria" de lo visto. La diferencia entre problemas es **qué información asocias** a cada elemento (presencia, frecuencia, índice, clave canónica).

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 217 | [[217-contains-duplicate\|Contains Duplicate]] | (facil) | [OK] C++ | "He visto X antes" |
| 242 | [[242-valid-anagram\|Valid Anagram]] | (facil) | [OK] | Frecuencias con dict / Counter / array 26 |
| 1 | [[1-two-sum\|Two Sum]] | (facil) | [OK] C++ | "He visto el complemento de X" |
| 49 | [[49-group-anagrams\|Group Anagrams]] | (media) | [OK] C++ | Clave canónica + `defaultdict(list)` |
| 347 | [[347-top-k-frequent-elements\|Top K Frequent Elements]] | (media) | [OK] | Counter + heap O(n log k), bucket sort O(n) |
| 271 | [[271-encode-and-decode-strings\|Encode and Decode Strings]] | (media) | [OK] | Length-prefix encoding (≈ tu protocolo embebido) |
| 238 | [[238-product-of-array-except-self\|Product of Array Except Self]] | (media) | [OK] | Prefix * Suffix products in-place O(1) |
| 36 | [[36-valid-sudoku\|Valid Sudoku]] | (media) | [OK] | Set con claves compuestas (múltiples restricciones) |
| 128 | [[128-longest-consecutive-sequence\|Longest Consecutive Sequence]] | (media) | [OK] | Set + check de "soy inicio" + análisis amortizado |

---

## 02. Two Pointers — [OK] COMPLETO

> **Idea central del patrón**: dos índices que recorren el array (mismo extremo o extremos opuestos) con criterios de avance distintos. Aplica especialmente a **arrays ordenados** y problemas de palíndromos.

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 125 | [[125-valid-palindrome\|Valid Palindrome]] | (facil) | [OK] C++ | Two pointers convergentes con skip de no-alfanuméricos |
| 167 | [[167-two-sum-ii-input-array-is-sorted\|Two Sum II - Input Array Is Sorted]] | (media) | [OK] | Monotonía del orden permite descartar 1 candidato por iter |
| 15 | [[15-3sum\|3Sum]] | (media) | [OK] C++ | Sort + fix one + two pointers (reducción de 3-Sum a 2-Sum) |
| 11 | [[11-container-with-most-water\|Container With Most Water]] | (media) | [OK] | Greedy local: mover el menor (argumento de descarte) |
| 42 | [[42-trapping-rain-water\|Trapping Rain Water]] | (dificil) | [OK] | Two pointers con tracking de máximos (3 niveles de optimización) |

---

## 03. Sliding Window — [OK] COMPLETO

> **Idea central del patrón**: ventana de tamaño variable o fijo que se desplaza por la colección, manteniendo invariantes. Para subarrays/substrings con propiedades.

| | Problema | | Estado | Idea distintiva |
| --- | ------------------------------------------------------------------------------------------------------ | --- | ------ | ----------------------------------------------------- |
| 121 | [[121-best-time-to-buy-and-sell-stock\|Best Time to Buy and Sell Stock]] | (facil) | [OK] C++ | Tracking de mínimo histórico (one-pass) |
| 3 | [[3-longest-substring-without-repeating-characters\|Longest Substring Without Repeating Characters]] | (media) | [OK] | Sliding window variable con set / dict de índices |
| 424 | [[424-longest-repeating-character-replacement\|Longest Repeating Character Replacement]]               | (media)  | [OK]      | Sliding window con tolerancia (`len - max_freq <= k`) |
| 567 | [[567-permutation-in-string\|Permutation in String]]                                                   | (media)  | [OK]      | Sliding window de tamaño FIJO + match de frecuencias  |
| 76  | [[76-minimum-window-substring\|Minimum Window Substring]]                                              | (dificil)  | [OK]      | Sliding window con cobertura (`have / need`)          |
| 239 | [[239-sliding-window-maximum\|Sliding Window Maximum]]                                                 | (dificil)  | [OK]      | Deque monotónica decreciente (O(n) amortizado)        |

---

## 04. Stack — [OK] COMPLETO

> **Idea central del patrón**: estructura LIFO para procesar elementos en orden inverso al de inserción. Validación de paréntesis, evaluación de expresiones, "siguiente mayor/menor" (stack monotónico).

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 20 | [[20-valid-parentheses\|Valid Parentheses]] | (facil) | [OK] C++ | LIFO para emparejar delimitadores |
| 155 | [[155-min-stack\|Min Stack]] | (media) | [OK] | Diseño de clase: stack auxiliar para min en O(1) |
| 150 | [[150-evaluate-reverse-polish-notation\|Evaluate Reverse Polish Notation]] | (media) | [OK] | Stack para evaluar expresiones (RPN) |
| 22 | [[22-generate-parentheses\|Generate Parentheses]] | (media) | [OK] | Backtracking con poda; intro al patrón 10 |
| 739 | [[739-daily-temperatures\|Daily Temperatures]] | (media) | [OK] | Stack monotónico decreciente ("próximo mayor") |
| 853 | [[853-car-fleet\|Car Fleet]] | (media) | [OK] | Sort + stack con tracking de ETA |
| 84 | [[84-largest-rectangle-in-histogram\|Largest Rectangle in Histogram]] | (dificil) | [OK] | Stack monotónico creciente para áreas máximas |

---

## 05. Binary Search — [OK] COMPLETO

> **Idea central del patrón**: búsqueda en O(log n) sobre estructuras ordenadas. La clave es **identificar la propiedad monotónica** que permite descartar la mitad del espacio en cada paso.

| | Problema | | Estado | Idea distintiva |
| --- | ------------------------------------------------------------------------------------ | --- | ------ | ---------------------------------------------------------------- |
| 704 | [[704-binary-search\|Binary Search]] | (facil) | [OK] C++ | Template clásico; las 4 trampas (overflow, `<=`, `+1`/`-1`, `<`) |
| 74  | [[74-search-a-2d-matrix\|Search a 2D Matrix]]                                        | (media)  | [OK]      | Matriz como 1D virtual; `divmod(mid, n)`                         |
| 875 | [[875-koko-eating-bananas\|Koko Eating Bananas]]                                     | (media)  | [OK]      | Binary search **on answer** con función monotónica               |
| 153 | [[153-find-minimum-in-rotated-sorted-array\|Find Minimum in Rotated Sorted Array]] | (media) | [OK] | Comparar con `nums[right]` para localizar pivote |
| 33  | [[33-search-in-rotated-sorted-array\|Search in Rotated Sorted Array]]                | (media)  | [OK]      | "Una mitad siempre ordenada" + árbol de 4 ramas                  |
| 981 | [[981-time-based-key-value-store\|Time Based Key-Value Store]]                       | (media)  | [OK]      | Diseño de clase + `bisect_right` para "último ≤ x"               |
| 4   | [[4-median-of-two-sorted-arrays\|Median of Two Sorted Arrays]]                       | (dificil)  | [OK]      | Binary search sobre **partición** (el más difícil)               |

---

## 06. Linked List — [OK] COMPLETO

> **Idea central del patrón**: manipulación de punteros (`prev`, `curr`, `next`) y dos punteros (slow / fast) para detectar ciclos, encontrar mitad, etc.

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 206 | [[206-reverse-linked-list\|Reverse Linked List]] | (facil) | [OK] C++ | 3 punteros (prev/curr/next) — sub-rutina central |
| 21 | [[21-merge-two-sorted-lists\|Merge Two Sorted Lists]] | (facil) | [OK] | Dummy node + tail pointer |
| 141 | [[141-linked-list-cycle\|Linked List Cycle]] | (facil) | [OK] | Floyd's tortoise & hare (slow/fast) |
| 143 | [[143-reorder-list\|Reorder List]] | (media) | [OK] | Composición: mid + reverse + merge alternado |
| 19 | [[19-remove-nth-node-from-end-of-list\|Remove Nth Node From End]] | (media) | [OK] | Two pointers con offset n+1 |
| 138 | [[138-copy-list-with-random-pointer\|Copy List with Random Pointer]] | (media) | [OK] | Hash map old→new para deep copy |
| 2 | [[2-add-two-numbers\|Add Two Numbers]] | (media) | [OK] | Suma con carry + dummy + `while l1 or l2 or carry` |
| 287 | [[287-find-the-duplicate-number\|Find the Duplicate Number]] | (media) | [OK] | Floyd sobre array (array como linked list virtual) |
| 146 | [[146-lru-cache\|LRU Cache]] | (media) | [OK] | Doubly linked list + hash map; get/put en O(1) |
| 23 | [[23-merge-k-sorted-lists\|Merge K Sorted Lists]] | (dificil) | [OK] | Min-heap o divide-and-conquer; O(n log k) |
| 25 | [[25-reverse-nodes-in-k-group\|Reverse Nodes in K-Group]] | (dificil) | [OK] | Reverse en bloques con localización + reconexión |

---

## 07. Trees — [OK] COMPLETO

> **Idea central del patrón**: recursión sobre estructura jerárquica. DFS (preorder, inorder, postorder), BFS (level order), invariantes de BST. **Núcleo de entrevistas**.

| | Problema | | Estado | Idea distintiva |
| ---- | ------------------------------------------------------------------------------------------------------------------ | --- | ------ | ------------------------------------------------- |
| 226 | [[226-invert-binary-tree\|Invert Binary Tree]] | (facil) | [OK] C++ | Recursión simple, swap pythonic |
| 104  | [[104-maximum-depth-of-binary-tree\|Maximum Depth of Binary Tree]]                                                 | (facil)  | [OK]      | `1 + max(left, right)` postorder                  |
| 543  | [[543-diameter-of-binary-tree\|Diameter of Binary Tree]]                                                           | (facil)  | [OK]      | Recursión + tracker global (patrón maestro)       |
| 110  | [[110-balanced-binary-tree\|Balanced Binary Tree]]                                                                 | (facil)  | [OK]      | Valor centinela `-1` para señalizar               |
| 100  | [[100-same-tree\|Same Tree]]                                                                                       | (facil)  | [OK]      | Recursión paralela sobre 2 árboles                |
| 572  | [[572-subtree-of-another-tree\|Subtree of Another Tree]]                                                           | (facil)  | [OK]      | Doble recursión: search + verify                  |
| 235  | [[235-lowest-common-ancestor-of-a-bst\|Lowest Common Ancestor of a BST]]                                           | (media)  | [OK]      | Aprovechar propiedad BST O(log n)                 |
| 102 | [[102-binary-tree-level-order-traversal\|Binary Tree Level Order Traversal]] | (media) | [OK] | BFS con `deque`, snapshot de tamaño por nivel |
| 199  | [[199-binary-tree-right-side-view\|Binary Tree Right Side View]]                                                   | (media)  | [OK]      | BFS + último de cada nivel                        |
| 1448 | [[1448-count-good-nodes-in-binary-tree\|Count Good Nodes in Binary Tree]]                                          | (media)  | [OK]      | DFS con acumulador top-down                       |
| 98   | [[98-validate-binary-search-tree\|Validate Binary Search Tree]]                                                    | (media)  | [OK]      | DFS con bounds (lower, upper) top-down            |
| 230  | [[230-kth-smallest-element-in-a-bst\|Kth Smallest Element in a BST]]                                               | (media)  | [OK]      | Inorder iterativo con stack                       |
| 105  | [[105-construct-binary-tree-from-preorder-and-inorder-traversal\|Construct Binary Tree from Preorder and Inorder]] | (media)  | [OK]      | Reconstrucción con índices + hash de inorder      |
| 124  | [[124-binary-tree-maximum-path-sum\|Binary Tree Maximum Path Sum]]                                                 | (dificil)  | [OK]      | Generalización de 543 con negativos (`max(., 0)`) |
| 297  | [[297-serialize-and-deserialize-binary-tree\|Serialize and Deserialize Binary Tree]]                               | (dificil)  | [OK]      | Preorder + N como marcador de None                |

---

## 08. Tries — [OK] COMPLETO

> **Idea central del patrón**: árbol de prefijos para búsquedas de string eficientes. Autocompletado, validación de palabras, búsqueda con wildcards.

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 208 | [[208-implement-trie-prefix-tree\|Implement Trie - Prefix Tree]] | (media) | [OK] | Estructura básica con dict de hijos + `is_end` |
| 211 | [[211-design-add-and-search-words-data-structure\|Design Add and Search Words]] | (media) | [OK] | Trie + DFS para wildcards `'.'` |
| 212 | [[212-word-search-ii\|Word Search II]] | (dificil) | [OK] | Trie + backtracking en grid |

---

## 09. Heap / Priority Queue — [OK] COMPLETO

> **Idea central del patrón**: estructura ordenada por prioridad con O(log n) inserción/extracción del mínimo (o máximo). Top-K, scheduling, mediana en stream.

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 703 | [[703-kth-largest-element-in-a-stream\|Kth Largest in Stream]] | (facil) | [OK] | Min-heap de tamaño k en streaming |
| 1046 | [[1046-last-stone-weight\|Last Stone Weight]] | (facil) | [OK] | Max-heap simulado con negación |
| 973 | [[973-k-closest-points-to-origin\|K Closest Points to Origin]] | (media) | [OK] | Max-heap top-K + saltar `sqrt` |
| 215 | [[215-kth-largest-element-in-an-array\|Kth Largest Element in Array]] | (media) | [OK] | Sort vs heap vs **quickselect O(n)** |
| 621 | [[621-task-scheduler\|Task Scheduler]] | (media) | [OK] | Heap + queue de cooldown |
| 355 | [[355-design-twitter\|Design Twitter]] | (media) | [OK] | Diseño con dict + heap |
| 295 | [[295-find-median-from-data-stream\|Find Median from Data Stream]] | (dificil) | [OK] | **Two heaps** (max-heap + min-heap) |

> Ya tocaste heap brevemente en [[347-top-k-frequent-elements]]; aquí se profundiza.

---

## 10. Backtracking — [OK] COMPLETO

> **Idea central del patrón**: explorar todas las posibles combinaciones / permutaciones recursivamente, con **poda** cuando una rama no puede llevar a solución. DFS sobre espacio de estados.

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 78 | [[78-subsets\|Subsets]] | (media) | [OK] | "Incluir / no incluir" |
| 39 | [[39-combination-sum\|Combination Sum]] | (media) | [OK] | Permitir repetir: `i` no `i+1` |
| 46 | [[46-permutations\|Permutations]] | (media) | [OK] | `used[]` flag |
| 90 | [[90-subsets-ii\|Subsets II]] | (media) | [OK] | Sort + skip dups (`i > start`) |
| 40 | [[40-combination-sum-ii\|Combination Sum II]] | (media) | [OK] | `i+1` + skip dups combinados |
| 79 | [[79-word-search\|Word Search]] | (media) | [OK] | DFS en grid + marcar/restaurar |
| 131 | [[131-palindrome-partitioning\|Palindrome Partitioning]] | (media) | [OK] | Particionar string + check palíndromo |
| 17 | [[17-letter-combinations-of-a-phone-number\|Letter Combinations of a Phone Number]] | (media) | [OK] | Producto cartesiano |
| 51 | [[51-n-queens\|N-Queens]] | (dificil) | [OK] | Múltiples constraints (cols, `r+c`, `r-c`) |

---

## 11. Graphs — [OK] COMPLETO

> **Idea central del patrón**: BFS (niveles, distancia mínima) y DFS (conectividad, ciclos). Modelar matrices como grafos implícitos. **Núcleo de entrevistas tecnicas**.

| | Problema | | Estado | Idea distintiva |
|---|---|---|---|---|
| 200 | [[200-number-of-islands\|Number of Islands]] | (media) | [OK] | DFS en grid + componentes conexos |
| 133 | [[133-clone-graph\|Clone Graph]] | (media) | [OK] | DFS + hash old→new |
| 695 | [[695-max-area-of-island\|Max Area of Island]] | (media) | [OK] | DFS devolviendo área |
| 417 | [[417-pacific-atlantic-water-flow\|Pacific Atlantic Water Flow]] | (media) | [OK] | DFS desde bordes (inverso) |
| 130 | [[130-surrounded-regions\|Surrounded Regions]] | (media) | [OK] | DFS desde bordes + flip |
| 994 | [[994-rotting-oranges\|Rotting Oranges]] | (media) | [OK] | Multi-source BFS con tiempo |
| 286 | [[286-walls-and-gates\|Walls and Gates]] | (media) | [OK] | Multi-source BFS para distancias |
| 207 | [[207-course-schedule\|Course Schedule]] | (media) | [OK] | DFS 3-colors o Kahn's algorithm |
| 210 | [[210-course-schedule-ii\|Course Schedule II]] | (media) | [OK] | Topological sort completo |
| 684 | [[684-redundant-connection\|Redundant Connection]] | (media) | [OK] | Union-Find básico |
| 323 | [[323-number-of-connected-components-in-an-undirected-graph\|Number of Connected Components]] | (media) | [OK] | DFS o UF para componentes |
| 261 | [[261-graph-valid-tree\|Graph Valid Tree]] | (media) | [OK] | UF + check `n-1` aristas |
| 127 | [[127-word-ladder\|Word Ladder]] | (dificil) | [OK] | BFS shortest path con patterns |

---

## 12. Advanced Graphs — Pendiente

> **Idea central del patrón**: algoritmos clásicos sobre grafos ponderados: Dijkstra (camino más corto), Prim/Kruskal (árbol de coste mínimo), Bellman-Ford, topological sort.

| | Problema | | Estado |
|---|---|---|---|
| 1584 | Min Cost to Connect All Points | (media) | |
| 743 | Network Delay Time | (media) | |
| 787 | Cheapest Flights Within K Stops | (media) | |
| 332 | Reconstruct Itinerary | (dificil) | |
| 778 | Swim in Rising Water | (dificil) | |
| 269 | Alien Dictionary | (dificil) | |

---

## 13. 1-D Dynamic Programming — Pendiente

> **Idea central del patrón**: descomponer un problema en **subproblemas óptimos** con dependencia 1D (estado = un índice). El terror clásico que se domesticа con repetición.

| | Problema | | Estado |
|---|---|---|---|
| 70 | Climbing Stairs | (facil) | |
| 746 | Min Cost Climbing Stairs | (facil) | |
| 198 | House Robber | (media) | |
| 213 | House Robber II | (media) | |
| 5 | Longest Palindromic Substring | (media) | |
| 647 | Palindromic Substrings | (media) | |
| 91 | Decode Ways | (media) | |
| 322 | Coin Change | (media) | |
| 152 | Maximum Product Subarray | (media) | |
| 139 | Word Break | (media) | |
| 300 | Longest Increasing Subsequence | (media) | |
| 416 | Partition Equal Subset Sum | (media) | |

---

## 14. 2-D Dynamic Programming — Pendiente

> **Idea central del patrón**: estado bidimensional (e.g. dos strings, dos índices). Las cumbres más altas del DP. Edit distance, knapsack, longest common subsequence.

| | Problema | | Estado |
|---|---|---|---|
| 62 | Unique Paths | (media) | |
| 1143 | Longest Common Subsequence | (media) | |
| 309 | Best Time to Buy and Sell Stock with Cooldown | (media) | |
| 518 | Coin Change II | (media) | |
| 494 | Target Sum | (media) | |
| 97 | Interleaving String | (media) | |
| 72 | Edit Distance | (media) | |
| 329 | Longest Increasing Path in a Matrix | (dificil) | |
| 115 | Distinct Subsequences | (dificil) | |
| 312 | Burst Balloons | (dificil) | |
| 10 | Regular Expression Matching | (dificil) | |

---

## 15. Greedy — Pendiente

> **Idea central del patrón**: tomar la decisión localmente óptima en cada paso. Simple cuando funciona; demostrar que funciona es lo difícil.

| | Problema | | Estado |
|---|---|---|---|
| 53 | Maximum Subarray | (media) | |
| 55 | Jump Game | (media) | |
| 45 | Jump Game II | (media) | |
| 134 | Gas Station | (media) | |
| 846 | Hand of Straights | (media) | |
| 1899 | Merge Triplets to Form Target Triplet | (media) | |
| 763 | Partition Labels | (media) | |
| 678 | Valid Parenthesis String | (media) | |

---

## 16. Intervals — Pendiente

> **Idea central del patrón**: ordenar intervalos por extremo (inicio o fin) y procesarlos linealmente. Solapamientos, fusiones, conflicts.

| | Problema | | Estado |
|---|---|---|---|
| 252 | Meeting Rooms | (facil) | |
| 56 | Merge Intervals | (media) | |
| 57 | Insert Interval | (media) | |
| 435 | Non-overlapping Intervals | (media) | |
| 253 | Meeting Rooms II | (media) | |
| 1851 | Minimum Interval to Include Each Query | (dificil) | |

---

## 17. Math & Geometry — Pendiente

> **Idea central del patrón**: manipulación de matrices (rotación, espirales), aritmética de enteros grandes, geometría plana básica.

| | Problema | | Estado |
|---|---|---|---|
| 202 | Happy Number | (facil) | |
| 66 | Plus One | (facil) | |
| 48 | Rotate Image | (media) | |
| 54 | Spiral Matrix | (media) | |
| 73 | Set Matrix Zeroes | (media) | |
| 50 | Pow(x, n) | (media) | |
| 43 | Multiply Strings | (media) | |
| 2013 | Detect Squares | (media) | |

---

## 18. Bit Manipulation — Pendiente

> **Idea central del patrón**: operaciones a nivel de bits (AND, OR, XOR, shifts). Útil cuando el dominio está acotado por el ancho de un entero (32 o 64 bits).
> Si vienes de hardware/embebido, este patrón te resultará **familiar** — XOR para diferencias, máscaras de bits, etc. son lenguaje habitual de firmware C.

| | Problema | | Estado |
|---|---|---|---|
| 136 | Single Number | (facil) | |
| 191 | Number of 1 Bits | (facil) | |
| 338 | Counting Bits | (facil) | |
| 190 | Reverse Bits | (facil) | |
| 268 | Missing Number | (facil) | |
| 371 | Sum of Two Integers | (media) | |
| 7 | Reverse Integer | (media) | |

---

## Cómo trabajar con este índice

1. **Punto de entrada único**: cuando vayas a estudiar, abres este MOC y eliges un problema.
2. **Wikilinks activos** [OK] → archivo creado con el formato worked-example. Click directo.
3. **Pendientes** → cuando estés listo para empezar uno nuevo, dímelo y lo redacto en el momento (o en lote por patrón completo, como hicimos con Arrays & Hashing).
4. **Estado en cada archivo**: la sección "Estado de progreso personal" al final de cada nota tiene checkboxes para tu seguimiento (leído / escrito desde cero / submitted en LeetCode / repaso semanal).
5. **Actualización del MOC**: cuando completemos un nuevo problema, actualizo la tabla de progreso global y marco el [OK] en su patrón.

## Orden recomendado de patrones

El orden numérico (1 → 18) **no es arbitrario**: cada patrón presupone los anteriores. Recomendación de progresión:

```
Fase 1 — Fundamentos      :  01 Arrays & Hashing  →  02 Two Pointers  →  03 Sliding Window
Fase 2 — Estructuras      :  04 Stack             →  06 Linked List   →  09 Heap
Fase 3 — Búsqueda         :  05 Binary Search
Fase 4 — Recursión / DFS  :  07 Trees             →  08 Tries         →  10 Backtracking
Fase 5 — Grafos           :  11 Graphs            →  12 Advanced Graphs
Fase 6 — DP               :  13 1-D DP            →  14 2-D DP
Fase 7 — Cierre           :  15 Greedy + 16 Intervals + 17 Math & Geometry + 18 Bit Manipulation
```

**Cadencia sostenible**: 3-5 problemas por semana → 30-50 semanas para completar los 150 (~7-12 meses). Constancia > intensidad.

## Recursos externos

- [neetcode.io/roadmap](https://neetcode.io/roadmap) — roadmap visual oficial con los 150.
- [neetcode.io/practice](https://neetcode.io/practice) — playlist de videos con explicación de cada problema (todos gratis).
- [LeetCode oficial](https://leetcode.com/) — plataforma para someter soluciones (cuenta gratis suficiente).
- [Blind 75](https://www.teamblind.com/post/New-Year-Gift---Curated-List-of-Top-75-LeetCode-Questions-to-Save-Your-Time-OaM1orEU) — lista anterior, subset de NeetCode 150 (los marcados con son aproximadamente Blind 75).

## Conexiones

- [[MOC_Programacion]] — área padre.
- Memoria asociada: `feedback_learning_style_algorithmic.md` (worked-example primero, no socrático para CS clásica).

---

## Consulta Dataview (problemas resueltos por dificultad)


> La consulta solo funciona si tienes el plugin **Dataview** instalado en Obsidian. Si no, ignórala — el MOC funciona igualmente.
