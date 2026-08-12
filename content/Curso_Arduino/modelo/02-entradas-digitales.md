---
title: "Módulo 02 — Entradas digitales"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/gpio, electronica/botones, programacion/estado]
aliases: [entradas-digitales, digitalRead, INPUT_PULLUP, antirrebote, debounce, flanco, modulo-02-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/02-entradas-digitales.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/02-entradas-digitales.md (se regenera con gen_course.py). -->

# Módulo 02 — Entradas digitales

## Idea central

Hasta ahora la placa solo hablaba: ponía pines a 5 V o a 0 V. Ahora aprende a **escuchar**. Un pin configurado como entrada mide la tensión que le llega y te dice si está alta o baja. El problema es que el mundo físico no es tan limpio como el código: un pin sin nada conectado no lee "nada", lee ruido; y un botón mecánico, al pulsarlo una vez, genera varios cambios de estado en pocos milisegundos. Este módulo va de leer un pin y, sobre todo, de leerlo **bien**.

---

## Qué aprendes

- Leer el estado de un pin con `digitalRead`.
- Qué es un pin flotante y por qué una entrada necesita siempre una referencia.
- Usar la resistencia de pull-up interna con `INPUT_PULLUP`, y convivir con su lógica invertida.
- Qué es el rebote de un contacto mecánico y cómo filtrarlo por software con `millis()`.
- La diferencia entre **nivel** ("está pulsado") y **flanco** ("se acaba de pulsar").
- Guardar estado entre iteraciones del `loop()` para que el programa "recuerde" algo.

---

## Explicación

### Un pin que escucha: digitalRead

Un pin digital puede trabajar en dos direcciones. En el módulo 01 lo configuraste como `OUTPUT` y le dijiste qué tensión poner. Ahora lo configuras como entrada y le preguntas qué tensión tiene:

```cpp
pinMode(2, INPUT_PULLUP);     // el pin 2 va a escuchar
int estado = digitalRead(2);  // devuelve HIGH o LOW
```

`digitalRead` devuelve exactamente los mismos dos valores que usabas para escribir, `HIGH` y `LOW`, y significan lo mismo: tensión alta (cerca de 5 V) o tensión baja (cerca de 0 V). La diferencia es que ahora no los decides tú, los decide el circuito.

Como el `loop()` se repite miles de veces por segundo, `digitalRead` no espera a nada: te da una foto instantánea del pin en ese momento. Esa idea, la de "foto instantánea repetida muchísimas veces", es la que hay que tener en la cabeza durante todo el módulo.

### El problema del pin flotante

Aquí aparece la primera trampa. Si configuras un pin como `INPUT` a secas y no le conectas nada, ¿qué lee?

Lo intuitivo es pensar que leerá `LOW`, porque "no hay corriente". Pero un pin de entrada tiene una impedancia altísima: prácticamente no consume, solo mide. Un pin al aire es como una antena diminuta que recoge el ruido eléctrico del ambiente, la interferencia de la red, la capacidad de tu propio dedo al acercarte. El resultado es que lee `HIGH` y `LOW` aparentemente al azar. A eso se le llama **pin flotante**, y es la causa de un montón de comportamientos inexplicables.

Y no es un caso raro: un botón sin más produce exactamente esa situación. Un pulsador **abierto** no conecta el pin a nada. O sea que la mitad del tiempo (la mitad en que no estás pulsando) tu pin está flotando.

La conclusión es importante y vale para toda la electrónica digital: **una entrada nunca puede quedar sin referencia**. Siempre tiene que haber algo que la ate a un nivel conocido cuando el botón no actúa.

### Pull-up y pull-down

Ese "algo" es una resistencia. Hay dos formas de ponerla:

| Configuración | Dónde va la resistencia | Nivel en reposo | Nivel al pulsar |
|---|---|---|---|
| **Pull-up** | entre el pin y 5 V | `HIGH` | `LOW` (el botón lleva el pin a GND) |
| **Pull-down** | entre el pin y GND | `LOW` | `HIGH` (el botón lleva el pin a 5 V) |

La resistencia es de valor alto (decenas de kΩ), así que apenas deja pasar corriente: su único trabajo es fijar el nivel del pin cuando nadie más lo hace. En cuanto el botón se cierra y conecta el pin directamente a GND (o a 5 V), esa conexión directa gana, porque no tiene resistencia apreciable. Por eso a la resistencia se le llama "débil": manda cuando no hay nadie, y cede cuando aparece alguien.

### INPUT_PULLUP: la pull-up que ya está dentro del chip

El microcontrolador del Arduino UNO trae una resistencia de pull-up **integrada en cada pin**, de unos 20 a 50 kΩ, que puedes conectar por software. Se activa así:

```cpp
pinMode(PIN_BOTON, INPUT_PULLUP);
```

Con esa sola línea te ahorras una resistencia física y dos cables, y el pin deja de flotar. El cableado se reduce a lo mínimo: **una patilla del botón al pin, la opuesta a GND**. Nada más.

La contrapartida es la que confunde a todo el mundo la primera vez: **la lógica queda invertida**.

| Situación del botón | Camino eléctrico | Lectura del pin |
|---|---|---|
| Suelto | la pull-up interna tira del pin hacia 5 V | `HIGH` |
| Pulsado | el botón conecta el pin a GND | `LOW` |

Así que `LOW` significa **pulsado**. No es un error ni una rareza de Arduino: es la consecuencia directa de haber elegido pull-up. Todo el código del módulo empieza con la misma comparación, `if (estado == LOW)`, y hasta que no lo interiorizas te parece que el programa va al revés.

### El montaje: un botón y un LED

Los cuatro ejercicios comparten el mismo montaje, así que se hace una vez y ya no se toca. Necesitas un Arduino UNO con su cable USB, una protoboard, un pulsador de cuatro patillas, un LED de 5 mm, una resistencia de 220 Ω y unos cinco cables Dupont.

```
UNO pin 2 ──┬── [ botón ] ── GND         (entrada; la pull-up es interna)
            │
        (pull-up interna, ~20-50 kΩ, activada por software)

UNO pin 8 ──[ 220Ω ]──►|── GND           (salida; LED con ánodo hacia la resistencia)
```

Dos cosas del montaje que dan guerra:

**El botón no lleva resistencia externa.** Es lo que compra `INPUT_PULLUP`. Si además le pones una pull-up de tu cosecha no pasa nada grave, pero es cable de más para el mismo resultado.

**El pulsador de cuatro patillas une sus patillas por pares.** Dos de ellas están conectadas entre sí **siempre**, pulses o no; el botón lo único que hace es unir un par con el otro. Si por descuido usas las dos patillas del mismo par, el pin está permanentemente conectado a GND y el programa cree que el botón está pulsado desde el principio. La regla práctica: usa dos patillas de **lados opuestos**, en diagonal. Si dudas, un polímetro en modo continuidad te lo dice en dos segundos.

El LED va exactamente igual que en el módulo 01: resistencia de 220 Ω siempre, patilla larga (ánodo) hacia la resistencia, patilla corta (cátodo) a GND.

### El rebote: por qué un clic son varios clics

Ya sabes leer el botón. Ahora el mundo físico te pasa la segunda factura.

Un pulsador no es un interruptor ideal: son dos láminas metálicas que se tocan. Y cuando se tocan, **botan**, literalmente, igual que una pelota contra el suelo. Durante los primeros milisegundos el contacto se abre y se cierra varias veces antes de asentarse. Para tu dedo eso es un clic; para un microcontrolador que lee el pin cada pocos microsegundos, es una ráfaga de `HIGH` y `LOW`.

Para el ejercicio 01 da igual: el LED sigue el nivel del botón, y si durante 5 ms parpadea de forma caótica no lo ves. El problema aparece en cuanto quieres **contar** pulsaciones o **conmutar** un estado: un solo clic te suma cuatro, o te deja el LED como estaba porque lo conmutó un número par de veces.

La solución se llama **antirrebote** (o *debounce*) y la idea es sencilla de decir: no te creas un cambio hasta que lleve un rato quieto. "Un rato" son unos 50 ms, que es mucho más que la duración del rebote (típicamente 1 a 10 ms) y mucho menos que lo que un humano tarda en pulsar dos veces a propósito.

### Antirrebote con millis(), no con delay()

La tentación es escribir `delay(50)` en cuanto detectas un cambio y seguir. Funciona, y es lo que verás en la mitad de los tutoriales de internet. Pero recuerda lo del módulo 01: `delay` congela la placa entera. Durante esos 50 ms el programa no puede hacer absolutamente nada más. Con un botón se nota poco; con dos botones, un sensor y un LED parpadeando, es inaceptable.

La alternativa es `millis()`:

```cpp
unsigned long ahora = millis();  // milisegundos desde que arrancó la placa
```

`millis()` no espera: te dice qué hora es, en milisegundos, según el reloj interno de la placa. En vez de "parar 50 ms", el programa apunta **cuándo** ocurrió el último cambio y en cada vuelta del `loop()` comprueba si ya han pasado 50 ms desde entonces. Mientras tanto sigue haciendo su vida.

Esto obliga a un cambio de mentalidad que vas a usar durante todo el resto del curso: dejas de escribir "haz esto, espera, haz lo otro" y empiezas a escribir "en cada vuelta, mira en qué estado estoy y si ya toca cambiar". Es la semilla de las máquinas de estados.

El patrón concreto necesita tres variables que sobreviven entre vueltas del `loop()` (por eso se declaran fuera, como globales):

```cpp
int lecturaAnterior = HIGH;        // la última lectura CRUDA del pin
int estadoEstable   = HIGH;        // el estado ya filtrado, el que te crees
unsigned long tUltimoCambio = 0;   // cuándo cambió la lectura cruda por última vez
```

Y la mecánica es esta: si la lectura cruda de este instante es distinta de la de la vuelta anterior, algo se ha movido, así que reinicias el cronómetro. Si, en cambio, la lectura lleva más de 50 ms sin cambiar, te la crees y la copias a `estadoEstable`. Durante una ráfaga de rebotes el cronómetro se reinicia continuamente y nunca llega a los 50 ms; en cuanto el contacto se asienta, el cronómetro corre limpio y el cambio se acepta una sola vez.

Fíjate en que `tUltimoCambio` es `unsigned long` y no `int`. `millis()` devuelve un contador que crece sin parar y que en un `int` de 16 bits se desbordaría en 32 segundos. Con `unsigned long` tardas casi 50 días, y además la resta `millis() - tUltimoCambio` sigue dando el resultado correcto incluso cuando el contador da la vuelta, siempre que ambas variables sean del mismo tipo sin signo.

### Nivel contra flanco

La última idea del módulo, y la más valiosa a largo plazo.

`digitalRead` te da un **nivel**: cómo está el pin *ahora*. Pero muchas veces lo que te interesa no es el nivel sino el **flanco**: el instante exacto en que el nivel cambia.

| Concepto | Pregunta que responde | Cuánto dura |
|---|---|---|
| Nivel `LOW` | ¿el botón **está** pulsado? | todo el tiempo que lo mantengas |
| Flanco de bajada | ¿el botón **se acaba de** pulsar? | un solo instante |

La diferencia es la que hay entre "la puerta está abierta" y "la puerta se acaba de abrir". Si cuentas niveles, un `loop()` que da diez mil vueltas por segundo te suma diez mil por cada segundo que mantengas el dedo encima. Si cuentas flancos, te suma uno.

Detectar un flanco no requiere nada nuevo: ya tienes el estado anterior guardado. Un flanco de bajada es sencillamente "el estado filtrado ha cambiado **y** el valor nuevo es `LOW`". Con `INPUT_PULLUP`, el flanco de bajada es el momento de pulsar y el de subida el de soltar.

Y una vez que sabes detectar el instante de la pulsación, puedes hacer lo que quieras en él: incrementar un contador (ejercicio 03) o invertir una variable que recuerda si el LED debe estar encendido (ejercicio 04). El esqueleto es el mismo; lo único que cambia son las dos o tres líneas de dentro.

---

## Worked example: el esqueleto que se repite en todo el módulo

A partir del ejercicio 02 los tres programas son el mismo con el relleno cambiado. Merece la pena aprenderse este bloque, porque lo vas a escribir muchas veces en tu vida:

```cpp
const int PIN_BOTON = 2;
const unsigned long ANTIRREBOTE = 50;   // ms que la señal debe mantenerse estable

int lecturaAnterior = HIGH;             // última lectura cruda
int estadoEstable   = HIGH;             // estado ya filtrado
unsigned long tUltimoCambio = 0;

void setup() {
    pinMode(PIN_BOTON, INPUT_PULLUP);
}

void loop() {
    int lectura = digitalRead(PIN_BOTON);

    if (lectura != lecturaAnterior) {   // se movió algo: reinicia el cronómetro
        tUltimoCambio = millis();
        lecturaAnterior = lectura;
    }

    if ((millis() - tUltimoCambio) > ANTIRREBOTE) {   // lleva 50 ms quieta
        if (lectura != estadoEstable) {               // y además es distinta de la que creía
            estadoEstable = lectura;                  // FLANCO
            if (estadoEstable == LOW) {
                // aquí va lo tuyo: contar, conmutar, arrancar algo...
            }
        }
    }
}
```

Léelo por partes. El primer `if` es el cronómetro: cada vez que la lectura cruda cambia, vuelve a cero. El segundo `if` es el filtro: solo pasan las lecturas que llevan quietas más de `ANTIRREBOTE` milisegundos. El tercer `if` es la detección de flanco: la lectura filtrada difiere del estado que teníamos guardado, así que ha habido un cambio real, y lo apuntamos. El cuarto `if` selecciona **qué** flanco nos interesa; con `INPUT_PULLUP`, `LOW` es pulsar.

Ese anidamiento no es casual: cada nivel descarta un tipo de falso positivo. Sin el segundo, cuentas rebotes. Sin el tercero, cuentas niveles. Sin el cuarto, cuentas también las veces que sueltas.

---

## Errores típicos

- **Esperar `HIGH` al pulsar.** Con `INPUT_PULLUP` es al revés: `LOW` es pulsado. Si el LED va "al contrario", es esto casi seguro.
- **Usar `INPUT` en vez de `INPUT_PULLUP`** sin poner resistencia externa. El pin flota y las lecturas son erráticas: parece que el programa hace cosas solo.
- **Cablear el botón por el par equivocado.** Las patillas de un mismo lado están unidas siempre, así que el programa ve el botón pulsado desde el arranque. Usa patillas en diagonal.
- **Contar el nivel en vez del flanco.** Un solo clic suma miles. Hay que comparar con el estado anterior, no mirar solo si el pin está `LOW`.
- **Antirrebotar con `delay(50)`.** Funciona pero congela la placa; en cuanto haya algo más que atender, se rompe. Usa `millis()`.
- **Declarar las variables de estado dentro del `loop()`.** Se reinician en cada vuelta y el filtro no filtra nada. Van fuera, como globales (o `static`).
- **Guardar `millis()` en un `int`.** Se desborda a los 32 segundos y el antirrebote se vuelve loco. Siempre `unsigned long`.
- **Olvidar `Serial.begin(9600)`** o abrir el Monitor Serie a otra velocidad. O no ves nada, o ves caracteres basura.

---

## Preguntas para pensar

- ¿Qué lee exactamente un pin de entrada al que no has conectado nada, y por qué no lee siempre lo mismo?
- ¿Por qué la resistencia de pull-up es de decenas de kΩ y no de 220 Ω, como la del LED?
- ¿Cuál es la diferencia entre "el botón está pulsado" y "el botón se acaba de pulsar"? ¿Cuál de las dos necesitas para contar?
- En el toggle, ¿por qué la variable que recuerda si el LED está encendido tiene que declararse fuera del `loop()`?
- Si subes `ANTIRREBOTE` a 500 ms, ¿qué deja de funcionar? ¿Y si lo bajas a 1 ms?
- ¿Cómo detectarías el flanco de **subida** (el momento de soltar) en vez del de bajada? ¿Para qué serviría?

---

## Ejercicios

- [[Curso_Arduino/practica/02-entradas-digitales/ej01|Ej 01 — LED encendido mientras se pulsa el botón (verde)]]
- [[Curso_Arduino/practica/02-entradas-digitales/ej02|Ej 02 — Antirrebote por software con millis() (verde)]]
- [[Curso_Arduino/practica/02-entradas-digitales/ej03|Ej 03 — Contador de pulsaciones por Serial (amarillo)]]
- [[Curso_Arduino/practica/02-entradas-digitales/ej04|Ej 04 — Toggle: el botón como interruptor (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/01-fundamentos]]
- Módulo siguiente: [[Curso_Arduino/modelo/03-salidas-analogicas-pwm]]
