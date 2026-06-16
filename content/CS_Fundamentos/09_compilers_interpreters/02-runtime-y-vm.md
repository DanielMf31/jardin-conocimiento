# 02 — Runtime y VMs

> 📚 **Doc 2 (último) del cluster Compilers (Tier 3 opcional)**. Qué pasa con el AST después del parsing. Bytecode, garbage collection, JIT compilation. Por qué Python es lento y Java/JS son sorprendentemente rápidos.
> 🎓 **Para quién**: opcional, útil para entender por qué tu código va a la velocidad que va.
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Del AST al programa ejecutándose

Después del parsing tienes un AST. Para ejecutar el programa hay varias estrategias:

1. **Tree-walking interpreter**: recorre el AST y ejecuta directamente. Simple pero muy lento.
2. **Bytecode interpreter**: AST → bytecode → loop que interpreta. Lo que hace Python (CPython).
3. **JIT compiler**: bytecode + análisis runtime → código máquina dinámico. Lo que hace V8 (JS), HotSpot (Java), PyPy.
4. **AOT compiler**: AST → optimizaciones → código máquina antes de ejecutar. C, Rust, Go.

Cada estrategia tiene trade-offs entre **velocidad de compilación**, **velocidad de ejecución**, **flexibilidad** y **portabilidad**.

---

## 2. Tree-walking interpreters

El más simple. Recorre el AST recursivamente, evaluando cada nodo:

```python
def evaluate(node):
    if isinstance(node, Constant):
        return node.value
    if isinstance(node, BinaryOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if node.op == '+': return left + right
        if node.op == '*': return left * right
    if isinstance(node, Variable):
        return env[node.name]
    # ...
```

**Pros**: trivial de implementar. Bueno para REPLs, DSLs pequeños, scripting.

**Contras**: lentísimo. Por cada operación, allocations + dispatch + recursion. ~100x más lento que código compilado.

Lenguajes que usan: Bash, muchos DSLs internos, primera versión de Ruby (antes de YARV).

---

## 3. Bytecode interpreters

Mucho más rápido. El compiler traduce el AST a una secuencia de **bytecodes** (instrucciones simples para una máquina virtual abstracta). Después un loop interpreta los bytecodes.

### CPython como ejemplo

CPython convierte tu .py a bytecode (.pyc files). El bytecode lo ejecuta una **VM** (Virtual Machine) escrita en C.

Ejemplo:
```python
def add(a, b):
    return a + b
```

Bytecode (puedes verlo con `dis` module):
```
LOAD_FAST    a
LOAD_FAST    b
BINARY_ADD
RETURN_VALUE
```

La VM tiene un loop tipo:
```c
while (true) {
    instruction = next_bytecode();
    switch (instruction) {
        case LOAD_FAST: push(stack, locals[arg]); break;
        case BINARY_ADD: b = pop(); a = pop(); push(a + b); break;
        case RETURN_VALUE: return pop();
        // ...
    }
}
```

### Stack-based vs register-based VMs

**Stack-based** (CPython, JVM): instrucciones operan sobre una pila. Más simples y portables. Más instrucciones por operación pero cada una rápida.

**Register-based** (V8, Lua, Dalvik antiguo Android): instrucciones tienen "registros virtuales". Menos instrucciones pero más complejas.

Trade-off de diseño. Stack-based es más simple pedagogicamente y maneja optimizaciones distintas.

### Pros y contras de bytecode

**Pros**:
- Mucho más rápido que tree-walking (10-50x).
- Portable (mismo bytecode corre en cualquier OS con la VM).
- Compilación rápida (no hay que generar código máquina).

**Contras**:
- Aún más lento que código compilado (1-10x más lento que C).
- Cada operación pasa por el dispatch loop.
- No optimiza basándose en runtime info.

Lenguajes: Python (CPython), Ruby (YARV), Lua, Erlang, Java pre-JIT.

---

## 4. JIT compilation — el siguiente nivel

**JIT** = Just-In-Time. Compila a código máquina **mientras el programa corre**. Combina lo mejor de bytecode (portabilidad) y código nativo (velocidad).

### Cómo funciona

1. Inicialmente: ejecuta como bytecode (rápido de empezar).
2. Mientras corre, identifica **hot code** (loops, funciones llamadas mucho).
3. Compila hot code a código máquina optimizado.
4. Reemplaza calls al bytecode por jumps al código nativo.

### Optimizaciones que JIT puede hacer (que AOT no)

JIT tiene **información que el compiler estático no**:

- **Tipos reales en runtime**: si un parameter siempre llega como int, puede compilar versión int-specific (más rápida que polymorphic).
- **Branch prediction profile-guided**: sabe qué branches se toman frecuentemente.
- **Inlining agresivo**: funciones llamadas mucho se inlinen sin pensar en code size.
- **Speculative optimizations**: asume comportamiento común, deopt si cambia.
- **Polymorphic inline caches**: optimiza method dispatch.

### Trade-offs JIT

**Pros**: rápido en steady-state. Puede superar a código C en algunos casos (más info runtime).

**Contras**:
- **Warmup time**: los primeros segundos/minutos son más lentos (bytecode + compilation overhead).
- **Memory overhead**: necesita guardar bytecode + código compilado + estructuras de optimización.
- **Predictability**: deoptimizations pueden causar latency spikes.
- **Embebidos / startup-sensitive**: malo para CLIs (warmup es overhead total).

### Implementaciones famosas

- **HotSpot (Java JVM)**: 2 tiers de JIT. C1 rápido, C2 agresivo.
- **GraalVM**: alternativa moderna a HotSpot. Soporta multi-language.
- **V8 (Chrome, Node)**: TurboFan optimizing compiler + Ignition interpreter.
- **PyPy**: implementación alternativa de Python con tracing JIT. 5-10x más rápido que CPython en muchos workloads.
- **LuaJIT**: una de las JITs más rápidas, brutalmente optimizada.
- **JuliaLang**: AOT + JIT mediante LLVM.

---

## 5. AOT compilation — el clásico

**AOT** = Ahead-Of-Time. Compila TODO antes de ejecutar. Resultado: binario nativo que se ejecuta directamente.

### Pipeline típico

1. Source → lexer → parser → AST.
2. AST → semantic analysis → IR (intermediate representation).
3. IR → optimizations.
4. IR → code generator → assembly.
5. Assembly → assembler → object file.
6. Linker → executable.

LLVM es la infraestructura más popular para esto. Rust, Clang (C/C++), Swift, Crystal usan LLVM.

### Pros y contras

**Pros**:
- Performance máxima (sin overhead de interpretación o JIT).
- Predictable (sin deopt).
- Startup instantáneo.
- Fácil distribuir (un binario, sin runtime adicional).

**Contras**:
- Compilación lenta (segundos a minutos para grandes proyectos).
- Sin info runtime → optimizaciones más limitadas que JIT en algunos casos.
- Menos flexibilidad (no puede cambiar comportamiento dinámicamente).

Lenguajes AOT puros: C, C++, Rust, Go, Swift, Crystal.

### Híbridos AOT + runtime

- **Go**: AOT pero con runtime grande (GC, scheduler de goroutines).
- **C# / .NET**: bytecode + JIT (CLR), también soporta AOT (ReadyToRun, NativeAOT).
- **Java**: bytecode + JIT principalmente, también AOT con GraalVM Native Image.

---

## 6. Garbage collection

Lenguajes manejados (Java, Python, Go, JS) tienen **garbage collection** automático: el runtime libera memoria de objetos que ya no se usan. Sin GC tienes que manejar manual (C, C++).

### Tipos de GC

**Reference counting**: cada objeto tiene contador de referencias. Cuando llega a 0 → libera.

**Pros**: simple. Predecible (libera inmediato).
**Contras**: no maneja **cycles** (A apunta a B, B a A, ambos con refcount > 0 pero inalcanzables). Necesita recolector adicional para cycles.

CPython usa reference counting + cycle collector.

**Mark-and-sweep**: periódicamente recorre objetos accesibles desde "roots" (variables globales, stack), marca alcanzables. Después libera no marcados.

**Pros**: maneja cycles.
**Contras**: pausas durante el recorrido (stop-the-world).

**Generational GC**: la mayoría de objetos mueren jóvenes (young generation). Recolectas young frecuente (rápido, pocos objetos), old infrecuente.

Java HotSpot usa esto. Permite GCs young muy rápidos.

**Concurrent / Parallel GC**: hace el trabajo en paralelo con el programa. Reduce pausas.

**Region-based** (G1, ZGC en Java): divide heap en regions. Recolecta regions individuales.

### Trade-offs GC

GC moderno es **muy bueno** pero tiene cost:
- **Throughput overhead**: 5-20% del tiempo de CPU típicamente.
- **Latency spikes**: pausas durante GC. Optimizable pero no gratis.
- **Memory overhead**: necesita slack para que GC funcione bien (típicamente 1.5-3x el working set).

Lenguajes sin GC (C, Rust, C++):
- Sin overhead de GC.
- Pero: bugs de memoria (use-after-free, leaks).
- Rust: borrow checker garantiza safety en compile time. **Sin GC, sin bugs**.

---

## 7. Por qué Python es "lento" — análisis

Python tiene reputación de "lento". ¿Por qué?

1. **Bytecode interpretado**, no JIT. Cada operación pasa por dispatch loop.
2. **Tipado dinámico**: cada `a + b` chequea tipos en runtime, busca métodos, etc.
3. **Object overhead**: incluso `int(5)` es un objeto con header, refcount, type pointer (~28 bytes en CPython 64-bit).
4. **GIL**: limita paralelismo CPU.
5. **Calls a métodos**: cada `obj.method()` busca el método en MRO en runtime.

**¿Qué tan lento?**: Python puro típicamente 50-100x más lento que C para CPU-bound. Para I/O-bound, casi igual (el bottleneck es I/O, no CPU).

**Cómo se acelera Python en producción**:
- **NumPy / pandas**: operaciones en C optimizado + SIMD. Para arrays numéricos, casi tan rápido como C.
- **Cython**: subset de Python compilado a C. Speedups grandes.
- **PyPy**: JIT alternativo. 5-10x speedup para muchos workloads.
- **C extensions**: hot path en C, lógica en Python.
- **Profile-driven optimization**: típicamente 10% del código consume 90% del tiempo. Optimizar solo eso.

---

## 8. Cómo Java/JS son rápidos a pesar de ser dinámicos

JS es dinámico como Python. Java tipado pero con boxing y GC. Sin embargo son **rapidísimos** comparados con Python. ¿Cómo?

**JIT muy sofisticado**: V8 y HotSpot llevan décadas de optimization. Inline caches, type specialization, escape analysis, vectorización auto.

**Ejemplo**: en V8, cuando llamas `obj.x` muchas veces y `obj` siempre tiene el mismo "shape" (mismas propiedades), V8 genera código que asume ese shape y accede directo (igual que Java accede a un field). Si el shape cambia, deopta.

CPython no hace esto. Cada `obj.x` busca en `__dict__` o lookup de descriptors.

**Consecuencia**: V8 ejecuta código JS dinámico a velocidades cercanas a Java. CPython no se acerca.

**Por qué Python no tiene JIT**: razones históricas (decisión de evolución del lenguaje), backward compat (C extensions asumen layout específico), recursos del proyecto. Hay esfuerzos (PyPy, Numba, Faster CPython project) pero el default sigue siendo bytecode.

---

## 9. Compilation a WebAssembly (WASM)

**WASM** es un formato binario portable que browsers ejecutan eficientemente. Lenguajes compilan a WASM y corren en cualquier browser.

**Lenguajes que compilan bien a WASM**: C/C++ (Emscripten), Rust, Go, AssemblyScript, Zig.

**Casos de uso**:
- Ejecutar código C/C++ en browser (Photoshop web, Figma, AutoCAD).
- Performance-critical web apps (parsers, ML).
- Edge compute (Cloudflare Workers WASM, Fastly Compute@Edge).
- Plugins seguros para apps (Envoy filters, Postgres extensions con WASM).

**Trade-off**: WASM es ~50% más lento que código nativo. Pero mucho más rápido que JS para CPU-heavy work.

WASM es **el siguiente capítulo** de runtimes portables. Está creciendo rápido fuera de browsers.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

CPython runtime ejecuta tu app. Saber que:
- Cada `int` es un objeto pesado.
- async/await usa el bytecode VM eficientemente (no spawn threads).
- numpy/pandas operations son C, mucho más rápidas que loops Python puros.

### En entrevistas tecnicas

**Pregunta clásica**: "Por qué Python es más lento que Java".

Multiple razones: bytecode interpretado vs JIT, dynamic typing checks runtime, GIL, object overhead, sin shape-based optimizations.

**Pregunta sobre GC**: "Cómo elegirías GC para tu lenguaje".

Trade-offs: throughput (parallel) vs latency (concurrent) vs memory (compacting). Para apps web latency-sensitive: G1 o ZGC. Para batch: parallel.

**Pregunta avanzada**: "Diseña runtime para nuevo lenguaje".

Decisiones: AOT vs bytecode + JIT. GC vs ownership (Rust-style). Stack-based vs register-based VM. Type system static vs dynamic. Cada decisión tiene trade-offs profundos.

---

## 11. Trampas típicas

**"Python es lento siempre"**: para I/O bound, casi tan rápido como cualquiera. Para CPU con numpy/cython, puede ser igual a C.

**"JIT es siempre mejor que AOT"**: JIT tiene warmup overhead. Para CLIs y short-lived processes, AOT es mejor.

**"GC es problema solo de Java"**: Python, Ruby, JS, Go también tienen GC. Diferencias en algoritmos.

**"Sin GC siempre es más rápido"**: management manual en C tiene su overhead (free calls). Y bugs de memoria → bugs en producción.

**"WASM solo es para browser"**: cada vez más usado en server (edge compute, plugins). Su ecosistema crece.

**"Bytecode es lento"**: comparado con AOT C sí. Comparado con tree-walker es 50x más rápido.

---

## 12. Preguntas típicas de interview

**Compiler vs interpreter**: compiler traduce todo antes. Interpreter ejecuta directamente. Híbridos comunes (Python: compila bytecode + interpreta).

**JIT vs AOT**: JIT compila en runtime con info adicional. AOT antes con menos info pero startup instant.

**Por qué Python es lento**: cubierto sección 7.

**Garbage collection — algoritmos**: refcounting, mark-sweep, generational, concurrent. Trade-offs throughput vs latency.

**Stack-based vs register-based VM**: stack más simple, register más eficiente.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- 4 estrategias de ejecución (tree-walker, bytecode, JIT, AOT) con trade-offs.
- Stack-based vs register-based VMs.
- JIT: por qué puede superar a AOT (info runtime).
- Garbage collection: refcounting vs mark-sweep vs generational.
- Por qué Python es más lento que Java/JS (no JIT, dynamic typing checks).
- WASM como siguiente capítulo.

Si no puedes → relee.

---

## ¡Cluster Compilers completado! 🎉
## ¡Cluster CS_Fundamentos COMPLETO! 🎉🎉🎉

**Has completado los 9 clusters, 37 docs**:

- Tier 1 (24 docs): Networking, OS, Concurrency, System Design, Database Internals.
- Tier 2 (11 docs): Distributed Systems, Computer Architecture, Security.
- Tier 3 (2 docs): Compilers.

Total estimado: ~17,000 líneas de doc didáctico denso.

---

## Conexiones

- [[01-lexer-parser-ast]] — el frontend del compiler
- [[../02_operating_systems/02-memoria-virtual-paging]] — GC interactúa con memoria
- [[../07_computer_architecture/01-cpu-pipeline-y-registros]] — JIT genera código nativo
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Crafting Interpreters** (Robert Nystrom, gratis online) — la mejor referencia moderna. Construye 2 implementaciones: tree-walker en Java + bytecode VM en C.
- **The Garbage Collection Handbook** (Jones, Hosking, Moss) — la biblia GC.
- **JIT Compilation in PyPy** (papers) — interesante.
- **V8 blog** (v8.dev/blog) — internals del JIT más usado.
- **JavaScript engines under the hood** (varios talks YouTube) — nivel técnico medio.
- **WebAssembly spec** (webassembly.org) — para entender WASM.
