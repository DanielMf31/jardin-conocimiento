---
title: MOC NeetCode 150 — Entrenamiento algorítmico
date: 2026-05-07
tags: [moc, programacion, programacion/leetcode, programacion/algoritmos, neetcode-150, entrenamiento-tecnico, carrera/preparacion-entrevistas]
type: moc
status: permanente
aliases: [MOC NeetCode 150, MOC LeetCode, NeetCode 150 Index, Entrenamiento algorítmico]
---

# MOC NeetCode 150 — Entrenamiento algorítmico

> 📍 **Punto de entrada único** al entrenamiento algorítmico siguiendo la lista curada [NeetCode 150](https://neetcode.io/roadmap). 150 problemas organizados en **18 patrones** que cubren los fundamentos de coding interviews.
>
> 🎯 **Estado actual**: **150 / 150 problemas documentados — TODOS LOS PATRONES COMPLETOS** 🎉
>
> 📖 **Referencia rápida de Python**: [[00_python-syntax-cheatsheet|Python Syntax Cheatsheet]] — todas las estructuras (list, set, dict, Counter, defaultdict, deque, heapq), métodos con complejidad, ejemplos cortos, trampas comunes y patrones por tipo de problema. **Ten esta pestaña abierta mientras resuelves**.
>
> 📚 **Formato de cada nota**: worked example primero, patrón abstraído, replicar sin mirar. Ver memoria `feedback_learning_style_algorithmic.md`.

## Resumen de progreso

| Patrón | Total | ✅ Hecho | ⏳ Pendiente | % |
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
| **TOTAL** | **150** | **150** | **0** | **100%** ✅ |

> 💡 **Convención de iconos en este índice**: ✅ archivo creado y wikilink activo · ⏳ pendiente de crear · 🆔 número LeetCode oficial · ⭐ recomendado especialmente · 🟢 Easy · 🟡 Medium · 🔴 Hard.

---

## 📘 Problemas con solución C++ añadida (contraste de lenguaje)

> Estos 10 problemas tienen además una **solución en C++** dentro de su `.md`
> (sección "Solución en C++ — contraste con Python") + un `.cpp` hermano
> compilable. Resueltos para estudiar las diferencias Python ↔ C++ en variedad de
> patrones (hash, two pointers, stack, binary search, punteros de lista, recursión
> de árbol). Marcados con `📘C++` en las tablas. Conecta con
> (`Build_Things/10_cpp_learning/`).

- [[217-contains-duplicate]] · [[1-two-sum]] · [[49-group-anagrams]]
- [[125-valid-palindrome]] · [[15-3sum]] · [[121-best-time-to-buy-and-sell-stock]]
- [[20-valid-parentheses]] · [[704-binary-search]] · [[206-reverse-linked-list]]
- [[226-invert-binary-tree]]

---

## 01. Arrays & Hashing — ✅ COMPLETO

> **Idea central del patrón**: el dict/set como "memoria" de lo visto. La diferencia entre problemas es **qué información asocias** a cada elemento (presencia, frecuencia, índice, clave canónica).

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 217 | [[217-contains-duplicate\|Contains Duplicate]] | 🟢 | ✅ 📘C++ | "He visto X antes" |
| 242 | [[242-valid-anagram\|Valid Anagram]] | 🟢 | ✅ | Frecuencias con dict / Counter / array 26 |
| 1 | [[1-two-sum\|Two Sum]] ⭐ | 🟢 | ✅ 📘C++ | "He visto el complemento de X" |
| 49 | [[49-group-anagrams\|Group Anagrams]] | 🟡 | ✅ 📘C++ | Clave canónica + `defaultdict(list)` |
| 347 | [[347-top-k-frequent-elements\|Top K Frequent Elements]] | 🟡 | ✅ | Counter + heap O(n log k), bucket sort O(n) |
| 271 | [[271-encode-and-decode-strings\|Encode and Decode Strings]] | 🟡 | ✅ | Length-prefix encoding (≈ tu protocolo embebido) |
| 238 | [[238-product-of-array-except-self\|Product of Array Except Self]] | 🟡 | ✅ | Prefix * Suffix products in-place O(1) |
| 36 | [[36-valid-sudoku\|Valid Sudoku]] | 🟡 | ✅ | Set con claves compuestas (múltiples restricciones) |
| 128 | [[128-longest-consecutive-sequence\|Longest Consecutive Sequence]] | 🟡 | ✅ | Set + check de "soy inicio" + análisis amortizado |

---

## 02. Two Pointers — ✅ COMPLETO

> **Idea central del patrón**: dos índices que recorren el array (mismo extremo o extremos opuestos) con criterios de avance distintos. Aplica especialmente a **arrays ordenados** y problemas de palíndromos.

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 125 | [[125-valid-palindrome\|Valid Palindrome]] | 🟢 | ✅ 📘C++ | Two pointers convergentes con skip de no-alfanuméricos |
| 167 | [[167-two-sum-ii-input-array-is-sorted\|Two Sum II - Input Array Is Sorted]] ⭐ | 🟡 | ✅ | Monotonía del orden permite descartar 1 candidato por iter |
| 15 | [[15-3sum\|3Sum]] ⭐ | 🟡 | ✅ 📘C++ | Sort + fix one + two pointers (reducción de 3-Sum a 2-Sum) |
| 11 | [[11-container-with-most-water\|Container With Most Water]] | 🟡 | ✅ | Greedy local: mover el menor (argumento de descarte) |
| 42 | [[42-trapping-rain-water\|Trapping Rain Water]] | 🔴 | ✅ | Two pointers con tracking de máximos (3 niveles de optimización) |

---

## 03. Sliding Window — ✅ COMPLETO

> **Idea central del patrón**: ventana de tamaño variable o fijo que se desplaza por la colección, manteniendo invariantes. Para subarrays/substrings con propiedades.

| 🆔  | Problema                                                                                               | 🎚️ | Estado | Idea distintiva                                       |
| --- | ------------------------------------------------------------------------------------------------------ | --- | ------ | ----------------------------------------------------- |
| 121 | [[121-best-time-to-buy-and-sell-stock\|Best Time to Buy and Sell Stock]] ⭐                             | 🟢  | ✅ 📘C++ | Tracking de mínimo histórico (one-pass)               |
| 3   | [[3-longest-substring-without-repeating-characters\|Longest Substring Without Repeating Characters]] ⭐ | 🟡  | ✅      | Sliding window variable con set / dict de índices     |
| 424 | [[424-longest-repeating-character-replacement\|Longest Repeating Character Replacement]]               | 🟡  | ✅      | Sliding window con tolerancia (`len - max_freq <= k`) |
| 567 | [[567-permutation-in-string\|Permutation in String]]                                                   | 🟡  | ✅      | Sliding window de tamaño FIJO + match de frecuencias  |
| 76  | [[76-minimum-window-substring\|Minimum Window Substring]]                                              | 🔴  | ✅      | Sliding window con cobertura (`have / need`)          |
| 239 | [[239-sliding-window-maximum\|Sliding Window Maximum]]                                                 | 🔴  | ✅      | Deque monotónica decreciente (O(n) amortizado)        |

---

## 04. Stack — ✅ COMPLETO

> **Idea central del patrón**: estructura LIFO para procesar elementos en orden inverso al de inserción. Validación de paréntesis, evaluación de expresiones, "siguiente mayor/menor" (stack monotónico).

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 20 | [[20-valid-parentheses\|Valid Parentheses]] ⭐ | 🟢 | ✅ 📘C++ | LIFO para emparejar delimitadores |
| 155 | [[155-min-stack\|Min Stack]] | 🟡 | ✅ | Diseño de clase: stack auxiliar para min en O(1) |
| 150 | [[150-evaluate-reverse-polish-notation\|Evaluate Reverse Polish Notation]] | 🟡 | ✅ | Stack para evaluar expresiones (RPN) |
| 22 | [[22-generate-parentheses\|Generate Parentheses]] | 🟡 | ✅ | Backtracking con poda; intro al patrón 10 |
| 739 | [[739-daily-temperatures\|Daily Temperatures]] | 🟡 | ✅ | Stack monotónico decreciente ("próximo mayor") |
| 853 | [[853-car-fleet\|Car Fleet]] | 🟡 | ✅ | Sort + stack con tracking de ETA |
| 84 | [[84-largest-rectangle-in-histogram\|Largest Rectangle in Histogram]] | 🔴 | ✅ | Stack monotónico creciente para áreas máximas |

---

## 05. Binary Search — ✅ COMPLETO

> **Idea central del patrón**: búsqueda en O(log n) sobre estructuras ordenadas. La clave es **identificar la propiedad monotónica** que permite descartar la mitad del espacio en cada paso.

| 🆔  | Problema                                                                             | 🎚️ | Estado | Idea distintiva                                                  |
| --- | ------------------------------------------------------------------------------------ | --- | ------ | ---------------------------------------------------------------- |
| 704 | [[704-binary-search\|Binary Search]] ⭐                                               | 🟢  | ✅ 📘C++ | Template clásico; las 4 trampas (overflow, `<=`, `+1`/`-1`, `<`) |
| 74  | [[74-search-a-2d-matrix\|Search a 2D Matrix]]                                        | 🟡  | ✅      | Matriz como 1D virtual; `divmod(mid, n)`                         |
| 875 | [[875-koko-eating-bananas\|Koko Eating Bananas]]                                     | 🟡  | ✅      | Binary search **on answer** con función monotónica               |
| 153 | [[153-find-minimum-in-rotated-sorted-array\|Find Minimum in Rotated Sorted Array]] ⭐ | 🟡  | ✅      | Comparar con `nums[right]` para localizar pivote                 |
| 33  | [[33-search-in-rotated-sorted-array\|Search in Rotated Sorted Array]]                | 🟡  | ✅      | "Una mitad siempre ordenada" + árbol de 4 ramas                  |
| 981 | [[981-time-based-key-value-store\|Time Based Key-Value Store]]                       | 🟡  | ✅      | Diseño de clase + `bisect_right` para "último ≤ x"               |
| 4   | [[4-median-of-two-sorted-arrays\|Median of Two Sorted Arrays]]                       | 🔴  | ✅      | Binary search sobre **partición** (el más difícil)               |

---

## 06. Linked List — ✅ COMPLETO

> **Idea central del patrón**: manipulación de punteros (`prev`, `curr`, `next`) y dos punteros (slow / fast) para detectar ciclos, encontrar mitad, etc.

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 206 | [[206-reverse-linked-list\|Reverse Linked List]] ⭐ | 🟢 | ✅ 📘C++ | 3 punteros (prev/curr/next) — sub-rutina central |
| 21 | [[21-merge-two-sorted-lists\|Merge Two Sorted Lists]] ⭐ | 🟢 | ✅ | Dummy node + tail pointer |
| 141 | [[141-linked-list-cycle\|Linked List Cycle]] | 🟢 | ✅ | Floyd's tortoise & hare (slow/fast) |
| 143 | [[143-reorder-list\|Reorder List]] | 🟡 | ✅ | Composición: mid + reverse + merge alternado |
| 19 | [[19-remove-nth-node-from-end-of-list\|Remove Nth Node From End]] | 🟡 | ✅ | Two pointers con offset n+1 |
| 138 | [[138-copy-list-with-random-pointer\|Copy List with Random Pointer]] | 🟡 | ✅ | Hash map old→new para deep copy |
| 2 | [[2-add-two-numbers\|Add Two Numbers]] | 🟡 | ✅ | Suma con carry + dummy + `while l1 or l2 or carry` |
| 287 | [[287-find-the-duplicate-number\|Find the Duplicate Number]] | 🟡 | ✅ | Floyd sobre array (array como linked list virtual) |
| 146 | [[146-lru-cache\|LRU Cache]] ⭐ | 🟡 | ✅ | Doubly linked list + hash map; get/put en O(1) |
| 23 | [[23-merge-k-sorted-lists\|Merge K Sorted Lists]] | 🔴 | ✅ | Min-heap o divide-and-conquer; O(n log k) |
| 25 | [[25-reverse-nodes-in-k-group\|Reverse Nodes in K-Group]] | 🔴 | ✅ | Reverse en bloques con localización + reconexión |

---

## 07. Trees — ✅ COMPLETO

> **Idea central del patrón**: recursión sobre estructura jerárquica. DFS (preorder, inorder, postorder), BFS (level order), invariantes de BST. **Núcleo de entrevistas**.

| 🆔   | Problema                                                                                                           | 🎚️ | Estado | Idea distintiva                                   |
| ---- | ------------------------------------------------------------------------------------------------------------------ | --- | ------ | ------------------------------------------------- |
| 226  | [[226-invert-binary-tree\|Invert Binary Tree]] ⭐                                                                   | 🟢  | ✅ 📘C++ | Recursión simple, swap pythonic                   |
| 104  | [[104-maximum-depth-of-binary-tree\|Maximum Depth of Binary Tree]]                                                 | 🟢  | ✅      | `1 + max(left, right)` postorder                  |
| 543  | [[543-diameter-of-binary-tree\|Diameter of Binary Tree]]                                                           | 🟢  | ✅      | Recursión + tracker global (patrón maestro)       |
| 110  | [[110-balanced-binary-tree\|Balanced Binary Tree]]                                                                 | 🟢  | ✅      | Valor centinela `-1` para señalizar               |
| 100  | [[100-same-tree\|Same Tree]]                                                                                       | 🟢  | ✅      | Recursión paralela sobre 2 árboles                |
| 572  | [[572-subtree-of-another-tree\|Subtree of Another Tree]]                                                           | 🟢  | ✅      | Doble recursión: search + verify                  |
| 235  | [[235-lowest-common-ancestor-of-a-bst\|Lowest Common Ancestor of a BST]]                                           | 🟡  | ✅      | Aprovechar propiedad BST O(log n)                 |
| 102  | [[102-binary-tree-level-order-traversal\|Binary Tree Level Order Traversal]] ⭐                                     | 🟡  | ✅      | BFS con `deque`, snapshot de tamaño por nivel     |
| 199  | [[199-binary-tree-right-side-view\|Binary Tree Right Side View]]                                                   | 🟡  | ✅      | BFS + último de cada nivel                        |
| 1448 | [[1448-count-good-nodes-in-binary-tree\|Count Good Nodes in Binary Tree]]                                          | 🟡  | ✅      | DFS con acumulador top-down                       |
| 98   | [[98-validate-binary-search-tree\|Validate Binary Search Tree]]                                                    | 🟡  | ✅      | DFS con bounds (lower, upper) top-down            |
| 230  | [[230-kth-smallest-element-in-a-bst\|Kth Smallest Element in a BST]]                                               | 🟡  | ✅      | Inorder iterativo con stack                       |
| 105  | [[105-construct-binary-tree-from-preorder-and-inorder-traversal\|Construct Binary Tree from Preorder and Inorder]] | 🟡  | ✅      | Reconstrucción con índices + hash de inorder      |
| 124  | [[124-binary-tree-maximum-path-sum\|Binary Tree Maximum Path Sum]]                                                 | 🔴  | ✅      | Generalización de 543 con negativos (`max(., 0)`) |
| 297  | [[297-serialize-and-deserialize-binary-tree\|Serialize and Deserialize Binary Tree]]                               | 🔴  | ✅      | Preorder + N como marcador de None                |

---

## 08. Tries — ✅ COMPLETO

> **Idea central del patrón**: árbol de prefijos para búsquedas de string eficientes. Autocompletado, validación de palabras, búsqueda con wildcards.

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 208 | [[208-implement-trie-prefix-tree\|Implement Trie - Prefix Tree]] ⭐ | 🟡 | ✅ | Estructura básica con dict de hijos + `is_end` |
| 211 | [[211-design-add-and-search-words-data-structure\|Design Add and Search Words]] | 🟡 | ✅ | Trie + DFS para wildcards `'.'` |
| 212 | [[212-word-search-ii\|Word Search II]] | 🔴 | ✅ | Trie + backtracking en grid |

---

## 09. Heap / Priority Queue — ✅ COMPLETO

> **Idea central del patrón**: estructura ordenada por prioridad con O(log n) inserción/extracción del mínimo (o máximo). Top-K, scheduling, mediana en stream.

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 703 | [[703-kth-largest-element-in-a-stream\|Kth Largest in Stream]] | 🟢 | ✅ | Min-heap de tamaño k en streaming |
| 1046 | [[1046-last-stone-weight\|Last Stone Weight]] | 🟢 | ✅ | Max-heap simulado con negación |
| 973 | [[973-k-closest-points-to-origin\|K Closest Points to Origin]] | 🟡 | ✅ | Max-heap top-K + saltar `sqrt` |
| 215 | [[215-kth-largest-element-in-an-array\|Kth Largest Element in Array]] | 🟡 | ✅ | Sort vs heap vs **quickselect O(n)** |
| 621 | [[621-task-scheduler\|Task Scheduler]] | 🟡 | ✅ | Heap + queue de cooldown |
| 355 | [[355-design-twitter\|Design Twitter]] | 🟡 | ✅ | Diseño con dict + heap |
| 295 | [[295-find-median-from-data-stream\|Find Median from Data Stream]] ⭐ | 🔴 | ✅ | **Two heaps** (max-heap + min-heap) |

> 💡 Ya tocaste heap brevemente en [[347-top-k-frequent-elements]]; aquí se profundiza.

---

## 10. Backtracking — ✅ COMPLETO

> **Idea central del patrón**: explorar todas las posibles combinaciones / permutaciones recursivamente, con **poda** cuando una rama no puede llevar a solución. DFS sobre espacio de estados.

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 78 | [[78-subsets\|Subsets]] ⭐ | 🟡 | ✅ | "Incluir / no incluir" |
| 39 | [[39-combination-sum\|Combination Sum]] ⭐ | 🟡 | ✅ | Permitir repetir: `i` no `i+1` |
| 46 | [[46-permutations\|Permutations]] ⭐ | 🟡 | ✅ | `used[]` flag |
| 90 | [[90-subsets-ii\|Subsets II]] | 🟡 | ✅ | Sort + skip dups (`i > start`) |
| 40 | [[40-combination-sum-ii\|Combination Sum II]] | 🟡 | ✅ | `i+1` + skip dups combinados |
| 79 | [[79-word-search\|Word Search]] | 🟡 | ✅ | DFS en grid + marcar/restaurar |
| 131 | [[131-palindrome-partitioning\|Palindrome Partitioning]] | 🟡 | ✅ | Particionar string + check palíndromo |
| 17 | [[17-letter-combinations-of-a-phone-number\|Letter Combinations of a Phone Number]] | 🟡 | ✅ | Producto cartesiano |
| 51 | [[51-n-queens\|N-Queens]] | 🔴 | ✅ | Múltiples constraints (cols, `r+c`, `r-c`) |

---

## 11. Graphs — ✅ COMPLETO

> **Idea central del patrón**: BFS (niveles, distancia mínima) y DFS (conectividad, ciclos). Modelar matrices como grafos implícitos. **Núcleo de entrevistas tecnicas**.

| 🆔 | Problema | 🎚️ | Estado | Idea distintiva |
|---|---|---|---|---|
| 200 | [[200-number-of-islands\|Number of Islands]] ⭐ | 🟡 | ✅ | DFS en grid + componentes conexos |
| 133 | [[133-clone-graph\|Clone Graph]] | 🟡 | ✅ | DFS + hash old→new |
| 695 | [[695-max-area-of-island\|Max Area of Island]] | 🟡 | ✅ | DFS devolviendo área |
| 417 | [[417-pacific-atlantic-water-flow\|Pacific Atlantic Water Flow]] | 🟡 | ✅ | DFS desde bordes (inverso) |
| 130 | [[130-surrounded-regions\|Surrounded Regions]] | 🟡 | ✅ | DFS desde bordes + flip |
| 994 | [[994-rotting-oranges\|Rotting Oranges]] | 🟡 | ✅ | Multi-source BFS con tiempo |
| 286 | [[286-walls-and-gates\|Walls and Gates]] | 🟡 | ✅ | Multi-source BFS para distancias |
| 207 | [[207-course-schedule\|Course Schedule]] ⭐ | 🟡 | ✅ | DFS 3-colors o Kahn's algorithm |
| 210 | [[210-course-schedule-ii\|Course Schedule II]] | 🟡 | ✅ | Topological sort completo |
| 684 | [[684-redundant-connection\|Redundant Connection]] | 🟡 | ✅ | Union-Find básico |
| 323 | [[323-number-of-connected-components-in-an-undirected-graph\|Number of Connected Components]] | 🟡 | ✅ | DFS o UF para componentes |
| 261 | [[261-graph-valid-tree\|Graph Valid Tree]] | 🟡 | ✅ | UF + check `n-1` aristas |
| 127 | [[127-word-ladder\|Word Ladder]] | 🔴 | ✅ | BFS shortest path con patterns |

---

## 12. Advanced Graphs — ⏳ Pendiente

> **Idea central del patrón**: algoritmos clásicos sobre grafos ponderados: Dijkstra (camino más corto), Prim/Kruskal (árbol de coste mínimo), Bellman-Ford, topological sort.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 1584 | Min Cost to Connect All Points | 🟡 | ⏳ |
| 743 | Network Delay Time | 🟡 | ⏳ |
| 787 | Cheapest Flights Within K Stops | 🟡 | ⏳ |
| 332 | Reconstruct Itinerary | 🔴 | ⏳ |
| 778 | Swim in Rising Water | 🔴 | ⏳ |
| 269 | Alien Dictionary | 🔴 | ⏳ |

---

## 13. 1-D Dynamic Programming — ⏳ Pendiente

> **Idea central del patrón**: descomponer un problema en **subproblemas óptimos** con dependencia 1D (estado = un índice). El terror clásico que se domesticа con repetición.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 70 | Climbing Stairs ⭐ | 🟢 | ⏳ |
| 746 | Min Cost Climbing Stairs | 🟢 | ⏳ |
| 198 | House Robber ⭐ | 🟡 | ⏳ |
| 213 | House Robber II | 🟡 | ⏳ |
| 5 | Longest Palindromic Substring ⭐ | 🟡 | ⏳ |
| 647 | Palindromic Substrings | 🟡 | ⏳ |
| 91 | Decode Ways | 🟡 | ⏳ |
| 322 | Coin Change ⭐ | 🟡 | ⏳ |
| 152 | Maximum Product Subarray | 🟡 | ⏳ |
| 139 | Word Break | 🟡 | ⏳ |
| 300 | Longest Increasing Subsequence ⭐ | 🟡 | ⏳ |
| 416 | Partition Equal Subset Sum | 🟡 | ⏳ |

---

## 14. 2-D Dynamic Programming — ⏳ Pendiente

> **Idea central del patrón**: estado bidimensional (e.g. dos strings, dos índices). Las cumbres más altas del DP. Edit distance, knapsack, longest common subsequence.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 62 | Unique Paths ⭐ | 🟡 | ⏳ |
| 1143 | Longest Common Subsequence ⭐ | 🟡 | ⏳ |
| 309 | Best Time to Buy and Sell Stock with Cooldown | 🟡 | ⏳ |
| 518 | Coin Change II | 🟡 | ⏳ |
| 494 | Target Sum | 🟡 | ⏳ |
| 97 | Interleaving String | 🟡 | ⏳ |
| 72 | Edit Distance ⭐ | 🟡 | ⏳ |
| 329 | Longest Increasing Path in a Matrix | 🔴 | ⏳ |
| 115 | Distinct Subsequences | 🔴 | ⏳ |
| 312 | Burst Balloons | 🔴 | ⏳ |
| 10 | Regular Expression Matching | 🔴 | ⏳ |

---

## 15. Greedy — ⏳ Pendiente

> **Idea central del patrón**: tomar la decisión localmente óptima en cada paso. Simple cuando funciona; demostrar que funciona es lo difícil.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 53 | Maximum Subarray ⭐ | 🟡 | ⏳ |
| 55 | Jump Game ⭐ | 🟡 | ⏳ |
| 45 | Jump Game II | 🟡 | ⏳ |
| 134 | Gas Station | 🟡 | ⏳ |
| 846 | Hand of Straights | 🟡 | ⏳ |
| 1899 | Merge Triplets to Form Target Triplet | 🟡 | ⏳ |
| 763 | Partition Labels | 🟡 | ⏳ |
| 678 | Valid Parenthesis String | 🟡 | ⏳ |

---

## 16. Intervals — ⏳ Pendiente

> **Idea central del patrón**: ordenar intervalos por extremo (inicio o fin) y procesarlos linealmente. Solapamientos, fusiones, conflicts.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 252 | Meeting Rooms | 🟢 | ⏳ |
| 56 | Merge Intervals ⭐ | 🟡 | ⏳ |
| 57 | Insert Interval | 🟡 | ⏳ |
| 435 | Non-overlapping Intervals | 🟡 | ⏳ |
| 253 | Meeting Rooms II ⭐ | 🟡 | ⏳ |
| 1851 | Minimum Interval to Include Each Query | 🔴 | ⏳ |

---

## 17. Math & Geometry — ⏳ Pendiente

> **Idea central del patrón**: manipulación de matrices (rotación, espirales), aritmética de enteros grandes, geometría plana básica.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 202 | Happy Number | 🟢 | ⏳ |
| 66 | Plus One | 🟢 | ⏳ |
| 48 | Rotate Image ⭐ | 🟡 | ⏳ |
| 54 | Spiral Matrix ⭐ | 🟡 | ⏳ |
| 73 | Set Matrix Zeroes | 🟡 | ⏳ |
| 50 | Pow(x, n) | 🟡 | ⏳ |
| 43 | Multiply Strings | 🟡 | ⏳ |
| 2013 | Detect Squares | 🟡 | ⏳ |

---

## 18. Bit Manipulation — ⏳ Pendiente

> **Idea central del patrón**: operaciones a nivel de bits (AND, OR, XOR, shifts). Útil cuando el dominio está acotado por el ancho de un entero (32 o 64 bits).
> 💡 Si vienes de hardware/embebido, este patrón te resultará **familiar** — XOR para diferencias, máscaras de bits, etc. son lenguaje habitual de firmware C.

| 🆔 | Problema | 🎚️ | Estado |
|---|---|---|---|
| 136 | Single Number ⭐ | 🟢 | ⏳ |
| 191 | Number of 1 Bits | 🟢 | ⏳ |
| 338 | Counting Bits | 🟢 | ⏳ |
| 190 | Reverse Bits | 🟢 | ⏳ |
| 268 | Missing Number | 🟢 | ⏳ |
| 371 | Sum of Two Integers | 🟡 | ⏳ |
| 7 | Reverse Integer | 🟡 | ⏳ |

---

## Cómo trabajar con este índice

1. **Punto de entrada único**: cuando vayas a estudiar, abres este MOC y eliges un problema.
2. **Wikilinks activos** ✅ → archivo creado con el formato worked-example. Click directo.
3. **Pendientes** ⏳ → cuando estés listo para empezar uno nuevo, dímelo y lo redacto en el momento (o en lote por patrón completo, como hicimos con Arrays & Hashing).
4. **Estado en cada archivo**: la sección "Estado de progreso personal" al final de cada nota tiene checkboxes para tu seguimiento (leído / escrito desde cero / submitted en LeetCode / repaso semanal).
5. **Actualización del MOC**: cuando completemos un nuevo problema, actualizo la tabla de progreso global y marco el ✅ en su patrón.

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
- [Blind 75](https://www.teamblind.com/post/New-Year-Gift---Curated-List-of-Top-75-LeetCode-Questions-to-Save-Your-Time-OaM1orEU) — lista anterior, subset de NeetCode 150 (los marcados con ⭐ son aproximadamente Blind 75).

## Conexiones

- [[MOC_Programacion]] — área padre.
- Memoria asociada: `feedback_learning_style_algorithmic.md` (worked-example primero, no socrático para CS clásica).

---

## Consulta Dataview (problemas resueltos por dificultad)


> 💡 La consulta solo funciona si tienes el plugin **Dataview** instalado en Obsidian. Si no, ignórala — el MOC funciona igualmente.
