---
title: Vulnerabilidades y explotacion (conceptual)
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, programacion/sistemas, ciberseguridad/vulnerabilidades, ciberseguridad/explotacion]
type: nota
status: en-progreso
source: claude-code
aliases: [vulnerabilidades, CVE, buffer overflow]
---

# 🔓 Vulnerabilidades y explotacion (conceptual)

## Por que importa este tema

Toda la ciberseguridad defensiva gira alrededor de una pregunta simple: **¿por que falla el software, y como lo explotan?** Sin entender la raiz del problema, las defensas son rituales ciegos — parcheas sin saber que parcheas, y configuras sin saber que proteges.

Este documento cubre el modelo conceptual: que es una vulnerabilidad, como se clasifica, las familias de errores mas comunes (especialmente los de memoria, que han dominado la historia del hacking), y el ciclo responsable de descubrimiento a parche. Todo con enfoque defensivo y etico.

---

## 1. Que es una vulnerabilidad

Una **vulnerabilidad** es un defecto en un sistema (codigo, configuracion, diseno o proceso humano) que permite a un actor realizar algo que no deberia estar permitido — escalar privilegios, ejecutar codigo arbitrario, acceder a datos ajenos, etc.

La distincion clave:

| Termino | Definicion |
|---|---|
| **Vulnerabilidad** | El defecto en si (el agujero) |
| **Exploit** | El mecanismo/codigo que aprovecha el defecto |
| **Payload** | Lo que se ejecuta una vez se ha explotado (shell, ransomware, etc.) |
| **Amenaza** | Actor o evento capaz de explotar la vulnerabilidad |
| **Riesgo** | Probabilidad x impacto potencial |

> Analogia de hardware: la vulnerabilidad es un pin de entrada sin proteccion de ESD en un PCB; el exploit es el pico de tension que lo quema; el payload es el comportamiento anormal resultante.

---

## 2. CVE y CVSS — el sistema de clasificacion

### CVE (Common Vulnerabilities and Exposures)

El **CVE** es un identificador unico estandar para vulnerabilidades conocidas publicamente. Lo gestiona MITRE y lo financia el gobierno de EE.UU.

Formato: `CVE-AÑO-NUMERO`
Ejemplo: `CVE-2021-44228` — Log4Shell (vulnerabilidad critica en la libreria Log4j de Java, 2021)

Cuando lees un CVE tienes: descripcion del defecto, software afectado, version vulnerable, y referencias a parches.

### CVSS (Common Vulnerability Scoring System)

El **CVSS** es la formula numerica que convierte una vulnerabilidad en una puntuacion de severidad del 0 al 10. La version actual es CVSSv3.1.

Factores que influyen en la puntuacion:

| Dimension | Preguntas que responde |
|---|---|
| **Vector de ataque** | ¿Se necesita acceso fisico, red local, o internet? |
| **Complejidad** | ¿Es facil de explotar o requiere condiciones especiales? |
| **Privilegios requeridos** | ¿El atacante ya necesita estar autenticado? |
| **Interaccion del usuario** | ¿Hace falta que alguien haga click? |
| **Confidencialidad / Integridad / Disponibilidad** | ¿Que dimensiones del sistema se ven comprometidas? |

Rangos CVSS:

```
0.0       → Sin severidad
0.1 - 3.9 → Baja
4.0 - 6.9 → Media
7.0 - 8.9 → Alta
9.0 - 10.0→ Critica
```

Log4Shell tenia CVSS 10.0: explotable desde internet, sin autenticacion, sin interaccion del usuario, con impacto total en confidencialidad/integridad/disponibilidad.

> Practica defensiva: en tu flujo DevSecOps ([[09-devsecops-y-appsec]]), integra un scanner de dependencias (Trivy, Dependabot, Snyk) que muestre CVEs y sus puntuaciones. Prioriza los 9+, investiga los 7+.

---

## 3. Clases comunes de vulnerabilidades

### 3.1 Errores de seguridad de memoria (Memory Safety)

La mayor familia historica de vulnerabilidades criticas viene de lenguajes que permiten al programador gestionar la memoria directamente (C, C++) sin guardianes automaticos. Si el programador comete un error, el atacante puede aprovecharlo.

#### Buffer Overflow (desbordamiento de buffer)

**Concepto fundamental:**

Un buffer es una region de memoria de tamano fijo reservada para datos. Un buffer overflow ocurre cuando se escribe mas datos de los que caben, sobreescribiendo memoria adyacente.

```
Buffer legitimo (capacidad: 8 bytes):
[H][o][l][a][ ][ ][ ][ ]  ← correcto

Input malicioso (12 bytes):
[A][A][A][A][A][A][A][A][X][X][X][X]
                          ↑↑↑↑ se sobreescriben datos fuera del buffer
```

En la pila de ejecucion (stack), junto al buffer suele estar la **direccion de retorno** de la funcion — la instruccion a la que el programa debe volver cuando termina. Si un atacante sobreescribe esa direccion con una que el controla, puede redirigir la ejecucion a codigo malicioso.

Esto es la base conceptual de los ataques de **stack smashing** que dominaron los anos 90-2000.

**Mitigaciones modernas:**
- `Stack Canaries`: valor sentinela entre el buffer y la direccion de retorno; si cambia, el programa aborta.
- `ASLR` (Address Space Layout Randomization): aleatorizacion de donde se carga la memoria en cada ejecucion.
- `NX/DEP` (No-Execute / Data Execution Prevention): marca regiones de memoria como no ejecutables.
- Compiladores modernos con flags de seguridad (`-fstack-protector`, `-D_FORTIFY_SOURCE`).
- Usar funciones seguras: `strncpy` en lugar de `strcpy`, `snprintf` en lugar de `sprintf`.

#### Use-After-Free (UAF)

**Concepto:** se libera un bloque de memoria (`free()`) pero el programa sigue teniendo un puntero a esa region y lo usa despues. Si un atacante logra que esa memoria sea reasignada con datos que el controla antes de que se use, puede manipular el comportamiento del programa.

```
ptr = malloc(64);   // reserva memoria
free(ptr);          // libera memoria
// ... el atacante hace que esa region se reasigne con sus datos ...
ptr->funcion();     // usa el puntero viejo → ejecuta codigo del atacante
```

Es mas sutil que el buffer overflow y sigue siendo una fuente frecuente de vulnerabilidades criticas en navegadores, kernels y software C/C++.

**Mitigacion:** zeroing de punteros despues de liberar (`ptr = NULL`), allocators con deteccion de UAF (AddressSanitizer en desarrollo), lenguajes con garbage collection o ownership estatico.

#### Integer Overflow

Cuando un calculo con enteros supera el valor maximo representable y "da la vuelta" a un valor pequeno. Si ese entero se usa para calcular el tamano de un buffer, se reserva menos memoria de la necesaria y el siguiente write produce un overflow.

```c
uint8_t tamanio = 200 + 100;  // 300 > 255 → resultado: 44 (overflow)
char *buf = malloc(tamanio);   // se reservan solo 44 bytes
memcpy(buf, input, 300);       // se escriben 300 → overflow
```

### 3.2 RCE — Remote Code Execution

**Remote Code Execution** es la clase de vulnerabilidad mas critica: permite a un atacante ejecutar codigo arbitrario en el sistema victima, de forma remota, generalmente sin autenticacion previa.

No es un mecanismo especifico sino una consecuencia. Puede llegar por:
- Buffer overflow que redirige ejecucion
- Deserializacion insegura (el sistema ejecuta codigo embebido en datos serializados)
- Inyeccion de comandos del sistema operativo (ver [[04-seguridad-web-owasp]])
- Vulnerabilidades en parsers (imagenes, documentos, protocoles de red)

Un RCE con CVSS alto es practicamente siempre un parche de emergencia.

### 3.3 Race Conditions (condiciones de carrera)

**Concepto:** dos o mas procesos/hilos acceden a un recurso compartido de forma concurrente, y el resultado depende del orden de ejecucion no determinista. Si un atacante puede influir en ese orden, puede explotar el intervalo entre dos operaciones.

El caso clasico en seguridad es el **TOCTOU** (Time Of Check to Time Of Use):

```
1. El programa comprueba: "¿tiene este usuario permiso para leer /etc/shadow?" → NO
   [ventana de tiempo]
2. Atacante reemplaza el archivo con un enlace simbolico a /etc/shadow
3. El programa abre el archivo (pensando que es inofensivo) → lee /etc/shadow
```

Tambien son criticas en criptografia: si la generacion de numeros aleatorios tiene una race condition, los secretos generados pueden ser predecibles.

**Mitigacion:** locks/mutexes, operaciones atomicas, evitar el patron check-then-act con recursos del sistema de archivos.

---

## 4. Por que los lenguajes memory-safe ayudan

Lenguajes como **Rust** y **Go** (y en menor medida Java, Python, etc.) eliminan o reducen drasticamente las vulnerabilidades de memoria:

| Propiedad | C/C++ | Rust | Go / Java / Python |
|---|---|---|---|
| Gestion de memoria | Manual (`malloc`/`free`) | Ownership estatico en compilacion | Garbage collector en runtime |
| Buffer overflow | Posible | Imposible por diseno | Imposible (GC gestiona limites) |
| Use-after-free | Posible | Imposible (el compilador lo rechaza) | Imposible (GC retiene el objeto) |
| Null pointer | Posible | Imposible (`Option<T>`) | Posible (Java), imposible en lenguajes modernos |
| Rendimiento | Maximo | Comparable a C | Menor que C (overhead GC/runtime) |

**El contexto:** la NSA, CISA y otros organismos han publicado guias recomendando migrar software critico a lenguajes memory-safe. Rust es la apuesta mas fuerte para sistemas de bajo nivel (kernels, drivers, firmware) porque no sacrifica rendimiento.

Esto no significa que Rust o Go sean inmunes a vulnerabilidades — logica de negocio erronea, criptografia mal implementada, o errores en codigo `unsafe` de Rust siguen siendo posibles — pero eliminan toda una clase de ataques historicamente destructiva.

---

## 5. El ciclo: descubrimiento → reporte → parche

### 5.1 Descubrimiento

Las vulnerabilidades se descubren por:
- **Investigadores de seguridad** (empresas especializadas, academicos, bug bounty hunters)
- **Auditores** contratados por el propio vendedor
- **Fuzzing automatizado**: se bombardea el software con inputs aleatorios/mutados buscando crashes
- **Analisis estatico de codigo** (SAST): herramientas que analizan el codigo sin ejecutarlo
- **Actores maliciosos** que las encuentran antes y las usan en silencio

### 5.2 Responsible / Coordinated Disclosure

Cuando un investigador encuentra una vulnerabilidad tiene una decision etica y legal importante. El estandar de la industria es la **divulgacion coordinada** (coordinated disclosure):

```
Investigador encuentra vuln
        ↓
Notifica PRIVADAMENTE al vendedor/mantenedor
        ↓
Se acuerda un plazo (tipicamente 90 dias — estandar de Google Project Zero)
        ↓
El vendedor prepara y publica el parche
        ↓
El investigador publica los detalles tecnicos (CVE se hace publico)
```

Por que 90 dias: es suficiente para que un vendedor diligente prepare un parche; si se pasa del plazo sin parche, el investigador puede publicar de todas formas (full disclosure) para presionar y para que los usuarios tomen medidas de mitigacion.

**Alternativas**:
- **Full disclosure inmediata**: publicar todo sin aviso previo. Etico solo en casos extremos (el vendedor ya sabe y no actua).
- **No disclosure / venta a brokers**: ilegal y no etico en la mayoria de jurisdicciones.

### 5.3 El parche y su ciclo de vida

```
CVE publicado
    ↓
Vendedor lanza parche (advisory + version corregida)
    ↓
Administradores aplican el parche (aqui suele haber retraso → ventana de exposicion)
    ↓
La vulnerabilidad deja de ser explotable en sistemas parcheados
```

La ventana entre publicacion del CVE y aplicacion del parche en produccion es el momento de mayor riesgo: el exploit es publico, pero muchos sistemas siguen vulnerables.

---

## 6. Zero-Days (0-days)

Un **0-day** (zero day) es una vulnerabilidad para la que no existe parche en el momento en que se usa o se conoce publicamente. El termino viene de "cero dias para prepararse".

```
Investigador/Atacante encuentra vuln
        ↓
No lo reporta → lo usa en secreto o lo vende
        ↓
El vendedor tiene 0 dias de adelanto
        ↓
Cuando se descubre el ataque, la vuln ya se habia usado ("in the wild")
        ↓
Ahora el vendedor corre a parchear (y el CVE se publica como "exploited in the wild")
```

Los 0-days tienen un mercado opaco: gobiernos, agencias de inteligencia, y cibercriminales pagan cantidades enormes (de decenas de miles a millones de dolares) por exploits funcionales de 0-days en software ampliamente usado (iOS, Chrome, Windows).

**Para la defensa**: no puedes parchear lo que no existe. Las defensas contra 0-days se centran en:
- **Reducir la superficie de ataque** (menos software, menos puertos abiertos, menos permisos)
- **Segmentacion de red** para limitar el movimiento lateral si algo se compromete
- **EDR** (Endpoint Detection and Response) para detectar comportamiento anomalo aunque no se conozca el exploit
- **Principio de minimo privilegio**: aunque el atacante explote algo, que no pueda hacer mucho con ello

---

## 7. Errores comunes (perspectiva defensiva)

- **No parchear rapido**: tener un proceso de patch management con SLAs por severidad CVSS (ej: criticos en 24-48h, altos en 7 dias).
- **Dependencias olvidadas**: el codigo propio puede estar bien pero una libreria de terceros tiene un CVE sin parchear. Automatiza el escaneo.
- **Confiar en el input del usuario**: la mayoria de las clases de vulnerabilidades (buffer overflow, inyecciones, UAF por logica de app) tienen como causa raiz no validar ni sanitizar la entrada.
- **Seguridad por oscuridad**: no publicar el codigo fuente no protege contra vulnerabilidades; los binarios se pueden analizar (reverse engineering).
- **No tener un proceso de disclosure**: si alguien encuentra una vuln en tu proyecto y no sabe a quien reportarla, puede optar por la full disclosure inmediata. Ten un `SECURITY.md` con un email de contacto.

---

## 8. Aplicalo / Practica

### CTFs y laboratorios (entorno controlado, legal)

- **Protostar / Exploit.education**: maquinas virtuales con ejercicios de buffer overflow progresivos desde cero. Ideal para entender la mecanica real.
- **pwn.college**: curso gratuito universitario con desafios de explotacion de binarios. Muy estructurado.
- **HackTheBox / TryHackMe**: incluyen maquinas con CVEs reales (simuladas) para practicar identificacion y explotacion etica.
- **CTFtime.org**: calendario de CTFs. Los de categoria "pwn" son los de explotacion de binarios.

> Nota legal y etica: practica UNICAMENTE en sistemas propios, maquinas virtuales, o plataformas CTF diseñadas para ello. Explotar sistemas sin autorizacion explicita es un delito en practicamente todas las jurisdicciones (Espana: art. 197 CP, Computer Fraud and Abuse Act en EE.UU., etc.). Ver [[01-fundamentos-y-mentalidad]].

### En tus propios proyectos

- Activa **Dependabot** o **Renovate** en tus repos de GitHub/GitLab para CVEs automaticos en dependencias.
- En el proyecto de producto: escanea la imagen Docker con `trivy image <nombre>` y revisa los CVEs de las dependencias de Python y Node.
- Configura un `SECURITY.md` en tus repos publicos con instrucciones de reporte responsable.
- Compila tu codigo C/C++ (si aplica) con `-fstack-protector-strong -D_FORTIFY_SOURCE=2`.

### Lectura de CVEs como habito

Subscribete al feed de CVEs relevantes para tu stack. Para Python: <https://pypi.org/security/>. Para Node: `npm audit`. Para Docker images: Trivy o Docker Scout.

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[02-criptografia]]
- [[03-seguridad-de-redes]]
- [[04-seguridad-web-owasp]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
- [[MOC_Desarrollo_Software]]
- [[MOC_CS_Fundamentos]]
