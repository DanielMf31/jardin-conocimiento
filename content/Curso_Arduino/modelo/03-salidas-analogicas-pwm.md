---
title: "Módulo 03 — Salidas analógicas (PWM)"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/pwm, electronica/led-rgb, programacion/fundamentos]
aliases: [pwm-arduino, analogWrite, duty-cycle, led-rgb-arduino, map-arduino, modulo-03-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/03-salidas-analogicas-pwm.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/03-salidas-analogicas-pwm.md (se regenera con gen_course.py). -->

# Módulo 03 — Salidas analógicas (PWM)

## Idea central

Un pin digital sigue sin saber dar "medio voltio": solo sabe 0 V o 5 V. Pero si lo enciendes y lo apagas cientos de veces por segundo, ni el LED ni tu ojo distinguen el parpadeo: perciben el **promedio**. Cambiando qué porcentaje del tiempo está encendido, obtienes cualquier brillo intermedio sin cambiar la tensión. Eso es **PWM**, y es la razón de que un pin de dos estados pueda comportarse como una salida analógica.

---

## Qué aprendes

- Qué es una señal PWM y qué significa su **duty cycle** (ciclo de trabajo).
- Usar `analogWrite(pin, valor)` con el rango **0..255**, y por qué es 255 y no 100.
- Identificar los pines **~** del Arduino UNO, los únicos con PWM por hardware.
- Hacer una rampa de brillo (*fade*) con un bucle `for`.
- Mezclar color en un LED RGB combinando tres salidas PWM.
- Reescalar rangos con `map()` para razonar en unidades cómodas (porcentaje) en vez de en cuentas.

---

## Explicación

### El problema: un pin solo tiene dos estados

En el módulo 01 el LED estaba encendido o apagado, y punto. Para atenuarlo, la intuición pide "bajar el voltaje a 2,5 V", pero un pin digital no tiene ningún circuito capaz de hacer eso: su etapa de salida es un par de interruptores que conectan el pin a 5 V o a GND. No hay estado intermedio.

La salida es cambiar de dimensión: en vez de jugar con la **tensión**, se juega con el **tiempo**.

### PWM y duty cycle

**PWM** (*Pulse Width Modulation*, modulación por ancho de pulso) es una señal cuadrada de frecuencia fija en la que lo único que varía es cuánto dura la parte alta de cada ciclo. Esa proporción es el **duty cycle**:

```
100% ─────────────────────  siempre en 5 V
 75% ▔▔▔▔▔_▔▔▔▔▔_▔▔▔▔▔_
 50% ▔▔▔__▔▔▔__▔▔▔__▔▔▔__
 25% ▔____▔____▔____▔____
  0% _____________________  siempre en 0 V
```

Cada ciclo dura siempre lo mismo; lo que cambia es dónde está el escalón. Con un 50 % de duty cycle, el LED recibe de media la mitad de la energía y se ve a medio brillo. No está "a 2,5 V" en ningún instante: está a 5 V la mitad del tiempo y a 0 V la otra mitad.

La frecuencia es lo bastante alta para que el parpadeo sea invisible. En el Arduino UNO los pines 3, 9, 10 y 11 conmutan a unos **490 Hz** y los pines 5 y 6 a unos **980 Hz**. A 490 Hz, cada ciclo dura poco más de 2 ms; el ojo humano integra cualquier cosa por encima de unos 60 Hz, así que ve luz continua y estable.

Conviene tener claro que el promedio lo hace el receptor, no el pin. Un LED y un ojo promedian estupendamente; un altavoz o un motor también, por inercia. Un instrumento rápido, en cambio, vería la onda cuadrada tal cual, porque ahí sigue estando.

### analogWrite y el rango 0..255

```cpp
analogWrite(pin, valor);   // valor entre 0 y 255
```

El nombre engaña un poco: `analogWrite` no genera una tensión analógica, genera PWM. El segundo argumento es el duty cycle expresado en **8 bits**, es decir 256 niveles distintos:

| Valor | Duty cycle | Qué se ve |
|---|---|---|
| `0` | 0 % | apagado |
| `64` | 25 % | brillo bajo |
| `128` | 50 % | medio brillo |
| `191` | 75 % | brillo alto |
| `255` | 100 % | máximo, equivale a `digitalWrite(pin, HIGH)` |

De aquí sale la confusión más repetida del módulo: `analogWrite(LED, 100)` no es el 100 %, es un 39 % largo. El techo es **255**, no 100. Para pasar de porcentaje a cuentas, la regla de tres es `valor = 255 * pct / 100`.

El pin sigue necesitando su `pinMode(pin, OUTPUT)` en `setup()`. PWM es una forma de accionar una salida, no un modo de pin distinto.

### Los pines ~

`analogWrite` solo produce PWM real en los pines que llevan una **tilde `~`** serigrafiada en la placa. En el Arduino UNO son seis:

```
~3   ~5   ~6   ~9   ~10   ~11
```

Son los pines conectados a los temporizadores internos del microcontrolador, que son quienes generan la onda cuadrada por hardware, sin que el programa tenga que hacer nada. En cualquier otro pin, `analogWrite` compila sin protestar y no da ningún error: simplemente pone el pin a LOW si el valor es menor que 128 y a HIGH si es 128 o más. El resultado es un LED que enciende y apaga a saltos en vez de atenuarse, y como no hay mensaje de error, es un fallo que cuesta encontrar si no sospechas del pin.

### Rampas: PWM dentro de un bucle

Un valor fijo de PWM da un brillo fijo. Para que el brillo **cambie**, hay que ir escribiendo valores sucesivos, y eso pide un bucle:

```cpp
for (int brillo = 0; brillo <= 255; brillo++) {
    analogWrite(LED, brillo);
    delay(8);
}
```

El `for` recorre los 256 niveles de uno en uno y el `delay` decide cuánto se ve cada escalón. Los dos números mandan cosas distintas: el paso del bucle controla la **suavidad** y el `delay` controla la **duración** total. Con 256 pasos de 8 ms, la rampa entera tarda unos dos segundos. Bajando el `delay` la rampa es igual de suave pero más rápida; subiendo el paso del `for` es igual de rápida pero se ven escalones.

### Mezcla de color: tres PWM a la vez

Un LED RGB no es un LED que cambie de color: son tres LEDs (rojo, verde y azul) metidos en la misma cápsula y con una patilla común. Si cada uno recibe su propio PWM, el ojo suma las tres luces y ve un solo color. Es **mezcla aditiva**, la misma de una pantalla, y no se comporta como mezclar pinturas:

| R | G | B | Color |
|---|---|---|---|
| 255 | 0 | 0 | rojo |
| 0 | 255 | 0 | verde |
| 0 | 0 | 255 | azul |
| 255 | 255 | 0 | amarillo |
| 0 | 255 | 255 | cian |
| 255 | 0 | 255 | magenta |
| 255 | 255 | 255 | blanco |

Rojo a tope más verde a tope da **amarillo**, no naranja: el naranja es rojo a tope con el verde a media potencia, algo como `(255, 128, 0)`. Y los tres a tope dan blanco, porque sumar las tres primarias de luz es exactamente lo que hace la luz blanca.

### map(): pensar en las unidades que quieres

Trabajar en cuentas de 0 a 255 es incómodo porque no es la unidad en la que piensas. `map()` traduce un valor de un rango a otro:

```cpp
int pwm = map(pct, 0, 100, 0, 255);   // 0..100 % -> 0..255 cuentas
```

La firma es `map(valor, deMin, deMax, aMin, aMax)`: primero el rango de **origen**, luego el de **destino**. Invertir esos dos pares es el error clásico y no da fallo de compilación, solo resultados absurdos.

`map` trabaja con enteros y **trunca**: `map(50, 0, 100, 0, 255)` da 127, no 127,5. Por eso el "50 %" a veces aparece como 127 y a veces como 128 según cómo lo calcules; la diferencia es una cuenta de 256 y no se ve. Lo que sí importa es que `map` te deja escribir el programa en la unidad del problema (porcentaje, grados, centímetros) y dejar la conversión en un solo sitio. Es una función que vas a reutilizar en todo el curso, sobre todo en el módulo siguiente, cuando el valor a reescalar venga de un potenciómetro y llegue en el rango 0..1023.

---

## El montaje

Para casi todo el módulo basta con lo del módulo 01, cambiando de pin: **un LED con su resistencia de 220 Ω en el pin 9**, que es uno de los pines `~`.

```
UNO pin ~9 ──[ 220Ω ]──►|── GND
                         LED
                  (▲ patilla larga = ánodo hacia la resistencia)
```

La resistencia **no se puede omitir por ser PWM**. Es una tentación razonable ("si de media pasa menos corriente..."), pero falsa: durante cada pulso el pin está a 5 V completos, y el pico de corriente es el mismo que sin PWM. Lo que baja es la media, no el pico.

Para el LED RGB hacen falta tres pines PWM y **tres resistencias**, una por color:

```
UNO pin ~9  ──[ 220Ω ]──►|─┐  (rojo)
UNO pin ~10 ──[ 220Ω ]──►|─┤  (verde)      patilla común (la más larga) ── GND
UNO pin ~11 ──[ 220Ω ]──►|─┘  (azul)
```

Poner una sola resistencia en la patilla común parece ahorrar dos componentes y estropea el resultado: los tres colores compartirían la limitación de corriente y el brillo de cada uno dependería de cuántos estén encendidos, así que el amarillo saldría más apagado que el rojo. Cada color, su resistencia.

El otro detalle del RGB es de qué tipo es. En un **cátodo común** la patilla larga va a **GND** y la lógica es la natural: 0 apagado, 255 máximo. En un **ánodo común** esa patilla va a **5 V** y todo se invierte: 255 apaga y 0 enciende a tope. Si montas los colores al revés o el LED no enciende de ninguna manera, ese suele ser el motivo. Los ejercicios y las simulaciones de Wokwi de este módulo usan cátodo común.

Lo que necesitas por puesto: la placa UNO con su cable USB, una protoboard, un LED de 5 mm, un LED RGB de cátodo común, hasta tres resistencias de 220 Ω y unos ocho cables Dupont macho-macho. Si no tienes el kit físico, cada ejercicio trae su montaje ya hecho en Wokwi, dentro de `wokwi/<ej>/`.

---

## Worked example: medio brillo y rampa

```cpp
const int LED = 9;               // pin con ~, imprescindible para que haya PWM

void setup() {
    pinMode(LED, OUTPUT);        // PWM también necesita el pin declarado como salida
}

void loop() {
    analogWrite(LED, 128);       // 50% de duty cycle -> medio brillo
    delay(1000);

    for (int brillo = 0; brillo <= 255; brillo++) {
        analogWrite(LED, brillo);
        delay(4);                // 256 pasos * 4 ms ~ 1 s de rampa
    }
}
```

Léelo como una frase: *prepara el pin 9 como salida; luego, para siempre: ponlo a medio brillo un segundo y después súbelo desde apagado hasta el máximo en un segundo*.

Fíjate en el contraste entre las dos mitades del `loop()`. La primera escribe **un** valor y el brillo se queda ahí: PWM es un estado, no un evento, y el pin sigue conmutando solo hasta que le digas otra cosa. La segunda escribe 256 valores seguidos: el movimiento no lo hace `analogWrite`, lo hace el bucle. Y cuando el `for` acaba, el LED se queda al máximo hasta que el `loop()` vuelve a empezar y lo baja de golpe a 128; ese salto brusco se ve, y es justo lo que se corrige haciendo también la rampa de bajada.

---

## Errores típicos

- **Usar un pin sin `~`** (el 7 o el 8, por ejemplo) con `analogWrite`. No hay error de compilación: el LED simplemente enciende y apaga a saltos en vez de atenuarse.
- **Confundir el rango.** `analogWrite(LED, 100)` no es el 100 %, es un 39 %. El máximo es 255.
- **Quitar la resistencia "porque es PWM".** Los picos siguen siendo a 5 V; lo único que baja es la corriente media.
- **Una sola resistencia en el común del RGB.** El brillo de cada color pasa a depender de cuántos estén encendidos y las mezclas salen mal.
- **Confundir cátodo común con ánodo común.** Con el tipo equivocado, o no enciende, o 0 y 255 hacen lo contrario de lo que esperas.
- **Olvidar `pinMode(pin, OUTPUT)`.** PWM no exime de declarar la salida.
- **Invertir los rangos de `map()`.** `map(pct, 0, 255, 0, 100)` compila igual y devuelve valores sin sentido; el rango de origen va primero.
- **Esperar naranja de `color(255, 255, 0)`.** Eso es amarillo. El naranja necesita el verde a media potencia.

---

## Preguntas para pensar

- Si el LED se enciende y se apaga 490 veces por segundo, ¿por qué no lo ves parpadear? ¿Qué pasaría a 5 Hz?
- ¿Qué valor de `analogWrite` corresponde exactamente al 50 %? ¿Por qué la respuesta es incómoda con 256 niveles?
- El PWM no cambia la tensión del pin en ningún momento. Entonces, ¿dónde ocurre realmente el "promedio"?
- ¿Qué ventaja tiene `map(pct, 0, 100, 0, 255)` frente a escribir `255 * pct / 100` a mano? ¿Y qué desventaja?
- En una rampa, ¿qué cambia si tocas el paso del `for` y qué cambia si tocas el `delay`?
- ¿Y si el valor del brillo no lo eligieras tú en el código, sino que viniera de un potenciómetro?

---

## Ejercicios

- [[Curso_Arduino/practica/03-salidas-analogicas-pwm/ej01|Ej 01 — Fade de un LED con un bucle for (verde)]]
- [[Curso_Arduino/practica/03-salidas-analogicas-pwm/ej02|Ej 02 — Cuatro niveles fijos de brillo (verde)]]
- [[Curso_Arduino/practica/03-salidas-analogicas-pwm/ej03|Ej 03 — LED RGB: mezcla de colores (amarillo)]]
- [[Curso_Arduino/practica/03-salidas-analogicas-pwm/ej04|Ej 04 — De porcentaje a PWM con map() (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/02-entradas-digitales]]
- Módulo siguiente: [[Curso_Arduino/modelo/04-entradas-analogicas]]
