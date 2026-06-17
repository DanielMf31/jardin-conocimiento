---
title: Historia de Linux
date: 2026-06-12
tags: [programacion/linux, historia, cultura]
type: nota
status: permanente
source: claude-code
aliases: [historia de linux, historia linux]
---


# Historia de Linux

> *"Just a hobby, won't be big and professional like gnu."*
> — Linus Torvalds, 25 de agosto de 1991 (en comp.os.minix)

Hay pocas historias en la tecnología que combinen todos los ingredientes de una buena novela: un estudiante solitario con un ordenador de segunda mano, una disputa filosófica sobre la naturaleza del software libre, una guerra de egos entre académicos, y un accidente feliz que termina siendo el sistema operativo más usado del planeta. La historia de Linux es todo eso. Y empieza, como muchas buenas historias, mucho antes del protagonista.

---

## Parte I — La prehistoria: antes de que Linux existiera (1969–1991)

Para entender Linux hay que entender que es, en gran medida, **un Unix que no es Unix**. Y Unix nació mucho antes, en un sitio casi mítico: los **Bell Labs** de AT&T, en Nueva Jersey.

### Unix: dos genios, un PDP y un juego espacial (1969)

En 1969, **Ken Thompson** y **Dennis Ritchie**, dos investigadores de Bell Labs, acababan de salir de un proyecto fallido y enormísimo llamado **Multics** — un sistema operativo que pretendía ser compartido por millones de usuarios, pero que resultó ser demasiado complejo, demasiado lento, demasiado caro. Bell Labs se retiró del proyecto. Thompson, que quería seguir jugando a un juego que había escrito (*Space Travel*), rescató una vieja minicomputadora **PDP-7** abandonada en los laboratorios y, sobre ella, durante el verano de 1969 — según la historia canónica, en el mes que su mujer Bonnie estuvo de viaje con su hijo de un año — construyó la primera versión reconocible de un sistema operativo pequeño, simple y elegante.

Como reacción irónica a la complejidad de Multics, lo llamaron primero **UNICS** (Uniplexed Information and Computing Service), luego **Unix**. La ironía estaba en el nombre: *Uni* en lugar de *Multi*. Menos es más.

La gran revolución llegó pocos años después. Para no tener que reescribir Unix en ensamblador cada vez que cambiaba de máquina, Ritchie desarrolló entre 1972 y 1973 un nuevo lenguaje de programación: el **lenguaje C**. En 1973 reescribieron casi todo el núcleo de Unix en C. Esto fue **enorme**: por primera vez, un sistema operativo era *portable*. Podías llevarlo a otra arquitectura simplemente recompilando, en lugar de reescribirlo entero. Una idea que tardó años en explotar del todo, pero la mecha ya estaba encendida.

> **Curiosidad**: La filosofía Unix —"haz una sola cosa y hazla bien", "todo es un archivo", "programas pequeños conectados con tuberías"— sigue viva cada vez que escribes `cat archivo | grep error | wc -l` en tu terminal. Esa tubería `|` es un invento de Bell Labs de hace más de cincuenta años. Kernighan y Ritchie documentaron todo esto en *The C Programming Language* (1978), conocido simplemente como "K&R", considerado aún hoy uno de los mejores libros técnicos jamás escritos.

### Las "guerras Unix" y BSD

AT&T, por un decreto antimonopolio que le impedía vender software comercialmente, distribuyó Unix a universidades casi gratis y con el código fuente durante los 70. El resultado fue una explosión de creatividad académica. En la **Universidad de California en Berkeley** surgió la **BSD** (*Berkeley Software Distribution*), que añadió cosas que hoy damos por sentadas, como la implementación de referencia de **TCP/IP** — el protocolo que sostiene internet.

Cuando en los 80 AT&T pudo por fin comercializar Unix, empezaron las **"Unix Wars"**: AT&T (System V) contra BSD, fabricantes peleándose por extensiones propietarias incompatibles, y una maraña de demandas legales. Cada fabricante tomaba el código base y añadía sus variantes: **HP-UX**, **AIX** de IBM, **SunOS**, **Solaris**, **IRIX** de SGI... Administradores de sistemas que tenían que aprender dialectos incompatibles, software que no compilaba de un Unix al otro, una balcanización que debilitó todo el ecosistema. El intento de estandarización con **POSIX** (1988) ayudó, pero el daño ya estaba hecho.

A principios de los 90, AT&T demandó a la Universidad de Berkeley alegando que partes de BSD contenían código propietario. La batalla legal paralizó BSD justo en el momento más crítico. Ese vacío — un Unix libre, con licencia limpia, disponible para PC — esperaba ser llenado.

### MINIX: el Unix de juguete para aprender (1987)

Mientras tanto, un profesor holandés, **Andrew S. Tanenbaum**, quería enseñar sistemas operativos en la Vrije Universiteit de Ámsterdam, pero AT&T había prohibido usar el código de Unix en contexto académico. Así que Tanenbaum escribió desde cero **MINIX**: un mini-Unix *educativo*, incluido en su libro *Operating Systems: Design and Implementation* (1987), pensado para PCs de la época con procesador 386.

MINIX era pequeño, limpio, y usaba un diseño de **microkernel** — un núcleo mínimo que delega en procesos separados. Tanenbaum lo controlaba con mano firme para mantenerlo pedagógicamente manejable. Si querías añadir soporte para un nuevo dispositivo o cambiar algo, necesitabas el permiso del profesor. Para un estudiante que quería trastear de verdad, era desesperante.

### GNU: Stallman declara la guerra al software propietario (1983)

El último ingrediente de la prehistoria es el más ideológico. En **septiembre de 1983**, un programador del MIT llamado **Richard Matthew Stallman** (RMS) anunció el **Proyecto GNU** — acrónimo recursivo de *"GNU's Not Unix"*. Su objetivo: construir un sistema operativo **completo, libre y compatible con Unix**, donde "libre" significaba libertad real (usar, estudiar, modificar y compartir el software), no precio.

Para blindar legalmente esa libertad, Stallman inventó un truco jurídico brillante que formalizó en la **GPL** (*GNU General Public License*) y su concepto de *copyleft*: cualquiera puede usar y modificar el software, pero **si lo distribuyes, debes liberar tus cambios bajo la misma licencia**. El copyright usado al revés, para garantizar libertad en lugar de restringirla.

Hacia 1991, GNU tenía casi todas las piezas de un sistema operativo libre: el compilador **GCC**, el shell **Bash**, el editor **Emacs**, el depurador **GDB**, las utilidades de sistema (grep, awk, sed, coreutils...)... pero les faltaba la pieza central: **el kernel**. El núcleo GNU, llamado **GNU Hurd**, llevaba años en desarrollo y seguía sin estar listo para uso real — demasiado ambicioso en su arquitectura de microkernel, demasiado difícil de llevar a la práctica. GNU era un cuerpo casi completo al que le faltaba el corazón.

Resumamos el tablero en 1991:
- Un **cuerpo sin corazón**: GNU, con todas las herramientas listas pero sin kernel.
- Un **hueco de mercado**: la gente quería un Unix libre y de licencia limpia para PCs asequibles.
- Un **estudiante frustrado** con MINIX, un PC nuevo y demasiada curiosidad.

---

## Parte II — Helsinki, 1991: nace el corazón

### Un 386 y mucha impaciencia

**Linus Benedict Torvalds** nació en Helsinki el 28 de diciembre de 1969 — curiosamente, el mismo año que nacía Unix. En 1991 tenía 21 años y cursaba su segundo año de informática en la Universidad de Helsinki. Había crecido programando en un Commodore VIC-20, luego en un Sinclair QL, y había desarrollado esa obsesión característica de ciertos ingenieros por entender las máquinas hasta el nivel más bajo posible.

Ese año, Linus compró (a plazos) un PC con el flamante procesador **Intel 80386** — el estado del arte para un particular en esa época. Instaló MINIX, pero las restricciones lo frustraban: no podía modificarlo como quería, no tenía emulación de terminal decente para conectarse a los servidores de la universidad, no tenía lo que necesitaba. Y en lugar de esperar — o de conformarse — decidió hacer algo que en retrospectiva parece una locura: escribir su propio sistema operativo desde cero.

Empezó en la primavera de 1991 con experimentos sobre las capacidades de multitarea del 386. Lo que empezó como un emulador de terminal para conectarse a los servidores de la universidad fue creciendo: un sistema de ficheros, gestión de memoria, llamadas al sistema. Para agosto ya tenía algo reconocible como un núcleo de sistema operativo funcional.

### El post más famoso de la historia del software (25 de agosto de 1991)

El **25 de agosto de 1991**, Linus publicó un mensaje en el grupo de noticias de Usenet **comp.os.minix**. El texto original, en inglés, con el typo histórico preservado:

```
Hello everybody out there using minix -

I'm doing a (free) operating system (just a hobby, won't be big and
professional like gnu) for 386(486) AT clones. This has been brewing
since april, and is starting to get ready. I'd like any feedback on
things people like/dislike in minix, as my OS resembles it somewhat
(same physical layout of the file-system (due to practical reasons)
among other things).

I've currently ported bash(1.08) and gcc(1.40), and things seem to
work. This implies that I'll get something practical within a few
months, and I'd like to know what features most people would want.
Any suggestions are welcome, but I won't promise I'll implement them :-)

Linus (torvalds@kruuna.helsinki.fi)

PS. Yes - it's free of any minix code, and it has a multi-threaded fs.
It is NOT protable (uses 386 task switching etc), and it probably never
will support anything other than AT-harddisks, as that's all I have :-(
```

La modestia es, en retrospectiva, casi cómica. *"Just a hobby, won't be big and professional like gnu"* — solo un hobby, nunca será grande ni profesional. Y añade en la posdata que el sistema NO es portable y *"probablemente nunca soportará nada más que discos AT, que es todo lo que tengo"*. Hoy Linux corre en teléfonos, supercomputadores, coches autónomos, sondas espaciales, routers... y en prácticamente cualquier dispositivo con un procesador.

> **Curiosidad**: Fíjate en que Linus menciona en el mismo mensaje que ya ha portado **bash** y **gcc** — herramientas del proyecto GNU. Desde el primer minuto, el corazón que Linus estaba construyendo latía dentro del cuerpo que Stallman había pasado casi una década ensamblando. El encuentro fue casi inconsciente.

### El nombre que Linus no eligió: de "Freax" a "Linux"

Linus, según relata en su autobiografía *Just for Fun* (2001), quería llamar a su sistema **"Freax"** — una mezcla de *free*, *freak* y la *x* de los sistemas Unix-like. Consideraba que llamarlo "Linux" era demasiado egocéntrico. En sus propias palabras del libro:

> *"Privately, I called it Linux. Honest: I didn't want to ever release it under the name Linux because it was too egotistical. What was the name I reserved for any eventual release? Freax."*

Cuando subió los primeros archivos al servidor FTP de la red universitaria finlandesa (`ftp.funet.fi`, de la Finnish University and Research Network), fue **Ari Lemmke** — administrador voluntario del servidor — quien creó el directorio donde se alojaría el proyecto. Sin consultar a Torvalds, lo llamó simplemente **`linux`**. El nombre quedó visible para todo el que descargaba el kernel, y simplemente... se quedó. Linus cedió ante el hecho consumado. El sistema operativo que hoy corre en miles de millones de dispositivos se llama así en parte por la decisión unilateral de un administrador de FTP al que no le gustaba el nombre original.

### La decisión que lo cambió todo: la GPL (1992)

Las primeras versiones de Linux llevaban una licencia propia que prohibía el uso comercial. Con la versión **0.12**, a principios de **1992**, Linus tomó la decisión más importante de su carrera: relicenciar el kernel bajo la **GPL v2**.

Esta decisión desató una colaboración sin precedentes. La GPL garantizaba a cualquier colaborador que sus mejoras no serían "secuestradas" por ninguna empresa: podías invertir tu tiempo sabiendo que el resultado seguiría siendo libre para todos. Eso removió una barrera psicológica enorme, y los parches empezaron a llegar de todo el mundo.

Y con eso se completó el puzzle: **el kernel Linux + las herramientas GNU = un sistema operativo libre y completo**. El corazón de Helsinki, latiendo dentro del cuerpo que Stallman había construido en el MIT durante casi una década.

> **Curiosidad — el debate del nombre "GNU/Linux"**: Stallman y la FSF defienden que el sistema completo debería llamarse **"GNU/Linux"**, porque "Linux" en sentido estricto es *solo el kernel*, y la mayor parte de las herramientas que usas a diario (bash, gcc, las coreutils...) son GNU. La mayoría de la gente dice simplemente "Linux". Torvalds, con su pragmatismo habitual, considera que el debate es pedante. Es uno de los temas más polémicos y recurrentes de la comunidad del software libre, con más de treinta años de historia y sin visos de resolución.

---

## Parte III — La pelea legendaria: Tanenbaum vs. Torvalds (1992)

A principios de 1992, el creador de MINIX no estaba impresionado. El **29 de enero de 1992**, Andrew Tanenbaum abrió un hilo en comp.os.minix con un título que es ya historia del flame war:

**"LINUX is obsolete"**

El argumento técnico tenía dos patas principales:

**1. Microkernel vs. monolítico.** Linux es un **kernel monolítico**: todo el sistema — drivers, gestión de memoria, sistema de archivos, red — vive en un solo bloque de código ejecutándose en modo privilegiado. Tanenbaum defendía el **microkernel**: un núcleo mínimo, con los servicios separados en procesos de usuario aislados, más limpio, más robusto en teoría. Sus palabras exactas del hilo original:

> *"writing a monolithic system in 1991 is a truly poor idea"*
> *"a giant step back into the 1970s"*
> *"the debate is essentially over. Microkernels have won"*

**2. Portabilidad.** Linux estaba atado a la arquitectura x86. Cuando esa arquitectura quedara obsoleta, Linux moriría con ella.

Linus respondió con la combatividad que lo haría famoso, defendiendo el pragmatismo: los microkernels son elegantes en teoría, pero más lentos y más complicados de implementar bien en la práctica. Un kernel monolítico bien escrito es más rápido y más fácil de desarrollar. El hilo acumuló unas 73 respuestas a lo largo de varias semanas.

> **Curiosidad — ¿quién ganó?**: Académicamente, Tanenbaum tenía razón en lo conceptual: los microkernels son arquitectónicamente más elegantes. En la práctica, ganó Linus por goleada — Linux conquistó el mundo mientras GNU Hurd sigue siendo un proyecto de investigación décadas después. Pero hay un giro final delicioso: **MINIX**, el SO educativo de Tanenbaum, acabó embebido en el **Intel Management Engine** — un subsistema de gestión oculto dentro de prácticamente todos los procesadores Intel modernos. Así que durante años, MINIX fue posiblemente el sistema operativo más *instalado* del planeta... corriendo en secreto dentro de tu propio ordenador, sin que nadie lo supiera, incluyendo al propio Tanenbaum, que se enteró por la prensa en 2017. Sobre la portabilidad: hoy Linux corre en x86, ARM, RISC-V, PowerPC, MIPS, SPARC, y prácticamente cualquier arquitectura de procesador relevante.

---

## Parte IV — Los años de expansión: distros, Tux y trajes (1993–2000)

Un kernel pelado no le sirve a nadie para el día a día. Necesitas un instalador, un gestor de paquetes, programas, configuración... Así nacieron las **distribuciones**: paquetes que combinan el kernel Linux con herramientas GNU y software adicional, listos para instalar.

### Las primeras distros

| Año | Distribución | Creador / Organización | Nota |
|-----|-------------|----------------------|------|
| 1992 | MCC Interim Linux | Owen Le Blanc (Manchester) | Primer intento de Linux "empaquetado" |
| 1993 | **Slackware** | Patrick Volkerding | La distro más antigua aún activa; minimalista, sin florituras |
| 1993 | **Debian** | Ian Murdock | Comunitaria, rigurosa; base directa de Ubuntu y cientos más |
| 1994 | **SUSE** | Roland Dürr et al. (Alemania) | Fuerte en Europa y entorno empresarial |
| 1994 | **Red Hat** | Marc Ewing / Bob Young | El gigante comercial; base de RHEL, Fedora, CentOS |

**Debian** merece un párrafo aparte. **Ian Murdock** — el nombre viene de "Deb"ra Lynn, su novia en aquel momento, más "Ian" — concibió una distribución que no dependiera de ninguna empresa sino de una comunidad de voluntarios gobernada democráticamente. Debian fue pionera en el modelo de **contrato social con el software libre** y en sistemas de empaquetado sofisticados. Hoy, Ubuntu — la distribución más usada en escritorio Linux — es una derivada directa de Debian.

### Tux, la mascota

En 1996, Linux necesitaba una imagen. La elección del pingüino como mascota tiene su anécdota: hacia **1993**, durante un viaje a Canberra (Australia) para un evento del Australian Unix Users Group, Linus fue mordido por un pingüino pigmeo (*Eudyptula minor*, conocido localmente como "fairy penguin"). En sus propias palabras, años después:

> *"I've been to Australia several times these days mostly for Linux.Conf.Au. But my first trip — and the one when I was bitten by a ferocious fairy penguin: you really should keep those things locked up! — was in 93 or so talking about Linux for the Australian Unix Users Group."*

Desde entonces Torvalds declara haber desarrollado cierta "penguinitis" — es decir, a encontrar simpáticos a los pingüinos. En **1996**, el programador **Larry Ewing** dibujó la mascota oficial usando **GIMP 0.54**. La primera aparición pública de Tux fue el **9 de mayo de 1996**. El nombre **"Tux"** lo propuso James Hughes el **10 de junio de 1996** — suele leerse como **T**orvalds **U**ni**X**, aunque también evoca el esmoquin (*tuxedo*) blanco y negro del pingüino.

> **Curiosidad**: Larry Ewing nunca cobró un céntimo por dibujar una de las imágenes de software más reconocidas del mundo. El archivo original está disponible libremente bajo una licencia sin restricciones.

### Entran los trajes: IBM y los mil millones (2000)

El **12 de diciembre de 2000**, en la eBusiness Conference and Expo de Nueva York, el CEO de IBM **Lou Gerstner** anunció que la compañía comprometía **1.000 millones de dólares para 2001 en Linux** — además de cerca de esa misma cifra ya invertida durante 2000 en hardware, software y servicios relacionados. IBM tenía en ese momento aproximadamente 1.500 desarrolladores trabajando directamente en Linux.

El mensaje para toda la industria fue inconfundible: Linux ya no era un juguete de universitarios. Era infraestructura seria. Sun, Oracle, HP y prácticamente todas las grandes tecnológicas siguieron. El ecosistema empresarial alrededor de Linux creció exponencialmente en los años siguientes. Red Hat había hecho su OPV en bolsa en 1999, en plena burbuja .com, y el precio de sus acciones se multiplicó por cinco el primer día de cotización — uno de los debuts bursátiles más espectaculares de la historia tecnológica hasta entonces.

---

## Parte V — Git: la herramienta que Linus inventó en diez días (2005)

Coordinar el trabajo de miles de ingenieros en todo el mundo sobre el mismo proyecto de software plantea un problema logístico brutal: **¿cómo gestionas el código?** ¿Cómo fusionas miles de parches sin perder la cabeza?

Durante años, el kernel usó **BitKeeper**, un sistema de control de versiones distribuido cedido gratuitamente a la comunidad por su autor, Larry McVoy, con una condición explícita: nadie podía hacer ingeniería inversa de su protocolo. En la primavera de 2005, el desarrollador **Andrew Tridgell** — conocido por crear Samba — empezó a escribir una herramienta para interactuar con repositorios BitKeeper analizando el protocolo de red. McVoy lo consideró una violación de la licencia y retiró la versión gratuita para proyectos de código abierto.

En palabras del propio Torvalds sobre Tridgell:

> *"Tridge in Australia basically reverse engineered BitKeeper... that was explicitly against the license."*

Linus se quedó de repente sin herramienta de control de versiones para el proyecto de software más importante del mundo. Su respuesta fue escribir la suya. Empezó el **3 de abril de 2005**. El **7 de abril** hizo el primer commit autoalojado en el repositorio recién creado, con el mensaje: *"Initial revision of 'git', the information manager from hell"*. Y en sus propias palabras sobre la velocidad de desarrollo:

> *"It was actually fewer than — well, it was about 10 days until I could use it for the kernel, yes."*

Git no era solo rápido de escribir: su modelo de datos — un grafo acíclico dirigido de objetos inmutables identificados por hashes SHA-1 — era conceptualmente superior a cualquier sistema equivalente de la época. En agosto de 2005, Linus transfirió el mantenimiento a **Junio Hamano**, que lo lleva hasta el día de hoy.

El impacto de Git es comparable al del propio Linux. GitHub, construido sobre Git en 2008, se convirtió en el repositorio de código más grande del mundo. En 2018, Microsoft lo adquirió por **7.500 millones de dólares**. La herramienta que Linus escribió en diez días, como reacción irritada a un problema de licencias, se convirtió en la infraestructura sobre la que descansa prácticamente todo el desarrollo de software del mundo.

> **Curiosidad**: El nombre "git" es argot británico para "persona estúpida o desagradable". Linus lo explicó con su habitual ironía: *"I'm an egotistical bastard, and I name all my projects after myself. First 'Linux', now 'git'."* Creó el kernel más importante del mundo y, casi de pasada, el sistema de control de versiones más usado de la historia. Los dos llevan su nombre. Los dos nacieron de la impaciencia.

---

## Parte VI — Linus, el personaje

Linux es inseparable de la personalidad de su creador, y conocerla explica buena parte de la cultura técnica del mundo del software libre.

### El estilo "brutalmente honesto"

Durante décadas, la **LKML** (*Linux Kernel Mailing List*) fue famosa — y temida — por el estilo de Torvalds: directo hasta la crueldad, alérgico a la diplomacia, con rants feroces cuando alguien proponía algo que consideraba mal diseñado. Para él era meritocracia pura ("juzgo el código, no las personas"); para muchos otros, era simplemente maltrato.

El ejemplo más citado del período moderno: el **14 de junio de 2012**, en una sesión de preguntas en el **Aalto Center for Entrepreneurship** en Otaniemi, Finlandia (Universidad Aalto). Un estudiante preguntó por la falta de soporte de **NVIDIA** para Linux, concretamente el problema de Optimus (la tecnología de GPU dual en portátiles). Linus, mirando directamente a la cámara, levantó el dedo medio y dijo textualmente:

> *"So, NVIDIA, fuck you."*

El vídeo se viralizó. NVIDIA eventualmente mejoró su soporte para Linux — años después, en 2022, abrió parcialmente los drivers del kernel bajo licencia MIT/GPLv2.

### 2018: la disculpa

Ese estilo también tenía consecuencias menos divertidas. El **16 de septiembre de 2018**, Linus publicó en la LKML un email con asunto *"Linux 4.19-rc4 released, an apology, and a maintainership note"* que sorprendió a toda la comunidad. En él escribió:

> *"I am not an emotionally empathetic kind of person and that probably doesn't come as a big surprise to anybody."*
> *"My flippant attacks in emails have been both unprofessional and uncalled for. Especially at times when I made it personal."*
> *"I know now this was not OK and I am truly sorry."*
> *"I am going to take time off and get some assistance on how to understand people's emotions and respond appropriately."*

Y, aclarando el alcance de su pausa:

> *"This is not some kind of 'I'm burnt out, I need to just go away' break."*

Ese mismo día, el "Code of Conflict" del kernel fue reemplazado por un nuevo **Code of Conduct** basado en el Contributor Covenant. Linus pidió a **Greg Kroah-Hartman** que finalizara la versión 4.19 en su ausencia. A su regreso, su tono en la lista de correo fue notablemente más moderado, sin perder su característica franqueza técnica.

### El pragmático frente al idealista

La gran tensión filosófica del mundo Linux se resume en dos figuras:

- **Richard Stallman (GNU/FSF):** el idealista. Para él, el software libre es una cuestión ética y moral fundamental. El software propietario es éticamente injusto. No transige.
- **Linus Torvalds:** el pragmático. Para él, el código abierto es, sobre todo, el mejor método de ingeniería para hacer buen software. Por eso usa, sin drama, el término "open source" en lugar del más militante "free software" de Stallman.

Esa tensión — ideal vs. práctica, filosofía vs. pragmatismo — recorre toda la historia del software libre y sigue generando debates acalorados hoy.

---

## Parte VII — El modelo de desarrollo: la catedral, el bazar y el milagro logístico

¿Cómo se coordina el trabajo de miles de ingenieros en 50 países sobre el proyecto de software voluntario más grande de la historia?

En **1997**, el hacker **Eric S. Raymond** intentó explicarlo en un ensayo influyentísimo: **"La Catedral y el Bazar"** (*The Cathedral and the Bazaar*). Su tesis: hay dos modelos de construir software.

- **La Catedral:** un grupo pequeño y cerrado construye en secreto y libera la obra ya terminada. Controlado, planificado, lento.
- **El Bazar:** un caos aparente y abierto donde todo el mundo ve el código, todo el mundo aporta y las versiones se liberan a menudo y temprano. Ruidoso, desordenado... y sorprendentemente eficaz.

Linus había establecido desde el principio el principio del bazar: *"release early, release often"* — libera pronto, libera a menudo. No esperes a tener algo perfecto; publica, acepta feedback, corrige rápido. De Raymond salió además la **"Ley de Linus"**: *"Given enough eyeballs, all bugs are shallow"* — con suficientes pares de ojos mirando el código, cualquier bug se vuelve fácil de encontrar.

El resultado es difícil de exagerar. El kernel Linux tiene hoy más de **27 millones de líneas de código**. Cada versión — publicada aproximadamente cada 9-10 semanas — incorpora el trabajo de más de 1.700 desarrolladores de más de 200 empresas. Las compañías que más contribuyen incluyen Intel, Red Hat (ahora parte de IBM), Google, Samsung y Linaro.

---

## Parte VIII — Linux hoy: el sistema invisible que está en todas partes

| Dominio | Cuota / Presencia | Nota |
|---------|------------------|------|
| Supercomputación | **100 %** del TOP500 | Desde noviembre de 2017 sin excepción |
| Smartphones | ~72 % global | Android usa el kernel Linux |
| Servidores web | ~96 % (aprox.) | Apache/Nginx en Linux |
| Cloud pública | Dominante | AWS, GCP, Azure corren Linux masivamente |
| Dispositivos embebidos | Ubicuo | Routers, TVs, coches, IoT |
| Escritorio PC | ~4 % mercado | Creciendo, especialmente con Steam Deck |

**Android** merece una explicación aparte. Google eligió el kernel Linux como base de su sistema móvil, lanzado en 2008. Hoy Android supera los **3.000 millones de usuarios activos**. Esto convierte a Linux, a nivel de kernel, en el sistema operativo más usado de la historia de la humanidad. Stallman señala regularmente que Android no es "GNU/Linux" porque no incluye las herramientas GNU; técnicamente tiene razón, pero el kernel de Linus está ahí, en cada uno de esos teléfonos.

---

## Parte IX — Curiosidades extra

> **Linus el buceador.** Torvalds se aficionó al submarinismo en los 2000 y, como no encontraba buen software para registrar inmersiones, hizo lo de siempre: escribió el suyo. Se llama **Subsurface**, es libre y de código abierto, y lo sigue manteniendo activamente. El creador del mayor sistema operativo del mundo y del sistema de control de versiones más usado también te ayuda a apuntar a cuántos metros viste un pez.

> **"Just for Fun".** Su autobiografía (2001), co-escrita con el periodista David Diamond, se titula *Just for Fun: The Story of an Accidental Revolutionary*. El título resume su filosofía: nunca buscó cambiar el mundo, solo se lo estaba pasando bien programando. "Accidental" es la palabra clave. (ISBN 0-06-662072-4, HarperBusiness.)

> **Las rarezas del versionado del kernel.** El número de versión de Linux tiene una historia peculiar:
> - Durante la era 2.x, ramas menores *impares* (2.3, 2.5) eran de desarrollo experimental y las *pares* (2.4, 2.6) eran las estables. Esa convención se abandonó después.
> - Linux se quedó "atascado" en la serie **2.6 durante ocho años** (2003–2011), llegando a versiones como 2.6.39.
> - El salto a **3.0 en 2011** fue básicamente estético: los números se estaban haciendo ridículamente largos y coincidía con el 20º aniversario de Linux. No hubo ningún cambio técnico revolucionario que lo justificara.
> - Desde entonces, Linus salta de número mayor más o menos cuando el segundo número se vuelve "demasiado grande" para su gusto. El versionado del kernel más importante del mundo se rige, en parte, por el criterio estético de una sola persona.

> **El símbolo definitivo.** Cuando arrancas una máquina Linux, en el fondo se está orquestando una historia de más de cincuenta años: la filosofía de Thompson y Ritchie, el lenguaje C, las herramientas de Stallman, la GPL, el kernel de un finlandés de 21 años, y el trabajo de decenas de miles de personas que nunca se conocieron. Todo empezó con alguien que pensaba que "solo era un hobby" y que el sistema "nunca sería portable".

---

## Tabla de hitos cronológicos

| Año | Evento |
|-----|--------|
| 1969 | Ken Thompson escribe la primera versión de Unix en Bell Labs, sobre un PDP-7. |
| 1972-73 | Dennis Ritchie desarrolla C; Unix se reescribe en C — se vuelve portable. |
| 1983 | Richard Stallman anuncia el Proyecto GNU. *"GNU's Not Unix."* |
| 1987 | Tanenbaum publica MINIX como SO educativo de microkernel. |
| 1988 | POSIX: primer intento de estandarizar los Unix. |
| 1989 | GPL v1: el copyleft queda formalizado. |
| **25 ago 1991** | **Post de Torvalds en comp.os.minix. "Just a hobby."** |
| Sep 1991 | Primeros archivos de Linux subidos a ftp.funet.fi; Ari Lemmke lo llama "linux". |
| **29 ene 1992** | **Tanenbaum: "LINUX is obsolete." El flame war de los microkernels.** |
| 1992 | Linux v0.12 se relicencia bajo GPL v2. Explosión de colaboración. |
| 1993 | Slackware y Debian. Las primeras distros longevas. |
| Mar 1994 | Linux 1.0 — primera versión "estable". |
| 9 may 1996 | Primera aparición pública de Tux, dibujado por Larry Ewing con GIMP. |
| 1997 | "La Catedral y el Bazar", de Eric S. Raymond. |
| 1999 | OPV de Red Hat. Consagración bursátil. |
| Dic 2000 | IBM compromete 1.000 millones de dólares en Linux. |
| 2001 | *Just for Fun*, autobiografía de Torvalds (con David Diamond). |
| **3 abr 2005** | **Linus empieza a escribir Git tras el conflicto de BitKeeper.** |
| 7 abr 2005 | Primer commit autoalojado de Git: *"the information manager from hell"*. |
| 2008 | Android lanzado; kernel Linux en miles de millones de móviles. |
| 2011 | Salto a Linux 3.0 por el 20º aniversario (y hartazgo de los números largos). |
| **14 jun 2012** | **"So, NVIDIA, fuck you." — Aalto University.** |
| Nov 2017 | Linux copa el 100 % del TOP500 de supercomputadores. |
| **16 sep 2018** | **Torvalds se disculpa; nuevo Code of Conduct en el kernel.** |
| 2018 | Microsoft adquiere GitHub por 7.500 M$ (Git = infraestructura global). |
| 2022 | NVIDIA abre parcialmente sus drivers del kernel bajo MIT/GPLv2. |

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|fundamentos]]
- [[MOC_Hyprland]]

---

*Documento narrativo elaborado con Claude Code (2026-06-12). Fechas, nombres y citas verificadas contra: post original de comp.os.minix del 25-ago-1991 (groups.google.com), hilo Tanenbaum-Torvalds de ene-1992 (groups.google.com), GitHub Blog entrevista "Git turns 20" a Torvalds, LKML 16-sep-2018 (lkml.rescloud.iu.edu), SiliconAngle jun-2012 (charla Aalto), Wikipedia (Unix history, Tux mascot, Git, Debian), y archivo en Internet Archive de Just for Fun. Las citas en inglés son textuales del original.*
