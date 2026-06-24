---
title: Historia de C
date: 2026-06-17
tags: [programacion/c, historia, cultura]
type: nota
status: permanente
source: claude-code
aliases: [historia de c, historia c, historia del lenguaje c]
---


# Historia de C

> *"C is quirky, flawed, and an enormous success."*
> — Dennis Ritchie

Pocos inventos han cambiado tanto el mundo siendo tan invisibles. No tiene mascota famosa, ni guerras de licencias épicas, ni un creador que enseñe el dedo corazón en una charla. Y sin embargo, casi todo lo que tocas a diario —el teléfono, el navegador, el router, el coche, el cajero, la sonda que fotografía Marte— tiene, en algún punto de sus cimientos, código escrito en C. Es el lenguaje sobre el que se construyó el suelo que pisan los demás lenguajes. Esta es su historia: la de una herramienta nacida casi por pereza —para no tener que reescribir un sistema operativo una y otra vez— que terminó siendo el idioma común de la informática.

---

## Parte I — La prehistoria: CPL, BCPL y B (1963–1971)

La historia de C empieza, como la de [[Linux/historia-de-linux|Linux]], en los **Bell Labs** de AT&T, y está entrelazada con Unix desde el primer día. Pero antes de C hubo una pequeña genealogía de lenguajes.

En los primeros 60, en Inglaterra, se diseñó **CPL** (*Combined Programming Language*), un lenguaje ambicioso, potente y tan complejo que casi nadie llegó a implementarlo del todo. Como reacción, **Martin Richards** creó en 1967 una versión destilada y portable: **BCPL** (*Basic CPL*), pensada para escribir compiladores. BCPL era *typeless*: solo conocía una cosa, la "palabra" de máquina.

Cuando **Ken Thompson** empezó a construir Unix en una **PDP-7** rescatada (ver la historia de Unix en [[Linux/historia-de-linux|Historia de Linux]]), quiso un lenguaje de alto nivel para no programar todo en ensamblador. Tomó BCPL, lo recortó hasta que cupiera en la minúscula memoria de la PDP-7, y lo llamó **B** (1969-1970) — probablemente por BCPL, quizá por otras razones que se han perdido en la leyenda. B heredó el problema de BCPL: seguía siendo *typeless*, todo eran palabras. Eso funcionaba en la PDP-7, pero cuando Unix se mudó a la nueva **PDP-11**, que manejaba bytes y distintos tamaños de datos, B se quedó corto: no sabía distinguir un carácter de un entero de un número con decimales.

---

## Parte II — Nace C: el lenguaje para escribir un sistema operativo (1972–1973)

Entre 1971 y 1973, **Dennis Ritchie** transformó B para arreglar precisamente eso. Le añadió un **sistema de tipos** (`char`, `int`, `float`, `double`), las **estructuras** (`struct`) y, sobre todo, una forma de hablar de la memoria que encajaba con cómo funcionan las máquinas de verdad. El lenguaje resultante, sucesor de B, se llamó con la siguiente letra del alfabeto: **C**.

El momento decisivo llegó en **1973**: Thompson y Ritchie **reescribieron el núcleo de Unix en C**. Hasta entonces, un sistema operativo era código atado a una máquina concreta; cambiar de hardware significaba reescribirlo casi entero en otro ensamblador. Con Unix escrito en C, bastaba con **escribir un compilador de C para la nueva máquina y recompilar**. Por primera vez, un sistema operativo serio era *portable*. Esa idea —software que viaja entre arquitecturas— es uno de los pilares invisibles de toda la informática moderna, e hizo que tanto Unix como C se extendieran juntos como el fuego.

> **Curiosidad — "portable assembly".** A C se le llama a menudo "ensamblador portable": te da casi el control de bajo nivel del ensamblador (punteros, acceso directo a memoria, operaciones sobre bits) pero con una sintaxis legible que funciona en cualquier máquina. Esa doble naturaleza —cercano al metal *y* portable— es justo lo que lo hizo imbatible para sistemas operativos, drivers y firmware. Y es la razón de que, medio siglo después, sigas aprendiéndolo: entender C es entender cómo piensa la máquina.

---

## Parte III — K&R: el libro que enseñó C al mundo (1978)

En **1978**, **Brian Kernighan** y **Dennis Ritchie** publicaron *The C Programming Language*. El libro —universalmente conocido como **"K&R"** por las iniciales de sus autores— era tan claro, tan breve y tan elegante que se convirtió a la vez en el **manual de referencia** y en la **definición de facto** del lenguaje durante más de una década (esa versión pre-estándar se conoce hoy como **"K&R C"**). Está considerado uno de los mejores libros técnicos jamás escritos: cabe en una mano y enseña un lenguaje entero.

De ese libro salió, además, el ritual de iniciación de todo programador del planeta:

```c
#include <stdio.h>

int main(void) {
    printf("hello, world\n");
    return 0;
}
```

> **Curiosidad — el "hello, world".** El programa que imprime *"hello, world"* como primer ejemplo de un lenguaje es una tradición que arranca aquí (apareció en un tutorial interno de Kernighan en Bell Labs hacia 1974 y se consagró en K&R en 1978). Desde entonces, prácticamente todos los lenguajes de programación de la historia empiezan su documentación con un "hola mundo", homenajeando sin saberlo a un manual de C de los años 70.

C se expandió pegado a Unix: AT&T repartía Unix casi gratis a las universidades con el código fuente, y con él iba C. Una generación entera de informáticos aprendió a programar sobre máquinas Unix, en C. Cuando esos estudiantes salieron a la industria, llevaron C con ellos a todas partes.

---

## Parte IV — La estandarización: de ANSI C a C23

Conforme C se extendía, surgió el problema de siempre: cada compilador añadía sus extensiones y empezaban a aparecer dialectos incompatibles (la misma "balcanización" que sufrió Unix). Hacía falta un estándar.

- **ANSI C (C89) / ISO C (C90).** El comité **ANSI X3J11** se formó en 1983 y publicó el estándar en **1989**; ISO lo adoptó en **1990**. Es la versión que unificó el lenguaje: introdujo los **prototipos de funciones** (declarar tipos de los argumentos), `void`, `const`, una **biblioteca estándar** formal… La 2.ª edición de K&R (1988) ya recogía este C "moderno".
- **C99 (1999).** La gran modernización: comentarios `//`, `long long`, `_Bool`/`<stdbool.h>`, `inline`, arrays de longitud variable (VLA), inicializadores designados, `snprintf`, números complejos, declarar variables en mitad del código…
- **C11 (2011).** Hilos (`<threads.h>`) y operaciones atómicas (concurrencia en el propio lenguaje), `_Generic`, `static_assert`, structs/unions anónimas; y se retiró la peligrosísima `gets()`.
- **C17 / C18 (2018).** Una versión de mantenimiento: aclara ambigüedades y corrige defectos del C11, **sin funciones nuevas**.
- **C23 (2024).** Modernización profunda: `true`/`false`/`bool` y `nullptr` como palabras clave, `constexpr`, `typeof`, literales binarios (`0b1010`), separador de dígitos (`1'000'000`), `#embed` (incrustar ficheros), atributos ``, enteros de anchura arbitraria (`_BitInt`)… y la eliminación definitiva de las viejas definiciones de funciones al estilo K&R.

> **Curiosidad — C cambia despacio a propósito.** Entre C89 y C23 hay 34 años y solo cinco revisiones. Esa lentitud no es pereza: es una virtud. Código C escrito en los 90 sigue compilando hoy, y un sistema crítico (un avión, un marcapasos, un kernel) necesita justo eso —estabilidad de décadas— más que features de moda. C envejece como las matemáticas, no como un framework de JavaScript.

---

## Parte V — La familia C: el idioma que moldeó a casi todos

Mira este fragmento: `for (int i = 0; i < n; i++) { ... }`. Esas llaves, ese `for`, ese `i++`, ese `==`… los reconoces en **C++, Java, C#, JavaScript, PHP, Go, Rust, Swift, Objective-C**… No es casualidad: todos beben de la sintaxis de C. Aprender C es aprender, de paso, la gramática base de medio mundo de la programación.

Pero la influencia va más hondo que la sintaxis. C definió el **ABI** (la convención de bajo nivel sobre cómo se llaman las funciones y se pasan datos en memoria) que se ha vuelto el **idioma común entre lenguajes**: cuando Python, Ruby, Rust o cualquier otro quieren hablar con código de otro lenguaje o con el sistema operativo, lo hacen a través de la "interfaz C". C no es solo un lenguaje; es el **punto de encuentro** de todos los demás.

> **Curiosidad — C++ empezó siendo C.** En 1979, también en Bell Labs, **Bjarne Stroustrup** empezó a añadirle clases a C: lo llamó *"C with Classes"*, y en 1983 pasó a llamarse **C++** (el `++` es el operador de incremento de C: "C mejorado"). Sus primeras versiones ni siquiera compilaban a binario directamente: un programa llamado *cfront* traducía C++ a C, y luego se compilaba ese C. El hijo nació hablando el idioma del padre.

---

## Parte VI — Cosas increíbles construidas con C

Si tuvieras que señalar el software que sostiene el mundo, casi todo estaría aquí. Una muestra:

| Categoría | Construido en C |
|---|---|
| **Sistemas operativos** | Unix, el **kernel de Linux** (~27 millones de líneas), el núcleo de **Windows (NT)**, el de **macOS/iOS (XNU)**, los BSD, Android (kernel) |
| **Otros lenguajes** | **CPython** (el intérprete de Python que usas), Ruby, PHP, Perl, Lua, Bash, el primer C++ (vía *cfront*) |
| **Bases de datos** | **SQLite** (la BD más desplegada del planeta: está en cada móvil y cada navegador), **PostgreSQL**, MySQL, **Redis** |
| **Infraestructura de internet** | **nginx**, Apache, **OpenSSL**, **curl**, OpenSSH, **Git** (sí, Git está escrito en C), **FFmpeg** (casi todo el vídeo del mundo) |
| **Espacio y embebido** | Software de vuelo de los **rovers de Marte** (Curiosity, Perseverance), aviónica, automoción, **Arduino** y prácticamente todo microcontrolador |
| **Videojuegos** | **DOOM** (1993) y **Quake** (1996) de id Software, motores que definieron una industria |

> **Curiosidad — C en Marte y reglas para no morir.** Como un fallo en C puede tener consecuencias catastróficas (un puntero mal usado puede estrellar literalmente una sonda), en entornos críticos se programa con cinturones de seguridad: el estándar **MISRA C** (1998) para coches, y las **"Power of Ten" rules** del JPL de la NASA (2006) — un decálogo de C ultra-restringido (sin recursión, sin `malloc` dinámico, sin bucles sin límite fijo…) para que el software que pilota una nave a millones de kilómetros no falle. El mismo lenguaje con el que haces tu "hola mundo" lleva décadas conduciendo robots por otro planeta.

---

## Parte VII — C hoy: vivo, imprescindible… y bajo presión

Medio siglo después, C sigue siendo uno de los lenguajes **más usados del mundo** (pelea cada año por lo más alto de rankings como TIOBE) y el **rey indiscutible** de los sistemas operativos, los drivers y el mundo embebido —tu terreno si vienes del hardware—. No es nostalgia: es que cuando necesitas hablar con el metal, control total y previsibilidad, no hay mucho más.

Pero C tiene un talón de Aquiles famoso: **la seguridad de memoria**. El control absoluto que te da (punteros, memoria a mano) es también su mayor peligro: un *buffer overflow* o un puntero colgante son la causa de una porción enorme de las vulnerabilidades de seguridad de la historia. Por eso desde ~2022 hay un empuje fuerte hacia lenguajes "memory-safe" como **Rust**: la propia Casa Blanca (informe de la ONCD, 2024) y agencias de ciberseguridad recomiendan migrar el software crítico nuevo, y el **kernel de Linux acepta Rust** junto a C desde la versión 6.1 (2022).

¿Significa eso que C se muere? No. Hay tanto C en el mundo —y tan irremplazable en lo más bajo— que seguirá ahí durante décadas. Pero por primera vez tiene un rival serio para su nicho. Saber C te da, además, justo lo que necesitas para entender *por qué* existe Rust y qué problema resuelve.

---

## Parte VIII — Dennis Ritchie, el genio discreto

Si Linux tiene a un Torvalds carismático y combativo, C tiene lo contrario: **Dennis MacAlistair Ritchie** (1941–2011) fue un ingeniero callado, modesto y alérgico a los focos, que cambió el mundo dos veces —con C y con Unix (codiseñado con Thompson)— y apenas dio entrevistas.

- En **1983** recibió, junto a Ken Thompson, el **Premio Turing** (el "Nobel de la informática") por Unix.
- En **1998** recibió la **National Medal of Technology** de manos del presidente de EE. UU.

> **Curiosidad — el genio a la sombra.** Ritchie murió el **12 de octubre de 2011**, apenas una semana después de **Steve Jobs**. La muerte de Jobs llenó portadas en todo el planeta; la de Ritchie pasó casi inadvertida fuera del mundo técnico. Y sin embargo, como señalaron muchos ingenieros entonces, *buena parte del imperio de Jobs corría sobre los cimientos que Ritchie había puesto*: el kernel de macOS y iOS desciende de Unix y está escrito en C. El hombre cuyo trabajo sostenía el mundo se fue casi sin que el mundo se enterara.

---

## Parte IX — Curiosidades extra

> **Comportamiento indefinido y "demonios nasales".** C tiene un concepto temido: el *undefined behavior* (UB). Si haces algo que el estándar no define (leer fuera de un array, desbordar un entero con signo…), el compilador puede hacer **literalmente cualquier cosa**. En 1992, en un grupo de noticias, alguien bromeó con que el estándar permitiría "hacer que salieran demonios por tu nariz". Desde entonces, *"nasal demons"* es la forma cariñosa con que los programadores de C se refieren al caos del UB.

> **El concurso de código más feo del mundo.** Desde **1984** existe el **IOCCC** (*International Obfuscated C Code Contest*): un concurso a ver quién escribe el programa en C más ilegible, retorcido y a la vez ingenioso. Hay ganadores que dibujan, que son a la vez código válido y una imagen, o que se ejecutan igual del derecho que del revés. Es a la vez una broma y un homenaje a lo expresivo (y peligroso) que es el lenguaje.

> **"Reflections on Trusting Trust".** En su discurso del Turing de 1984, **Ken Thompson** describió un ataque legendario: un compilador de C modificado para que, al compilar el programa de *login*, le inyectara en secreto una puerta trasera… y que además se reinyectara a sí mismo al recompilar el propio compilador, sin dejar rastro en el código fuente. La conclusión —"no puedes confiar del todo en código que no escribiste tú entero, hasta el compilador"— sigue siendo una de las ideas más profundas (e inquietantes) de la seguridad informática.

> **El `goto fail` que rompió la seguridad de Apple.** En 2014, un fallo en el código C de seguridad (SSL/TLS) de Apple —una simple línea `goto fail;` duplicada por error— dejó vulnerables a millones de dispositivos. Una lección perfecta de por qué en C cada llave y cada línea importan, y de por qué `-Wall` (avisos del compilador) es tu amigo.

> **Por qué se llama C.** No hay misterio profundo: viene **después de B** (el lenguaje de Thompson), que a su vez viene de **BCPL**. Hubo quien bromeó con que el siguiente debería llamarse "D" o "P" (la siguiente letra de BCPL); al final, el sucesor espiritual con clases se llamó **C++**, y sí existe un lenguaje moderno llamado **D**.

---

## Tabla de hitos cronológicos

| Año | Evento |
|-----|--------|
| 1967 | Martin Richards crea **BCPL**, antecesor portable y *typeless*. |
| 1969-70 | Ken Thompson crea **B** para la PDP-7 de Unix, recortando BCPL. |
| **1972** | **Dennis Ritchie transforma B en C** (añade tipos y structs) en Bell Labs. |
| **1973** | **Unix se reescribe en C** — un SO portable por primera vez. |
| 1978 | Kernighan & Ritchie publican **K&R**; se consagra el *"hello, world"*. |
| 1979 | Stroustrup empieza *"C with Classes"* (futuro **C++**) en Bell Labs. |
| 1983 | Ritchie y Thompson reciben el **Premio Turing**. Se forma el comité ANSI C. |
| 1984 | Thompson: *"Reflections on Trusting Trust"*. Nace el **IOCCC**. |
| **1989-90** | **ANSI C (C89) / ISO C (C90)**: el estándar que unificó el lenguaje. |
| 1998 | MISRA C (C seguro para automoción). Ritchie: National Medal of Technology. |
| **1999** | **C99**: `//`, `long long`, `bool`, VLAs, complejos… |
| 2011 | **C11**: hilos, atómicos, `_Generic`. Muere Dennis Ritchie (12 oct). |
| 2018 | **C17/C18**: versión de correcciones, sin features nuevas. |
| 2022 | El **kernel de Linux** empieza a aceptar **Rust** junto a C (v6.1). |
| **2024** | **C23**: `nullptr`, `constexpr`, `typeof`, literales binarios, `#embed`… |

---

## Conexiones

- [[Curso_C/00_README|Curso de C]] — el itinerario práctico
- [[Curso_C/modelo/00-que-es-c]] — qué es C y cómo funciona el compilador
- [[Linux/historia-de-linux|Historia de Linux]] — la historia hermana (C y Unix nacieron juntos)
- [[Curso_Python/00_README|Curso de Python]] — el puente: C explícito → Python cómodo
- [[MOC_Programacion]] · [[MOC_CS_Fundamentos]]

---

*Documento narrativo elaborado con Claude Code (2026-06-17). Fechas y citas contrastables con: los escritos de Dennis Ritchie sobre el desarrollo de C (*"The Development of the C Language"*), el comité ISO/IEC JTC1/SC22/WG14 (estándares C89–C23), los discursos del Premio Turing de Ritchie y Thompson, y documentación pública sobre MISRA C y las "Power of Ten" del JPL. Las citas en inglés son textuales del original.*
