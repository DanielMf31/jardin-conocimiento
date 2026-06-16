---
title: Algoritmo de Dijkstra — caminos mínimos en grafos con pesos no negativos
date: 2026-05-11
tags: [programacion/cs-fundamentos, programacion/algoritmos, programacion/grafos]
type: nota
status: permanente
aliases: [Dijkstra, Dijkstra algorithm, caminos mínimos, shortest path]
---

# Algoritmo de Dijkstra — caminos mínimos en grafos con pesos no negativos

## Qué es y por qué importa

**Dijkstra** (D-i-j-k-s-t-r-a, holandés, inventado por **Edsger W. Dijkstra** en 1956 mientras tomaba café en Ámsterdam, publicado en 1959) es el **algoritmo clásico para encontrar el camino más corto** desde un nodo origen a todos los demás nodos en un grafo con **pesos no negativos** en las aristas.

Es uno de los 5-10 algoritmos que **TIENES QUE saber para grandes tecnologicas**. Aparece en:
- System design ("¿cómo funciona Google Maps?")
- LeetCode mediano-difícil (varios problemas NeetCode 150)
- Cualquier sistema que tenga que **rutear** algo: paquetes en red, vehículos en mapa, datos en mesh sensorial, NPCs en videojuegos.

## Vocabulario mínimo

| Término | Significado |
|---|---|
| Grafo | Conjunto de nodos (vértices) conectados por aristas. Puede ser dirigido (aristas con flecha) o no dirigido |
| Peso | Coste/distancia asociado a una arista. Para Dijkstra debe ser ≥ 0 |
| Origen (source) | Nodo desde el que calculamos distancias |
| Camino mínimo | Secuencia de aristas que conecta dos nodos con suma de pesos mínima |
| Relajar (relax) | Actualizar la distancia tentativa a un nodo si encontramos un camino mejor |
| V | Número de nodos (vertices) |
| E | Número de aristas (edges) |
| Min-heap / priority queue | Estructura que devuelve siempre el elemento de menor prioridad en O(log n) |

## Para qué sirve (aplicaciones reales)

| Aplicación | Qué representa el grafo |
|---|---|
| **Google Maps / Waze** | Nodos = intersecciones, aristas = tramos de calle, peso = tiempo o distancia |
| **Routing en internet (OSPF)** | Nodos = routers, aristas = enlaces, peso = latencia |
| **Pathfinding en videojuegos** | Nodos = celdas del mapa, aristas = movimientos, peso = coste de terreno |
| **Vuelos baratos** | Nodos = aeropuertos, aristas = vuelos, peso = precio o duración |
| **Redes eléctricas** | Nodos = subestaciones, aristas = líneas, peso = pérdida energética |
| **Robótica móvil** | Nodos = posiciones, aristas = movimientos, peso = energía/tiempo |
| **Mesh sensorial IoT** | Nodos = sensores ESP32, aristas = enlaces RF, peso = latencia/calidad |

El caso canónico: tienes un mapa, estás en A, quieres llegar a Z, ¿cuál es la ruta más corta? Dijkstra te lo dice en **O((V+E) log V)** — milisegundos para grafos de millones de nodos.

## Restricción crítica: pesos NO negativos

Esto es lo más importante a recordar. Dijkstra **falla con pesos negativos** porque su lógica greedy asume que una vez procesas un nodo, su distancia ya no puede mejorar. Si hubiera un peso negativo más adelante, esa asunción se rompe.

| Situación | Algoritmo correcto | Complejidad |
|---|---|---|
| Pesos no negativos, un origen → todos | **Dijkstra** | O((V+E) log V) |
| Pesos negativos posibles | **Bellman-Ford** | O(V·E) |
| Tienes heurística (sabes "hacia dónde") | **A\*** (A-star) | depende, más rápido en práctica |
| Caminos mínimos entre TODOS los pares | **Floyd-Warshall** | O(V³) |
| Grafo no ponderado (todos pesos = 1) | **BFS** | O(V+E) |

## Cómo funciona — la intuición

**Idea central**: como una **onda expansiva desde el origen**. Imagina que pones una gota de tinta en el nodo origen y se difunde por las aristas a velocidad inversamente proporcional al peso. El primer momento en que la tinta toca cada nodo es su distancia mínima desde el origen.

**Algoritmo en lenguaje natural**:

1. Mantén una tabla `dist[nodo]` con la distancia mínima conocida desde el origen a cada nodo. Inicialmente `dist[origen] = 0` y `dist[resto] = infinito`.
2. Mantén un **min-heap** (priority queue) de nodos ordenados por su `dist` actual.
3. Repite: saca del heap el nodo `u` con menor `dist`. Para cada vecino `v` de `u`, comprueba si `dist[u] + peso(u,v) < dist[v]`. Si sí, **relaja**: actualiza `dist[v]` y mete `v` al heap.
4. Una vez sacas un nodo del heap, **su distancia es definitiva** (esto es la clave; solo funciona porque los pesos son ≥ 0).
5. Termina cuando el heap está vacío (o cuando sacas el nodo destino, si solo te interesa uno).

## Ejemplo trace paso a paso

Grafo dirigido pequeño:

```
A → B  peso 4
A → D  peso 1
D → C  peso 3
B → C  peso 2
```

Visualmente:

```
        4
   A ───────► B
   │           │
 1 │         2 │
   ▼           ▼
   D ───►───── C
        3
```

**Pregunta**: distancia mínima desde A a todos los nodos.

**Estado inicial**:

| Nodo | dist | procesado | heap |
|---|---|---|---|
| A | 0 | no | [(0, A)] |
| B | ∞ | no | |
| C | ∞ | no | |
| D | ∞ | no | |

**Paso 1**: sacar (0, A) del heap. Procesar vecinos:
- A→B: nuevo dist = 0+4 = 4 < ∞ → actualizar B=4, push (4, B)
- A→D: nuevo dist = 0+1 = 1 < ∞ → actualizar D=1, push (1, D)

| Nodo | dist | procesado | heap |
|---|---|---|---|
| A | 0 | ✓ | [(1, D), (4, B)] |
| B | 4 | no | |
| C | ∞ | no | |
| D | 1 | no | |

**Paso 2**: sacar (1, D). Procesar vecinos:
- D→C: nuevo dist = 1+3 = 4 < ∞ → actualizar C=4, push (4, C)

| Nodo | dist | procesado | heap |
|---|---|---|---|
| A | 0 | ✓ | [(4, B), (4, C)] |
| B | 4 | no | |
| C | 4 | no | |
| D | 1 | ✓ | |

**Paso 3**: sacar (4, B). Vecinos:
- B→C: nuevo dist = 4+2 = 6, pero dist[C] ya es 4. **No mejora**, no actualizar.

| Nodo | dist | procesado | heap |
|---|---|---|---|
| A | 0 | ✓ | [(4, C)] |
| B | 4 | ✓ | |
| C | 4 | no | |
| D | 1 | ✓ | |

**Paso 4**: sacar (4, C). C no tiene vecinos.

**Resultado**:
- A → A: 0
- A → D: 1 (ruta: A→D)
- A → B: 4 (ruta: A→B)
- A → C: 4 (ruta: A→D→C, no A→B→C que sería 6)

## Implementación en Python (la que vas a escribir en interview)

```python
import heapq

def dijkstra(graph, start):
    """
    graph: dict {nodo: [(vecino, peso), ...]}
    start: nodo origen
    return: dict {nodo: distancia_minima}
    """
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]  # (distancia, nodo)

    while heap:
        d, u = heapq.heappop(heap)

        # Optimización clave: skip si ya procesamos con dist menor
        if d > dist[u]:
            continue

        for v, peso in graph[u]:
            nueva_dist = d + peso
            if nueva_dist < dist[v]:
                dist[v] = nueva_dist
                heapq.heappush(heap, (nueva_dist, v))

    return dist
```

**Uso**:

```python
graph = {
    'A': [('B', 4), ('D', 1)],
    'B': [('C', 2)],
    'C': [],
    'D': [('C', 3)],
}
print(dijkstra(graph, 'A'))
# {'A': 0, 'B': 4, 'C': 4, 'D': 1}
```

**Detalles importantes del código**:

- `heap = [(0, start)]`: el heap guarda tuplas `(distancia, nodo)`. Python compara tuplas lexicográficamente, así que ordena por distancia.
- `if d > dist[u]: continue`: optimización **lazy deletion**. Python `heapq` no tiene `decrease-key`. En vez de actualizar la entrada vieja, metemos una nueva y dejamos la vieja como "basura". Cuando sale, comprobamos si su `d` ya es peor que el `dist[u]` actual, y si es así, la ignoramos. Mantiene la complejidad correcta.
- Si solo quieres distancia a UN destino, puedes salir antes con `if u == destino: return dist[u]`.

## Complejidad

| Implementación | Complejidad | Cuándo usar |
|---|---|---|
| Lista + búsqueda lineal | O(V²) | Grafos densos pequeños |
| Min-heap binario (Python `heapq`) | **O((V+E) log V)** | **El caso típico, lo que harás siempre** |
| Heap de Fibonacci | O(E + V log V) | Teórico, no se usa en práctica |

Donde V = nodos, E = aristas.

**Por qué O((V+E) log V)**: cada arista se procesa una vez (cada relajación es O(log V) por el push al heap). Cada nodo sale del heap a lo sumo una vez (pero puede entrar varias por la lazy deletion). En total: O(E log V) por las relajaciones + O(V log V) por las extracciones.

## Cómo reconstruir el camino (no solo la distancia)

Si necesitas saber QUÉ nodos forman la ruta óptima (no solo "cuesta 4"), añade un dict `parent`:

```python
def dijkstra_with_path(graph, start, end):
    dist = {node: float('inf') for node in graph}
    parent = {node: None for node in graph}
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == end:
            break

        for v, peso in graph[u]:
            nueva_dist = d + peso
            if nueva_dist < dist[v]:
                dist[v] = nueva_dist
                parent[v] = u
                heapq.heappush(heap, (nueva_dist, v))

    # Reconstruir camino end → start → invertir
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return list(reversed(path)), dist[end]
```

## Trampas típicas

1. **No olvidar el `if d > dist[u]: continue`**. Sin esto, procesas nodos múltiples veces y la complejidad se rompe.

2. **Pesos negativos**: si la entrada los permite, NO uses Dijkstra. Es la pregunta de seguimiento más común en interview: "¿y si hay pesos negativos?" → respuesta: Bellman-Ford.

3. **Grafos no ponderados**: si todos los pesos son 1, no necesitas Dijkstra — usa **BFS**, que es O(V+E) sin el factor log.

4. **No confundir con BFS**: BFS funciona porque "todas las aristas pesan 1, así que niveles = distancia". Dijkstra es BFS + heap para manejar pesos arbitrarios no negativos.

5. **Inicializar `dist[start] = 0`** y meter `(0, start)` al heap. Olvidarlo es bug clásico.

6. **`graph[u]`** debe existir aunque `u` no tenga vecinos. Si usas `dict`, asegúrate que cada nodo tiene una entrada (vacía si hace falta) o usa `graph.get(u, [])`.

## Variantes y problemas relacionados

| Problema | Variante de Dijkstra |
|---|---|
| Caminos mínimos de A a TODOS | Dijkstra estándar |
| Camino mínimo de A a B | Dijkstra con early exit cuando sale B |
| Camino mínimo con K paradas máximo | Dijkstra modificado (estado = (nodo, paradas_usadas)) — LeetCode 787 |
| Camino con menor ESFUERZO máximo (no suma) | Dijkstra cambiando "suma" por "max" — LeetCode 1631 |
| Tiempo mínimo de propagación (red) | Dijkstra desde origen, devolver max(dist) — LeetCode 743 |
| Tiempo de "natación" en grid | Dijkstra en grid, peso = max(elev_actual, elev_vecino) — LeetCode 778 |

## Aplicación al perfil del usuario

**Problemas NeetCode 150 que usan Dijkstra** (orden recomendado de práctica):

1. **743 Network Delay Time** — Dijkstra "puro" sobre lista de aristas. Es "Dijkstra de libro de texto". Hazlo primero.
2. **787 Cheapest Flights Within K Stops** — Dijkstra con estado extendido (nodo, k). Variante interesante.
3. **1631 Path with Minimum Effort** — Dijkstra en grid 2D con relajación por max() en vez de suma. Cambia el "operator" de Dijkstra.
4. **778 Swim in Rising Water** — Otra variante en grid 2D, similar a 1631.
5. **2421 Number of Good Paths** — más avanzado, usa Union-Find pero conceptos relacionados.

**Para perfiles de hardware/IoT** (embebido y extensiones): si extiendes a mesh multi-nodo donde varios ESP32 deben rutar datos al gateway con peso = calidad de enlace (RSSI o latencia), Dijkstra es la herramienta directa. Cualquier algoritmo de routing en red propio se basa en él (RIP, OSPF, etc.).

## Checklist de dominio

Sabes Dijkstra cuando puedes en 5 minutos sin mirar:

1. Explicar la idea (greedy, onda expansiva, pesos no negativos).
2. Identificar cuándo usarlo vs BFS / Bellman-Ford / A*.
3. Escribir la implementación con `heapq` desde cero, incluyendo el `if d > dist[u]: continue`.
4. Trazar manualmente un grafo pequeño (4-5 nodos) paso a paso.
5. Saber su complejidad (O((V+E) log V)) y por qué.
6. Saber reconstruir el camino con un dict `parent`.
7. Identificar las 2-3 variantes típicas (peso = max, estado extendido con k paradas).

## Resumen mental

> "Dijkstra es **BFS + heap** para grafos con **pesos no negativos**. Mantienes `dist[nodo]` tentativo, sacas siempre el nodo de menor `dist` del min-heap, **relajas** sus vecinos. Cuando sale del heap, su distancia es definitiva. O((V+E) log V). Si hay pesos negativos → Bellman-Ford. Si no hay pesos → BFS. Si tienes heurística → A*."

## Conexiones

- [[MOC_CS_Fundamentos]]
- [[MOC_NeetCode_150]]
- [[MOC_Programacion]]

## Fuente

Conversación con Claude Code, 2026-05-11. Referencia clásica: CLRS (Cormen et al.), capítulo 24 "Single-Source Shortest Paths". También cubierto en *Algorithms* de Sedgewick & Wayne y en MIT 6.006 (lectures 14-15).
