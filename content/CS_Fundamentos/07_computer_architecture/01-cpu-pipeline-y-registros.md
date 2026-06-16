# 01 — CPU pipeline y registros

> 📚 **Doc 1 del cluster Computer Architecture**. Por qué tu código va más rápido o lento de lo que esperas. Lo que pasa "debajo" del lenguaje de programación.
> 🔥 **Frecuencia interview**: aparece en preguntas de performance avanzadas. Para roles low-level / systems / hardware (donde perfiles de hardware/IoT encaja) es crítico.
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Por qué entender la CPU si programas en Python

A primera vista, "soy programador de aplicaciones, no necesito esto". En realidad, entender la CPU te ayuda en:

1. **Performance debugging**: por qué un loop que parece igual al de al lado va 10x más lento.
2. **Lectura de logs de profiling**: cycles, branch misses, cache misses son la moneda real.
3. **Decisiones de diseño**: por qué SIMD/vectorización ayuda, por qué NumPy es 100x más rápido que loops Python.
4. **Para tu perfil HW+SW** (técnico + IoT): trabajas con microcontroladores donde estos conceptos son visibles directamente.
5. **En entrevistas tecnicas**: roles de infraestructura, ML systems, gaming, embedded esperan que sepas esto.

No necesitas escribir ensamblador. Sí necesitas el modelo mental.

---

## 2. La CPU desde 30,000 pies

Una CPU moderna ejecuta el ciclo **fetch-decode-execute**:

1. **Fetch**: leer la siguiente instrucción de memoria (señalada por el Program Counter).
2. **Decode**: interpretar qué hace (sumar, mover, saltar...).
3. **Execute**: hacer la operación, posiblemente modificando registros o memoria.
4. Repetir.

Una instrucción típica como `ADD r1, r2, r3` significa "suma el valor de los registros r2 y r3, guarda en r1". Tarda un puñado de **ciclos de CPU** (1 ciclo = ~0.3ns en una CPU a 3GHz).

Ahora, si la CPU ejecutara una instrucción a la vez, sería lentísimo. La realidad es mucho más sofisticada.

---

## 3. Registros — la memoria más rápida

Los **registros** son la memoria DENTRO del chip. Acceso instantáneo (1 ciclo). Hay pocos (16-32 típicamente en x86-64).

Cuando programas en C `int x = 5`, esa variable termina en un registro o en stack memoria, según el compilador decida. Cuando haces `x + y`, los valores tienen que estar en registros (la CPU no opera directamente sobre memoria principal).

**La jerarquía**:
- Registros: 1 ciclo, ~32 disponibles, en el chip.
- L1 cache: 3-4 ciclos, decenas de KB.
- L2 cache: 10-20 ciclos, cientos de KB.
- L3 cache: 30-50 ciclos, decenas de MB.
- RAM: 200-400 ciclos, GBs.
- Disco SSD: ~100,000-300,000 ciclos.
- Disco HDD: ~10 millones de ciclos.

Cada nivel es 10-100x más lento que el anterior. **Por eso la localidad de datos importa tanto** (ver doc 02 sobre cache).

---

## 4. Pipelining — la primera optimización clave

Si cada instrucción tarda 5 ciclos completar (fetch + decode + execute + memory + writeback), pero la CPU procesa solo 1 a la vez, throughput = 1 instrucción cada 5 ciclos.

**Pipelining**: divide el trabajo en etapas. Mientras la instrucción A está en "execute", la B ya está en "decode" y la C en "fetch". Como una cinta de montaje.

```
Sin pipeline:
  cycle 1: A:fetch
  cycle 2: A:decode
  cycle 3: A:execute
  cycle 4: A:memory
  cycle 5: A:writeback
  cycle 6: B:fetch
  ...

Con pipeline (5 etapas):
  cycle 1: A:fetch
  cycle 2: A:decode | B:fetch
  cycle 3: A:exec   | B:decode | C:fetch
  cycle 4: A:mem    | B:exec   | C:decode | D:fetch
  cycle 5: A:wb     | B:mem    | C:exec   | D:decode | E:fetch
  ...
```

Throughput ideal: **1 instrucción por ciclo**. CPUs modernas tienen pipelines de 14-20 etapas.

### Pipeline hazards — cuando se rompe

El pipeline se interrumpe cuando hay dependencias:

- **Data hazard**: instrucción B necesita el resultado de A (que aún no acabó).
- **Control hazard**: hay un salto (branch) y el CPU no sabe qué instrucción cargar siguiente.
- **Structural hazard**: dos instrucciones quieren la misma unidad de hardware.

Cuando hay hazard, el pipeline **stallea** (espera) o **flushea** (descarta trabajo especulativo). Stalls = ciclos perdidos = código más lento.

---

## 5. Branch prediction — la magia que hace tu código rápido

**El problema**: cuando hay un `if` o un loop, la CPU no sabe a qué instrucción saltar hasta que evalúa la condición. Pero el pipeline necesita estar lleno de instrucciones siguientes. Si espera → stall.

**La solución**: **branch prediction**. La CPU adivina qué dirección va a tomar el branch (basándose en historial) y carga instrucciones especulativamente. Si acierta → todo bien. Si falla → flush del pipeline + cargar las correctas (penalización de 10-20 ciclos).

CPUs modernas aciertan **>95% de los branches**. Los algoritmos de predicción son muy sofisticados (perceptrones, two-level adaptive predictors).

### Por qué importa para tu código

```python
# Versión 1: branch impredecible (si datos random)
for x in data:
    if x > threshold:
        result.append(x)

# Versión 2: branchless (sin if)
mask = data > threshold
result = data[mask]
```

Si `data` es random, la versión 1 tiene branch miss en ~50% de iteraciones (el predictor no puede predecir random). Cada miss cuesta 10-20 ciclos. La versión 2 (numpy) es vectorizada, sin branches, mucho más rápida.

**Esto es por qué NumPy es 100x más rápido que un loop Python**: no es solo el GIL ni el overhead del intérprete. Es que las operaciones vectorizadas eliminan branches y aprovechan SIMD (siguiente sección).

---

## 6. Out-of-order execution

CPUs modernas no ejecutan instrucciones estrictamente en el orden del programa. **Si una instrucción tiene dependencia no resuelta**, la CPU **busca instrucciones futuras independientes y las ejecuta antes**.

Esto se llama **out-of-order (OoO) execution**. Mantiene la ilusión de ejecución secuencial al programador, pero internamente reordena agresivamente.

Implicación: el compilador y el hardware juntos optimizan tu código mucho más de lo que crees. Pero esto tiene **efectos visibles** en multi-threading (ver memory ordering, doc 03).

---

## 7. Superscalar — más de 1 instrucción por ciclo

Las CPUs modernas no procesan 1 instrucción por ciclo. Procesan **varias en paralelo** (4-8 instrucciones por ciclo) si son independientes.

**Tienen múltiples "ports" / unidades funcionales**:
- 2-3 ALUs (suma/resta/lógica entera).
- 1-2 unidades de multiplicación/división.
- 1-2 unidades de load/store (memoria).
- Unidades vectoriales (AVX, NEON).

Si tu código tiene paralelismo de instrucciones (ILP — Instruction-Level Parallelism), la CPU lo explota automáticamente. Si todas tus instrucciones dependen de la anterior, no.

**Optimización del compilador**: reordena código para maximizar ILP. Por ejemplo, intercala loads (que son lentos) con cálculos (que son rápidos).

---

## 8. SIMD — operaciones vectorizadas

**SIMD** (Single Instruction, Multiple Data) = una instrucción opera sobre **múltiples datos a la vez**. Usa registros más anchos.

- **SSE** (128 bits): 4 floats o 2 doubles por instrucción.
- **AVX** (256 bits): 8 floats o 4 doubles.
- **AVX-512** (512 bits): 16 floats u 8 doubles.

**Ejemplo**: sumar dos arrays de 1000 floats:
- Sin SIMD: 1000 instrucciones de ADD escalares.
- Con AVX: 125 instrucciones (8 elementos por instrucción). 8x más rápido en teoría.

**Quién usa SIMD**:
- Compiladores modernos auto-vectorizan loops simples (con `-O3`).
- Librerías numéricas (NumPy, BLAS, Intel MKL): SIMD intensivo.
- Codecs multimedia (vídeo, audio).
- Criptografía (AES tiene instrucciones SIMD dedicadas: AES-NI).
- ML inference: matrix multiplications son SIMD-friendly.

**ARM NEON** es el equivalente en ARM (móviles, Apple Silicon).

---

## 9. RISC vs CISC — los dos paradigmas

### CISC (Complex Instruction Set)

Instrucciones **muchas y complejas**. Una instrucción puede hacer "carga de memoria + suma + escritura a memoria" en una.

**Ejemplo**: x86. La instrucción `ADD [eax], ebx` lee de memoria, suma, escribe — todo en una instrucción.

**Pros (históricos)**: programas más cortos (importante cuando memoria era cara).
**Contras**: hardware más complejo, decodificador grande.

### RISC (Reduced Instruction Set)

Instrucciones **pocas y simples**. Cada una hace UNA cosa básica. Para sumar dos valores en memoria: load + load + add + store (4 instrucciones).

**Ejemplo**: ARM, RISC-V, MIPS.

**Pros**: hardware más simple, mejor para pipelining, menor consumo.
**Contras**: programas más largos.

### La realidad moderna

x86 internamente es RISC: el decodificador convierte instrucciones CISC a "micro-ops" RISC que la CPU ejecuta. Esto da lo mejor de ambos: compatibilidad CISC + ejecución RISC eficiente.

ARM ha ganado en móviles y portátiles (Apple Silicon, Snapdragon, eficiencia energética). En servidores/desktop, x86 sigue dominando pero ARM crece (AWS Graviton, Apple Mac).

---

## 10. Speculative execution y los attacks famosos

CPUs modernas ejecutan **especulativamente** muchas cosas: branches predichos, prefetch de datos, etc. Si la especulación es correcta, ganan tiempo. Si es incorrecta, descartan.

**El problema**: la especulación deja **huellas observables** en el cache, aunque "se descarte". Esto fue la base de **Meltdown y Spectre** (2018), las vulnerabilidades de hardware más famosas:

- Atacante hace que la CPU especule un acceso a memoria privilegiada.
- La especulación se descarta (correctamente).
- Pero el cache sigue con la huella.
- Atacante mide tiempos de cache para inferir el dato secreto.

**Mitigations**: parches de SO + microcode + cambios en compiladores. Coste: pérdida de performance ~5-30% según workload.

Saber que existen y por qué importa para entender debates de seguridad hardware.

---

## 11. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

A nivel app, irrelevante directo. Pero cuando uses NumPy/pandas en algún proyecto, las ganancias de SIMD son tangibles.

### En embebido (perfil HW+IoT)

Microcontroladores que usas (ESP32, etc.) son **mucho más simples** que CPUs desktop:
- Sin pipeline largo (típicamente 3-5 etapas).
- Sin branch prediction (o muy básica).
- Sin out-of-order execution.
- Sin SIMD.

**Esto los hace deterministas en timing**, lo cual es crítico para sistemas real-time. Una CPU desktop con todas esas optimizaciones tiene timing impredecible (el mismo código puede tardar distinto según predicciones).

Para mantener timing real-time en hardware más capaz: PREEMPT_RT en Linux, o usar microcontroladores dedicados.

### En entrevistas tecnicas

**Pregunta clásica**: "Por qué loop A es 10x más rápido que loop B (que parece igual)".

Respuestas posibles:
- Branch prediction (uno tiene branches predecibles, otro random).
- Cache misses (uno respeta localidad, otro no).
- SIMD (uno se vectoriza, otro no).
- ILP (uno tiene dependencias serializadas, otro no).

**Pregunta avanzada**: "Por qué NumPy es tan rápido vs Python".

Multiple razones:
1. C en lugar de bytecode interpretado.
2. Operaciones vectorizadas SIMD.
3. Sin GIL en muchos paths (libera durante operaciones).
4. Layout de memoria contiguo (cache friendly).
5. Branchless en operaciones masivas.

**Pregunta sobre trade-offs**: "Por qué x86 sigue dominando si ARM es más eficiente".

Ecosistema: software, drivers, OS optimizados durante 40 años. Cloud providers grandes (Intel, AMD) optimizan agresivo. ARM gana donde la eficiencia es crítica (móvil, Apple Silicon laptops).

---

## 12. Trampas típicas

**"La CPU ejecuta mi código exactamente como está escrito"**: NO. Reordena (OoO), especula (branch prediction), paraleliza (superscalar). El programa observable es el mismo, pero internamente es muy distinto.

**"Más MHz = más rápido"**: solo dentro de la misma arquitectura. CPUs modernas a 3GHz son MUCHO más rápidas que CPUs de hace 15 años a 3GHz por todo lo descrito aquí.

**"Optimizar siempre es bueno"**: solo lo que pesa. Profile primero (perf, py-spy, etc.). El 90% del tiempo lo pasa en el 10% del código.

**"Branchless siempre es más rápido que branches"**: si el branch es muy predecible (>95%), la versión con branch puede ser igual o más rápida. Hay que medir.

**"SIMD se aplica siempre"**: solo a operaciones vectorizables. Loops con condiciones complejas, accesos no contiguos, etc., no se vectorizan bien.

**"El compilador no puede optimizar mejor que yo"**: en 99% de casos, sí. Compiladores modernos hacen optimizaciones que un humano no puede mantener. Escribir clean code y dejar que el compilador haga su trabajo.

---

## 13. Preguntas típicas de interview

**¿Qué es pipelining?**: dividir ejecución de instrucción en etapas para procesar varias en paralelo (cinta de montaje).

**¿Qué es branch prediction y por qué importa?**: la CPU adivina qué instrucción cargar después de un branch. Acierto = pipeline lleno. Fallo = flush + 10-20 ciclos perdidos.

**Diferencia RISC vs CISC**: RISC instrucciones simples (ARM, RISC-V). CISC complejas (x86). Hoy x86 internamente RISC con decoder CISC.

**¿Qué es SIMD?**: una instrucción opera sobre múltiples datos. Base de NumPy/BLAS/codecs.

**¿Por qué NumPy es rápido?**: C compilado + SIMD + cache-friendly + sin GIL en operaciones.

**Out-of-order execution**: CPU ejecuta instrucciones en orden distinto al programa si son independientes, mantiene ilusión de orden secuencial.

**Speculative execution y Spectre**: la CPU especula. Las huellas en cache son observables. Permite ataques que extraen secretos.

---

## 14. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Ciclo fetch-decode-execute.
- Jerarquía de memoria (registros → cache → RAM → disco) y latencias relativas.
- Pipelining: por qué multiplica throughput.
- Pipeline hazards (data, control, structural).
- Branch prediction: por qué crítica para performance.
- Out-of-order y superscalar execution.
- SIMD y por qué NumPy es rápido.
- RISC vs CISC y la realidad moderna (x86 RISC interno).
- Por qué microcontroladores son más simples (real-time determinism).

Si no puedes → relee.

---

## Conexiones

- [[02-jerarquia-de-memoria-y-cache]] — la otra mitad de la historia
- [[03-coherencia-cache-multicore]] — multicore complica todo
- [[../03_concurrency/02-locks-y-mutex]] — atomic ops dependen de hardware
- [[../02_operating_systems/03-scheduling]] — scheduler interactúa con CPU
- [[../02_operating_systems/02-memoria-virtual-paging]] — TLB es parte de la jerarquía
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Computer Systems: A Programmer's Perspective (CSAPP)** Bryant & O'Hallaron — la biblia.
- **Computer Architecture: A Quantitative Approach** Hennessy & Patterson — más académico.
- **Agner Fog's optimization manuals** (agner.org/optimize/) — gratis, brutal.
- **What every programmer should know about memory** (Ulrich Drepper) — clásico.
- **Intel/AMD optimization manuals** — referencia oficial.
- **`perf stat`, `perf record`** — ver ciclos, branch misses, cache misses reales en tu código.
