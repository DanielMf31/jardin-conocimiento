---
title: Historia de Python
date: 2026-06-17
tags: [programacion/python, historia, cultura]
aliases: [historia de python, historia python, historia del lenguaje python]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/historia-de-python.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/historia-de-python.md (se regenera con gen_course.py). -->

# Historia de Python

*"Python is an experiment in how much freedom programmers need. Too much freedom and nobody can read another's code; too little and expressiveness is endangered."*
— Guido van Rossum

Si C es el suelo invisible sobre el que se construye la informática, Python es la planta que ha crecido más rápido y más alto en las últimas tres décadas. Nació como el pasatiempo navideño de un programador holandés aburrido, sin ninguna ambición de conquistar nada, y hoy es el lenguaje más usado del planeta, el idioma por defecto de la inteligencia artificial y la primera lengua de programación de millones de estudiantes. Su historia es la de una idea sencilla y casi terca —*el código se lee muchas más veces de las que se escribe, así que hagámoslo legible*— llevada hasta sus últimas consecuencias.

---

## Parte I — Antes de Python: ABC y un programador aburrido (1989)

A finales de los 80, en el **CWI** (*Centrum Wiskunde & Informatica*, el instituto nacional de matemática e informática de Ámsterdam), un programador llamado **Guido van Rossum** había trabajado en un lenguaje educativo llamado **ABC**. ABC era elegante y fácil de aprender, pero tenía defectos que lo hundieron: era cerrado, difícil de extender, no se llevaba bien con el sistema operativo. Guido se quedó con las buenas ideas (la legibilidad, la indentación como estructura) y con la espina de los errores.

En **diciembre de 1989**, durante las vacaciones de Navidad, buscando un proyecto con el que entretenerse, Guido empezó a escribir un intérprete para un lenguaje nuevo. Quería algo a medio camino entre C (potente pero tedioso) y el shell (cómodo pero limitado): un lenguaje de *scripting* legible, con el que pudiera trabajar de verdad y que corrigiera los fallos de ABC.

**Curiosidad — ¿por qué "Python"?** No es por la serpiente. Guido era fan del grupo de humor británico **Monty Python** (*Monty Python's Flying Circus*), y buscaba un nombre corto, único y un poco irreverente. La serpiente vino mucho después, como logo. Por eso, por tradición, en los ejemplos de Python las variables de relleno no se llaman `foo` y `bar`, sino **`spam` y `eggs`** (de un famoso sketch de Monty Python). El humor está en el ADN del lenguaje.

---

## Parte II — 1991: el primer Python y su filosofía

En **febrero de 1991**, Guido publicó la primera versión (la 0.9.0) en el grupo de Usenet *alt.sources*. Ya tenía las señas de identidad que lo harían reconocible:

- **La indentación define los bloques** (nada de llaves `{ }` ni `begin/end`): el código *tiene* que estar bien sangrado, así que es legible por obligación.
- **Tipado dinámico** y gestión de memoria automática: no declaras tipos ni reservas memoria a mano (justo lo contrario que [[Curso_C/historia-de-c|C]]).
- **"Baterías incluidas"** (*batteries included*): una biblioteca estándar grande, para que muchas tareas comunes se resuelvan sin instalar nada.
- Estructuras potentes de serie: listas, diccionarios, cadenas con métodos cómodos.

La apuesta de fondo: **el código se lee muchas más veces de las que se escribe**. Si optimizas para la legibilidad, ganas en mantenimiento, en enseñanza y en colaboración. Era una idea poco de moda en una época que premiaba la astucia y la concisión crípticas, y resultó ser visionaria.

---

## Parte III — El Zen de Python: una filosofía con humor

Esa filosofía acabó destilada en un pequeño poema de **19 aforismos**, el **Zen de Python** (PEP 20), escrito por **Tim Peters** hacia 1999. Lo puedes invocar hoy mismo en cualquier intérprete escribiendo `import this`:

```
Bello es mejor que feo.
Explícito es mejor que implícito.
Simple es mejor que complejo.
La legibilidad cuenta.
...
Debería haber una —y preferiblemente solo una— manera obvia de hacerlo.
```

Esa última línea es una declaración de guerra cultural. Frente a la filosofía de **Perl** —*"There's more than one way to do it"* (hay más de una forma de hacerlo)—, Python defiende lo contrario: **una sola forma obvia**. Menos ingenio, más consenso. Es la razón de que el código Python de dos personas distintas se parezca tanto, y de que sea tan fácil de leer.

**Curiosidad — los huevos de Pascua.** Python está lleno de bromas escondidas. `import this` muestra el Zen. `import antigravity` **abre el navegador en una tira cómica de xkcd** (la 353, donde alguien vuela "porque Python"). Y si escribes `from __future__ import braces` (pidiendo poder usar llaves como en C), el intérprete responde: **`SyntaxError: not a chance`** ("ni de broma"). El mensaje es claro: Python nunca tendrá llaves.

---

## Parte IV — De 1.0 a 2.0: nace una comunidad (1994–2000)

**Python 1.0** llegó en **enero de 1994**. Guido se mudó después a Estados Unidos (al CNRI), y el lenguaje fue ganando tracción poco a poco entre administradores de sistemas, científicos y gente que necesitaba "pegar" programas entre sí.

El salto importante fue **Python 2.0**, en **octubre de 2000**. No solo trajo features clave —**list comprehensions** (esa forma compacta y elegante de construir listas), recolección de basura con detección de ciclos, soporte de Unicode—, sino algo más profundo: el desarrollo se abrió a la comunidad. Python dejó de ser "lo que decidía Guido" para volverse un proyecto colaborativo con su propio proceso de propuestas, las **PEP** (*Python Enhancement Proposals*).

---

## Parte V — El gran cisma: Python 2 vs Python 3 (2008–2020)

En **diciembre de 2008** llegó la decisión más valiente y más dolorosa de la historia del lenguaje: **Python 3.0**, deliberadamente **incompatible** con Python 2. Guido y el equipo decidieron romper la compatibilidad para arreglar de una vez defectos de diseño acumulados durante años:

- `print` pasó de ser una instrucción (`print "hola"`) a una **función** (`print("hola")`).
- La división `/` pasó a dar decimales por defecto (`3/2 == 1.5`, no `1`).
- El texto pasó a ser **Unicode** por defecto (un lío enorme en Python 2).

El problema: **millones de líneas de Python 2 ya escritas no funcionaban en Python 3**. Empezó una migración que duró **más de una década**. Durante años convivieron los dos mundos, con bibliotecas que soportaban uno, otro o ambos a duras penas. **Python 2.7** (2010) fue la última versión 2.x, y su **fin de vida oficial fue el 1 de enero de 2020** — tras varias prórrogas. Fue una transición larga y a ratos traumática, pero hoy se ve como la decisión correcta: sin ella, Python cargaría aún con la herencia de los 90.

**Curiosidad — la valentía de romper cosas.** Pocos lenguajes de éxito se atreven a romper la compatibilidad hacia atrás a propósito (compara con [[Curso_C/historia-de-c|C]], obsesionado con que el código viejo siga compilando). Python lo hizo, sufrió por ello más de diez años, y salió reforzado. Es el ejemplo de manual de "deuda técnica que merece la pena pagar".

---

## Parte VI — Qué se construye con Python (y por qué explotó)

Python empezó como lenguaje de scripting y "pegamento", pero fue colonizando un campo tras otro hasta volverse omnipresente:

| Campo | Lo que corre sobre Python |
|---|---|
| **Web** | **Django** (2005, base de Instagram), **Flask** (2010), **FastAPI** (2018) — el del [[Curso_Servidores_y_Redes/00_README|curso de servidores]] |
| **Ciencia de datos** | **NumPy**, **pandas**, **Matplotlib**, **Jupyter** — el ecosistema científico estándar |
| **Inteligencia artificial** | **scikit-learn**, **TensorFlow** (Google), **PyTorch** (Meta) — Python es **la lengua franca de la IA** |
| **Automatización / DevOps** | scripts, *scraping*, Ansible, pipelines de datos |
| **Grandes productos** | Instagram, YouTube, Dropbox, Reddit, Spotify, Netflix |

**Curiosidad — Python es rápido porque por dentro es C.** Aquí se cierra el círculo con la [[Curso_C/historia-de-c|historia de C]]: el intérprete de Python que casi todo el mundo usa, **CPython**, está escrito en C. Y las bibliotecas que hacen a Python rápido para ciencia e IA (NumPy, PyTorch…) tienen su núcleo pesado en **C/C++**, con Python como una capa cómoda por encima. Python no compite con C: lo *abraza*. Tú escribes Python legible; el trabajo bruto lo hace C por debajo. Esa combinación —comodidad arriba, velocidad abajo— es buena parte del secreto de su éxito.

¿Por qué explotó? Tres razones que se reforzaron: es **fácil de leer y aprender** (lo hace ideal para enseñar y para gente que no es informática de carrera, como científicos), tiene **"baterías incluidas" y un ecosistema gigantesco**, y llegó en el momento justo a la **ola de los datos y la IA**, que necesitaban exactamente un lenguaje así.

---

## Parte VII — Guido, el "dictador benevolente", y su renuncia (2018)

Durante casi tres décadas, Guido tuvo la última palabra sobre el diseño del lenguaje. La comunidad le dio un título medio en broma medio en serio: **BDFL**, *Benevolent Dictator For Life* (Dictador Benévolo Vitalicio). No mandaba por la fuerza, pero cuando un debate se atascaba, él decidía.

En **2018**, una propuesta concreta —el **operador morsa** `:=` (PEP 572), que permite asignar dentro de una expresión— desató un debate tan agrio y agotador en la comunidad que, tras aprobarlo, **Guido dimitió como BDFL** (julio de 2018). En su mensaje de despedida dejó claro que estaba cansado de las peleas. Python pasó entonces a gobernarse por un **Consejo de Dirección** (*Steering Council*) elegido por los desarrolladores: el dictador benévolo dejó paso a una pequeña democracia.

**Curiosidad — un operador tumbó al fundador.** Que el detonante de la marcha de Guido fuera algo tan pequeño como `:=` dice mucho de lo intensas que pueden ser las discusiones de diseño en una comunidad apasionada. El operador morsa entró en Python 3.8 (2019); Guido, mientras tanto, se tomó un respiro… y al poco volvió como un colaborador más, ya sin la corona.

---

## Parte VIII — Python hoy: el número uno y la nueva era

Python lleva años en lo más alto de prácticamente todos los rankings de popularidad (es el **nº 1 de TIOBE** desde principios de los 2020), empujado sobre todo por la **explosión de la IA** y por ser el lenguaje con el que casi todo el mundo aprende a programar hoy.

Pero tiene una asignatura histórica pendiente: el **GIL** (*Global Interpreter Lock*), un candado interno de CPython que, simplificando, impide que varios hilos ejecuten código Python *a la vez* —un problema en la era de los procesadores con muchos núcleos—. La comunidad lleva años trabajando en dos frentes:

- **Faster CPython**: un esfuerzo (con Guido en el equipo) para acelerar el intérprete; Python **3.11** (2022) fue notablemente más rápido que el anterior.
- **Quitar el GIL**: la **PEP 703** abrió la puerta a un CPython *sin* GIL, disponible de forma experimental desde **Python 3.13** (2024). Si cuaja, será uno de los cambios más profundos en la vida del lenguaje.

**Curiosidad — de Google a Microsoft.** La carrera de Guido es un mapa de Silicon Valley: trabajó en **Google** (2005-2012, donde dedicaba la mitad de su tiempo a Python), luego en **Dropbox** (2013-2019, una empresa construida casi entera en Python), se "jubiló"… y en 2020 volvió al ruedo en **Microsoft**, precisamente para hacer Python más rápido. Cuesta encontrar un lenguaje cuyo creador siga arremangándose con él 35 años después.

---

## Parte IX — Curiosidades extra

**Spam, huevos y humor inglés.** Más allá de `spam` y `eggs`, toda la cultura de Python tiene un punto gamberro heredado de Monty Python. La documentación oficial, históricamente, está salpicada de bromas y referencias al grupo.

**La legibilidad como ley.** Que la **indentación sea obligatoria** (y no decorativa) fue, en su día, polémico: a muchos programadores les parecía una imposición. Hoy es una de las razones por las que el código Python ajeno se entiende casi siempre a la primera. Lo que parecía un capricho era una decisión de diseño profunda.

**El logo de las dos serpientes.** El logo moderno (dos serpientes entrelazadas, azul y amarilla) no llegó hasta **2006**. Durante quince años, el lenguaje "de la serpiente" no tuvo serpiente alguna: solo el chiste de Monty Python.

**PEP: gobernar con documentos.** Casi cada decisión importante de Python vive en una **PEP** (propuesta numerada y discutida en abierto). El propio Zen es la PEP 20; el estilo de código que casi todo el mundo sigue es la **PEP 8**. Es un modelo de gobernanza técnica que muchos otros proyectos han copiado.

---

## Tabla de hitos cronológicos

| Año | Evento |
|-----|--------|
| **dic 1989** | **Guido van Rossum empieza Python en vacaciones de Navidad** (CWI, Ámsterdam). |
| feb 1991 | Primera versión pública (0.9.0) en *alt.sources*. Indentación, baterías incluidas. |
| ene 1994 | **Python 1.0**. |
| oct 2000 | **Python 2.0**: list comprehensions, Unicode, desarrollo abierto, PEPs. |
| 2004 | Tim Peters formaliza el **Zen de Python** (PEP 20). Sale la **PEP 8** (estilo). |
| 2005-2012 | Guido trabaja en **Google** (medio tiempo dedicado a Python). |
| **dic 2008** | **Python 3.0**: ruptura deliberada con Python 2 para arreglar el diseño. |
| jul 2010 | **Python 2.7**, la última de la rama 2.x. |
| 2015 | *Type hints* (PEP 484) y `async`/`await` (3.5). |
| dic 2016 | **f-strings** (3.6): formateo de cadenas cómodo. |
| **jul 2018** | **Guido dimite como BDFL** tras el debate del operador morsa `:=`. |
| 2019 | Operador morsa `:=` en 3.8. Gobierno por **Steering Council**. |
| **1 ene 2020** | **Fin de vida de Python 2.** Fin de un cisma de más de una década. |
| oct 2021 | **Pattern matching** `match/case` (3.10). |
| 2022 | **Faster CPython** (3.11, mucho más rápido). Python, nº 1 en TIOBE. |
| 2024 | **CPython sin GIL** experimental (PEP 703) en Python **3.13**. |

---

## Conexiones

- [[Curso_Python/00_README|Curso de Python]] — el itinerario práctico
- [[Curso_Python/modelo/00-python-vs-c]] — el puente C → Python
- [[Curso_C/historia-de-c|Historia de C]] — el padre de bajo nivel (CPython está escrito en C)
- [[Linux/historia-de-linux|Historia de Linux]] — completa la trilogía
- [[Curso_Servidores_y_Redes/00_README|Curso de Servidores y Redes]] — FastAPI, Python en acción
- [[MOC_Programacion]] · [[MOC_NeetCode_150]]

---

*Documento narrativo elaborado con Claude Code (2026-06-17). Fechas y datos contrastables con: los escritos de Guido van Rossum sobre los orígenes de Python, las PEP oficiales (PEP 20 "Zen of Python", PEP 8, PEP 484, PEP 572, PEP 703), el historial de versiones de python.org y el calendario de fin de vida de Python 2 (1-ene-2020).*
