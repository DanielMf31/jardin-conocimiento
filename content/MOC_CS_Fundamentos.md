---
title: MOC CS Fundamentos — auto-estudio Computer Science
date: 2026-05-10
tags: [moc, programacion, programacion/cs-fundamentos, programacion/teoria, networking, operating-systems, concurrency, system-design, database-internals, distributed-systems, computer-architecture, security, compilers]
type: moc
status: permanente
aliases: [MOC CS Fundamentos, MOC Computer Science, MOC Teoria CS, CS para SWE Google, Hoja ruta CS interview prep]
---

# MOC CS Fundamentos — auto-estudio Computer Science

> 📍 **Punto de entrada único** al cluster de **teoría CS** que cubre la brecha del 20% teórico del plan de estudio. Paralelo a [[MOC_NeetCode_150]] .
>
> 🎯 **Objetivo**: cubrir los temas que NO salen automáticamente de hacer NeetCode + Build Things pero **sí preguntan en entrevistas tecnicas** (sobre todo system design + behavioral).
>
> 📚 **Filosofía**: **referencia teórica permanente**, NO roadmap de proyectos. Si la pregunta es *"¿cómo lo construyo?"* →. Si la pregunta es *"¿por qué funciona así?"* o *"¿qué tradeoffs tiene?"* → este MOC.
>
> ⏱️ **Cadencia**: 1-2h/semana sostenidas (= 20% del plan de estudio). NO robar tiempo a NeetCode ni Build Things.
>
> 🛡️ **Convenciones de iconos**: ✅ doc creado y leído · 🚧 doc creado, pendiente leer · ⏳ pendiente crear · ⭐ recomendado especialmente · 🔥 frecuente en interviews · 🆔 tier (1=crítico, 2=importante, 3=opcional).

## Resumen de progreso

| Tier | Tema | Total docs | ✅ | 🚧 | ⏳ | % |
|---|---|---|---|---|---|---|
| **1** | Networking | 5 | 0 | **5** | 0 | **100%** creados |
| **1** | Operating Systems | 5 | 0 | **5** | 0 | **100%** creados |
| **1** | Concurrency | 4 | 0 | **4** | 0 | **100%** creados |
| **1** | System Design Patterns | 5 | 0 | **5** | 0 | **100%** creados |
| **1** | Database Internals | 5 | 0 | **5** | 0 | **100%** creados |
| **2** | Distributed Systems | 4 | 0 | **4** | 0 | **100%** creados |
| **2** | Computer Architecture | 3 | 0 | **3** | 0 | **100%** creados |
| **2** | Security | 4 | 0 | **4** | 0 | **100%** creados |
| **3** | Compilers / Interpreters | 2 | 0 | **2** | 0 | **100%** creados |
| **1** | **Algorithms (clásicos)** | abierto | 0 | **1** | — | en construcción bajo demanda |
| **TOTAL** | | **37+** | **0** | **38** | **0** | — |

> 💡 **No hace falta crearlos todos a la vez**. Cada doc lleva 30-60 min de creación + 1-2h de tu lectura. Cadencia recomendada: 1-2 docs/mes sostenidos. Llegas a Tier 1 completo en ~6 meses.

---

## TIER 1 — CRÍTICOS para entrevistas tecnicas

> Estos son los temas que aparecen explícita o implícitamente en **system design + behavioral interviews**. Sin ellos, **te crujen** en cuanto la conversación deja el algoritmo puro. Crear los 23 docs en los primeros 6 meses (mayo-noviembre 2026).

### 1. Networking — la base de todo

> **Todo lo que sucede entre máquinas**. Si vas a tocar APIs, microservicios, cloud, cualquier cosa distribuida, esto es la base. **El más urgente** del cluster.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 1.1 | [[01_networking/01-tcp-ip-osi\|TCP/IP + OSI model]] 🔥 ⭐ | 🚧 | 7 capas OSI, 4 capas TCP/IP, encapsulación, three-way handshake, TCP vs UDP, sliding window |
| 1.2 | [[01_networking/02-http-y-evolucion\|HTTP — del 1.0 al 3.0]] 🔥 | 🚧 | Métodos, status codes, headers, cookies, HTTP/1.1 keep-alive, HTTP/2 multiplexing, HTTP/3 QUIC |
| 1.3 | [[01_networking/03-dns-resolucion-nombres\|DNS y resolución de nombres]] | 🚧 | Recursividad, caching, A/AAAA/CNAME/MX, TTL, anycast, root servers |
| 1.4 | [[01_networking/04-sockets-y-puertos\|Sockets y puertos]] 🔥 | 🚧 | Berkeley sockets, well-known ports, socket lifecycle, blocking vs non-blocking, IO models |
| 1.5 | [[01_networking/05-tls-https\|TLS y HTTPS]] | 🚧 | Handshake TLS 1.3, asymmetric vs symmetric, certificate chain, MITM, Let's Encrypt |

### 2. Operating Systems — qué pasa por debajo

> Cómo el SO orquesta procesos, memoria y hardware. **Aparece en interviews "¿qué pasa cuando ejecutas `ls`?"** y similares.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 2.1 | `02_operating_systems/01-procesos-y-threads.md` 🔥 ⭐ | ⏳ | Process vs thread, fork/exec, context switching, GIL Python |
| 2.2 | `02_operating_systems/02-memoria-virtual-paging.md` | ⏳ | Virtual address, page tables, TLB, swap, OOM killer |
| 2.3 | `02_operating_systems/03-scheduling.md` | ⏳ | Round-robin, priority, CFS Linux, preemptive vs cooperative |
| 2.4 | `02_operating_systems/04-syscalls-y-kernel.md` | ⏳ | User vs kernel space, syscall mechanism, strace, signals |
| 2.5 | `02_operating_systems/05-filesystems.md` | ⏳ | inode, journaling (ext4, btrfs), permissions, mounts |

### 3. Concurrency — cuando varias cosas a la vez se rompen

> Lo más fácil de **escribir mal** y lo más difícil de **debuggear**. Aparece directamente en interview senior y en cualquier sistema con threads/async.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 3.1 | `03_concurrency/01-race-conditions.md` 🔥 | ⏳ | TOCTOU, atomic ops, ABA problem, ejemplo clásico cuenta bancaria |
| 3.2 | `03_concurrency/02-locks-y-mutex.md` ⭐ | ⏳ | Mutex, semaphore, spinlock, RWLock, reentrant locks |
| 3.3 | `03_concurrency/03-deadlock-livelock.md` 🔥 | ⏳ | 4 condiciones Coffman, dining philosophers, prevention vs avoidance |
| 3.4 | `03_concurrency/04-async-vs-threads-vs-procesos.md` ⭐ | ⏳ | Cooperative vs preemptive, asyncio, GIL, multiprocessing, cuándo cada uno |

### 4. System Design Patterns — el currículo de la system design interview

> Patrones que aparecen en **toda** system design entrevistas tecnicas. Saberlos por nombre + tradeoffs te diferencia.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 4.1 | `04_system_design_patterns/01-load-balancing.md` 🔥 ⭐ | ⏳ | L4 vs L7, round-robin, least-conn, consistent hashing, health checks |
| 4.2 | `04_system_design_patterns/02-caching-strategies.md` 🔥 ⭐ | ⏳ | Cache-aside, write-through, write-behind, TTL, eviction (LRU/LFU) |
| 4.3 | `04_system_design_patterns/03-message-queues.md` 🔥 | ⏳ | Push vs pull, at-least-once vs at-most-once, dead letter, Kafka vs RabbitMQ |
| 4.4 | `04_system_design_patterns/04-cdn-y-edge.md` | ⏳ | Origin, edge, cache invalidation, geo-routing, Cloudflare/Akamai |
| 4.5 | `04_system_design_patterns/05-rate-limiting.md` 🔥 | ⏳ | Token bucket, leaky bucket, fixed/sliding window, distribuido vs local |

### 5. Database Internals — qué pasa dentro de Postgres/MySQL

> Las preguntas típicas en interview backend: "¿qué es un índice?", "¿qué hace REPEATABLE READ?", "¿cuándo NoSQL?". Sin esto te quedas en superficial.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 5.1 | `05_database_internals/01-b-trees-y-indexing.md` 🔥 ⭐ | ⏳ | B-tree vs B+tree, clustered vs secondary, covering index, EXPLAIN |
| 5.2 | `05_database_internals/02-acid-transactions.md` 🔥 | ⏳ | ACID, WAL, 2PC, savepoints, qué garantiza realmente cada DB |
| 5.3 | `05_database_internals/03-isolation-levels.md` 🔥 ⭐ | ⏳ | Read uncommitted/committed, repeatable read, serializable, MVCC |
| 5.4 | `05_database_internals/04-replication-y-sharding.md` | ⏳ | Master-slave, multi-master, sync vs async, sharding strategies |
| 5.5 | `05_database_internals/05-sql-vs-nosql-tradeoffs.md` | ⏳ | Relational, document, key-value, columnar, graph; cuándo cada uno |

---

## TIER 2 — IMPORTANTES (meses 6-12)

> Para system design avanzado. No críticos para júnior absoluto pero sí valorados.

### 6. Distributed Systems

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 6.1 | `06_distributed_systems/01-cap-pacelc.md` 🔥 | ⏳ | CAP teorema, PACELC extension, ejemplos prácticos por DB |
| 6.2 | `06_distributed_systems/02-consensus-paxos-raft.md` ⭐ | ⏳ | Por qué consensus es difícil, Paxos básico, Raft (más entendible) |
| 6.3 | `06_distributed_systems/03-eventual-consistency.md` | ⏳ | Strong vs eventual, vector clocks, CRDTs, Dynamo paper |
| 6.4 | `06_distributed_systems/04-distributed-tracing.md` | ⏳ | OpenTelemetry, span/trace, contexto distribuido, Jaeger/Zipkin |

### 7. Computer Architecture

> Menos en SWE puro pero relevante para perfiles de hardware/IoT y para entender por qué algunas cosas son rápidas o lentas.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 7.1 | `07_computer_architecture/01-cpu-pipeline-y-registros.md` | ⏳ | Pipeline, branch prediction, superscalar, instrucción → ejecución |
| 7.2 | `07_computer_architecture/02-jerarquia-de-memoria-y-cache.md` ⭐ | ⏳ | L1/L2/L3, cache lines, locality (espacial/temporal), false sharing |
| 7.3 | `07_computer_architecture/03-coherencia-cache-multicore.md` | ⏳ | MESI protocol, memory barriers, atomic ops a bajo nivel |

### 8. Security

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 8.1 | `08_security/01-tls-handshake-detallado.md` ⭐ | ⏳ | TLS 1.3 step-by-step, ECDHE, perfect forward secrecy, certificate pinning |
| 8.2 | `08_security/02-hashing-vs-cifrado.md` | ⏳ | bcrypt, argon2, AES, RSA, salt, rainbow tables |
| 8.3 | `08_security/03-owasp-top-10.md` 🔥 | ⏳ | Injection, broken auth, XSS, CSRF, SSRF, los 10 con ejemplos |
| 8.4 | `08_security/04-jwt-y-session-management.md` | ⏳ | Stateful vs stateless, refresh tokens, revocation, secure storage |

---

## TIER 3 — OPCIONAL (post-12 meses)

### 9. Compilers / Interpreters

> Educativo, no crítico para interview júnior. Solo si te apetece profundizar después.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 9.1 | `09_compilers_interpreters/01-lexer-parser-ast.md` | ⏳ | Tokenización, gramáticas, recursive descent, AST, ejemplo calculadora |
| 9.2 | `09_compilers_interpreters/02-runtime-y-vm.md` | ⏳ | Bytecode, GC (mark-sweep, generacional), CPython internals, JIT |

---

## CLUSTER PARALELO — Algorithms clásicos (creado bajo demanda)

> **Cluster abierto** que crece según vayan apareciendo dudas conceptuales sobre **algoritmos clásicos** (Dijkstra, Bellman-Ford, A*, Floyd-Warshall, MST Kruskal/Prim, Union-Find, KMP, etc.). Complementario a [[MOC_NeetCode_150]]: NeetCode entrena los **patrones generales** (sliding window, two pointers, DP); aquí van los **algoritmos con nombre propio** que tienen identidad técnica fuerte y aparecen como tales en interview/system design.
>
> **Criterio para crear doc**: el algoritmo tiene nombre propio (de inventor o canónico), aparece en CLRS / Sedgewick, y tiene aplicaciones recurrentes que merecen referencia permanente.

| # | Doc | Estado | Conceptos clave |
|---|---|---|---|
| 10.1 | [[10_algorithms/01-dijkstra\|Dijkstra — caminos mínimos pesos no negativos]] 🔥 ⭐ | 🚧 | Min-heap, relajación, O((V+E) log V), lazy deletion, vs BFS/Bellman-Ford/A* |
| 10.2 | `10_algorithms/02-bellman-ford.md` (pendiente) | ⏳ | Pesos negativos, V-1 iteraciones, detección ciclos negativos |
| 10.3 | `10_algorithms/03-a-star.md` (pendiente) | ⏳ | Heurística admisible, f=g+h, pathfinding óptimo en práctica |
| 10.4 | `10_algorithms/04-floyd-warshall.md` (pendiente) | ⏳ | All-pairs shortest paths, O(V³), DP en grafos |
| 10.5 | `10_algorithms/05-union-find.md` (pendiente) | ⏳ | Path compression, union by rank, casi O(1) amortizado |
| 10.6 | `10_algorithms/06-mst-kruskal-prim.md` (pendiente) | ⏳ | Minimum spanning tree, greedy, redes/clustering |
| 10.7 | `10_algorithms/07-kmp-string-matching.md` (pendiente) | ⏳ | Búsqueda subcadena O(n+m), tabla LPS |
| 10.8 | `10_algorithms/08-topological-sort.md` (pendiente) | ⏳ | DAG, Kahn vs DFS, dependencies, build systems |

---

## Workflow de estudio

```
CADENCIA SEMANAL TÍPICA:
  Lunes/Martes:    NeetCode (algoritmos) — 2-3h
  Miércoles:       Build Things — 2-3h
  Jueves:          CS Fundamentos LECTURA — 1h ← teoría
  Viernes:         Build Things — 2-3h
  Sábado:          NeetCode + revisión — 2h
  Domingo:         libre o atomización en vault

Total CS Fundamentos: ~1-2h/semana (4-8h/mes)
Cuadra con 20% del plan de estudio

POR DOC NUEVO:
  1. Lectura completa (1-2h, una sentada)
  2. Active recall: 2-3 días después, intenta explicar el doc sin mirar
  3. Atomización opcional: notas atómicas en 10_Notas/ con tag cs/<tema>
  4. Aplicación: cuando hagas un Build Things relacionado, releer la sección clave
```

## Criterio "CS Fundamentos vs Build Things"

```
"¿Cómo lo construyo?"               → MOC_Build_Things
"¿Por qué funciona así?"            → MOC_CS_Fundamentos
"¿Qué tradeoffs tiene esto?"        → MOC_CS_Fundamentos
"¿Qué pasa internamente con X?"     → MOC_CS_Fundamentos

EJEMPLOS:
  "Implementar Redis cache en mi API"           → Build Things T1.3
  "¿Por qué Redis es más rápido que Postgres?"  → CS Fund 5.1 (DB internals)
  "¿Qué pasa cuando llamo socket.send()?"       → CS Fund 1.4 (Sockets)
  "Build Your Own Load Balancer"                → Build Things T2.2
  "¿Por qué round-robin vs least-connections?"  → CS Fund 4.1 (Load balancing)
```

## Recursos generales (referencia rápida)

### Libros core
- **Designing Data-Intensive Applications** (Martin Kleppmann, 2017) — DB + Distributed (cubre Tier 1.5 + Tier 2.6 enteros)
- **Operating Systems: Three Easy Pieces** (Remzi Arpaci-Dusseau, GRATIS online en pages.cs.wisc.edu/~remzi/OSTEP/) — Tier 1.2 entero
- **Computer Networking: A Top-Down Approach** (Kurose & Ross) — Tier 1.1 completo
- **Computer Systems: A Programmer's Perspective** (Bryant & O'Hallaron, "CSAPP") — Tier 2.7 + parte 1.2
- **System Design Interview** (Alex Xu, vol 1+2) — Tier 1.4 entero

### Cursos online gratis
- **MIT 6.006 / 6.046** Algorithms (YouTube) — complemento NeetCode
- **MIT 6.824** Distributed Systems (YouTube) — Tier 2.6 nivel posgrado
- **Stanford CS144** Computer Networking — Tier 1.1
- **CS50** Harvard intro — bueno para review fundamentals

### Newsletters / blogs
- **High Scalability** — case studies sistemas reales
- **The Pragmatic Engineer** (Gergely Orosz) — system design real-world
- **ByteByteGo** — system design visual semanal
- **Hillel Wayne — Computer Things** — formal methods + teoría

### YouTube channels
- **ByteByteGo** — diagramas system design
- **Gaurav Sen** — system design interviews
- **Hussein Nasser** — networking + DBs
- **Engineer Man** — concurrency, OS internals
- **Computerphile** — CS general

## Conexiones

- [[MOC_Programacion]] — área padre
- [[MOC_NeetCode_150]] — sub-MOC paralelo
- — sub-MOC paralelo

---

## Consultas Dataview futuras

### Notas atómicas CS por tema

### Docs CS Fundamentos por estado
