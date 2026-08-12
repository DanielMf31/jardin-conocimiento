---
title: "Módulo 04 — Entradas analógicas"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/adc, electronica/sensores, electronica/divisor-tension]
aliases: [analogRead, ADC Arduino, potenciometro Arduino, LDR Arduino, divisor de tension, modulo-04-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/04-entradas-analogicas.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/04-entradas-analogicas.md (se regenera con gen_course.py). -->

# Módulo 04 — Entradas analógicas

## Idea central

Hasta ahora la placa solo sabía preguntarle al mundo una cosa: ¿hay tensión en este pin o no? Un pin analógico pregunta algo mucho más rico: **¿cuánta tensión hay?**. Dentro del microcontrolador hay un **ADC** (conversor analógico-digital) que mide la tensión de un pin entre 0 y 5 V y la traduce a un número entero entre 0 y 1023. Con eso, un mando que se gira, un sensor de luz o cualquier magnitud continua del mundo real se convierte en un número que el programa puede comparar, escalar y usar para decidir.

---

## Qué aprendes

- Qué es el ADC del Arduino UNO, por qué su rango es 0-1023 y qué precisión tiene cada paso.
- Leer un pin analógico con `analogRead` y por qué no necesita `pinMode`.
- No confundir `analogRead` (entrada, 0-1023) con `analogWrite` (salida PWM, 0-255), que se parecen en el nombre y hacen cosas opuestas.
- Usar `map()` para reescalar el rango del ADC al rango que necesite otra pieza del sistema.
- Por qué un sensor resistivo como una LDR **no se puede leer solo** y necesita un **divisor de tensión**.
- Tomar decisiones con un **umbral**, y calibrarlo mirando datos reales en vez de a ojo.

---

## Explicación

### El pin analógico mide tensión

Un pin digital tiene dos estados y nada más: HIGH (5 V) o LOW (0 V). Un pin analógico no tiene estados, tiene una **rampa**: puede distinguir 3,1 V de 3,2 V. El Arduino UNO tiene seis de estos pines, etiquetados **A0 a A5**, y solo ellos pueden hacer esta medida.

Es importante fijar bien lo que se mide: **tensión, y solo tensión**. Un pin analógico no mide resistencia, ni luz, ni temperatura, ni fuerza. Todo lo que quieras medir tiene que llegar al pin convertido en un valor de tensión entre 0 y 5 V. Esa frase parece de manual, pero es la que explica el montaje de la LDR más abajo, que es el concepto duro del módulo.

### El ADC: de voltios a un número

La pieza que hace la traducción se llama **ADC**, *Analog to Digital Converter*. El del UNO es de **10 bits**, lo que significa que reparte el rango de entrada en 2^10 = **1024 escalones**, numerados del 0 al 1023.

| Tensión en el pin | Valor que devuelve `analogRead` |
|---|---|
| 0 V | 0 |
| 1,25 V | ≈ 256 |
| 2,5 V | ≈ 512 |
| 5 V | 1023 |

Cada escalón vale 5 V / 1024 ≈ **4,9 mV**. Ese es el límite de resolución: dos tensiones que se diferencien en menos de 5 milivoltios darán el mismo número. Para un potenciómetro o una LDR sobra de largo.

Que el máximo sea 1023 y no 1024 despista al principio. No es un fallo: con 1024 valores distintos empezando en el 0, el último es el 1023, igual que en una calle con 1024 portales numerados desde el 0 el último es el 1023.

### analogRead

```cpp
int valor = analogRead(A0);   // 0..1023 según la tensión que haya en A0
```

Dos detalles que conviene tener claros:

- **No hace falta `pinMode(A0, INPUT)`.** Los pines analógicos ya están preparados para leer; ponerlo no molesta y no rompe nada, pero no cambia nada. El contraste con `digitalWrite`, que sí exige su `pinMode(pin, OUTPUT)`, tiene sentido: para *sacar* corriente hay que configurar el pin como salida, porque por defecto no lo es. Para *medir*, no hay nada que configurar.
- **La lectura tarda algo**, unos 100 microsegundos. En la práctica es despreciable, pero explica por qué no tiene sentido leer un sensor un millón de veces por segundo.

### analogRead frente a analogWrite

Los nombres se parecen tanto que se confunden constantemente, y hacen cosas opuestas:

| | `analogRead(pin)` | `analogWrite(pin, valor)` |
|---|---|---|
| Dirección | entrada: la placa mide | salida: la placa genera |
| Rango | devuelve 0-1023 | recibe 0-255 |
| Pines | A0-A5 | los digitales con `~` (3, 5, 6, 9, 10, 11) |
| Qué es de verdad | una medida de tensión real | PWM: pulsos rápidos que *simulan* una tensión media |

La asimetría de rangos (1023 frente a 255) no es un capricho: el ADC es de 10 bits y el PWM del UNO es de 8 bits. Por eso, en cuanto quieres que una lectura analógica controle una salida PWM, hay que reescalar.

### map(): reescalar rangos

```cpp
int brillo = map(valor, 0, 1023, 0, 255);
```

`map()` toma un número de un rango de origen y devuelve el número equivalente en un rango de destino, manteniendo la proporción: 0 sigue siendo 0, 1023 pasa a 255, y la mitad del primero es la mitad del segundo. Se lee de izquierda a derecha como *"coge `valor`, que va de 0 a 1023, y llévalo al rango de 0 a 255"*.

¿Por qué no meter el 0-1023 directamente en `analogWrite`? Porque `analogWrite` solo entiende hasta 255. Todo lo que le pases por encima se comporta de forma indeseada y, sobre todo, pierdes el control: el LED llegaría al máximo brillo con el potenciómetro a un cuarto de recorrido y no cambiaría nada en los otros tres cuartos. `map()` reparte el recorrido completo del mando sobre el rango completo del brillo.

Un detalle útil: los rangos de `map()` pueden ir al revés. `map(valor, 0, 1023, 255, 0)` invierte el sentido, de modo que girar el mando hacia un lado bajaría el brillo en vez de subirlo. También hay que aceptar que `map()` con enteros pierde información al reducir 1024 valores a 256: cuatro lecturas consecutivas del ADC dan el mismo brillo. Es inevitable y no se nota.

### El divisor de tensión: por qué la LDR no se lee sola

Aquí está la idea que separa "copiar un montaje" de "entender lo que estás haciendo".

Una **LDR** (fotorresistor) es una resistencia que cambia de valor con la luz: a oscuras puede tener cientos de miles de ohmios, con luz directa unos pocos cientos. El problema es evidente en cuanto juntas las dos frases del módulo: la LDR informa cambiando su **resistencia**, y el pin analógico solo sabe medir **tensión**. Falta un traductor.

Ese traductor es el **divisor de tensión**: dos resistencias en serie entre 5 V y GND, con el pin conectado al nodo intermedio.

```
5V ──[ LDR ]──┬──[ 10 kΩ ]── GND
              │
              A0
```

La tensión en el nodo central depende de cómo se reparten las dos resistencias los 5 V:

```
V(A0) = 5V · R_fija / (R_LDR + R_fija)
```

Con mucha luz, la LDR baja su resistencia, se "queda" con una parte pequeña de los 5 V y en A0 aparece una tensión **alta**, o sea un `analogRead` **alto**. A oscuras, la LDR sube su resistencia, se lleva casi todos los voltios y en A0 queda una tensión **baja**. Con este cableado, más luz significa número más grande. Si intercambias la LDR y la resistencia fija, el sentido se invierte: es una decisión de montaje, no una propiedad del sensor, y por eso siempre hay que comprobar hacia dónde se mueve el número antes de escribir el `if`.

Si quitas la resistencia de 10 kΩ, el pin A0 se queda conectado solo a la LDR y sin camino a GND: es lo que se llama una **entrada flotante**. No hay ningún circuito que fije su tensión, así que el ADC lee interferencias del ambiente y devuelve números que bailan sin sentido, a veces incluso reaccionando a que acerques la mano. Ese es el error conceptual clave del módulo: no es que "falte una resistencia de protección", es que **sin la segunda resistencia no hay nada que medir**.

El potenciómetro, en cambio, ya es un divisor de tensión de fábrica, y ajustable: sus dos extremos van a 5 V y GND, y el cursor central se desliza por la pista resistiva entregando cualquier tensión intermedia. Por eso no lleva resistencia adicional. Un potenciómetro y una LDR con su resistencia fija son, desde el punto de vista del pin, exactamente lo mismo.

### Decidir con un umbral

Leer un número está bien, pero lo que suele querer un sistema es actuar. La forma más simple es comparar contra un valor de corte:

```cpp
const int UMBRAL = 400;
if (luz < UMBRAL) {
    // está oscuro
} else {
    // hay luz
}
```

El umbral **no se elige de memoria**: depende del sensor, de la resistencia fija y de la iluminación de la habitación. La forma correcta de fijarlo es empírica: imprime el valor por Serial, tapa el sensor y anota el número, ilumínalo y anota el otro, y elige un valor cómodo entre ambos. Un umbral copiado de otro montaje casi nunca funciona en el tuyo.

Si el sensor se queda justo en el borde, la salida oscila encendiéndose y apagándose sin parar. La solución profesional se llama **histéresis** (usar un umbral para encender y otro distinto, más separado, para apagar), y aunque este módulo no la implementa, merece la pena saber que el problema tiene nombre.

---

## El montaje

Todo el módulo se monta sobre protoboard con muy pocas piezas: un **potenciómetro de 10 kΩ**, una **LDR**, una **resistencia de 10 kΩ** para su divisor, un **LED** con su **resistencia de 220 Ω** y unos ocho cables.

- **Potenciómetro**: tiene tres patillas. Las dos de los extremos van a **5 V** y **GND** (da igual cuál a cuál: solo cambia el sentido de giro), y la **central**, el cursor, va a **A0**. No lleva ninguna resistencia extra.
- **LDR**: `5V → LDR → nodo → R 10 kΩ → GND`, y el **nodo central a A0**. La LDR no tiene polaridad, da igual cómo la orientes. La resistencia de 10 kΩ es obligatoria por lo explicado arriba.
- **LED de brillo variable** (ejercicio 02): pin **9**, que es uno de los pines con `~` y por tanto capaz de PWM, en serie con **220 Ω** hacia el **ánodo** (patilla larga); el **cátodo** a GND. Si lo pones en un pin sin `~`, `analogWrite` no regulará el brillo.
- **LED indicador** (ejercicio 04): pin **8** con su **220 Ω** y su vuelta a GND. Aquí solo se enciende y se apaga, así que no necesita PWM.

En el simulador Wokwi la LDR aparece como el módulo `wokwi-photoresistor-sensor`, que ya lleva la resistencia del divisor integrada en la placa del sensor: solo cableas VCC a 5 V, GND a GND y AO a A0. Eso es cómodo, pero esconde justo el concepto del módulo. En protoboard física el divisor lo montas tú.

---

## Worked example: el potenciómetro por Serial

```cpp
const int PIN_POT = A0;   // pin analógico donde lee el cursor del potenciómetro

void setup() {
    Serial.begin(9600);   // abrir el puerto serie a 9600 baudios
}

void loop() {
    int valor = analogRead(PIN_POT);  // 0..1023 según la tensión en A0 (0V..5V)
    Serial.print("Pot: ");
    Serial.println(valor);
    delay(200);                       // no saturar el Serial Monitor
}
```

Léelo como una frase: *prepara el puerto serie; luego, para siempre: mide la tensión de A0, dime qué número ha salido y espera un poco*.

Hay tres decisiones pequeñas que conviene ver. `Serial.begin(9600)` va en `setup()` porque abrir el canal es preparación, se hace una vez. `Serial.print` escribe sin salto de línea y `Serial.println` escribe y salta, de forma que la etiqueta y el número aparecen juntos en una misma fila. Y el `delay(200)` no está ahí por el sensor, que podría leerse mil veces más rápido, sino por ti: sin él, el Serial Monitor se llena de cinco mil líneas por segundo y no puedes leer nada.

Este programa de once líneas es la herramienta de diagnóstico más útil del módulo. Antes de escribir cualquier `if` con un umbral, lo primero es siempre esto: sacar el número por Serial y mirar cómo se mueve de verdad.

---

## Errores típicos

- **Montar la LDR sin la resistencia fija.** A0 queda flotante y las lecturas son ruido. No es un olvido menor: sin divisor no hay tensión que medir.
- **Confundir `analogRead` con `analogWrite`.** Nombres parecidos, direcciones opuestas y rangos distintos (0-1023 frente a 0-255).
- **Meter el 0-1023 directamente en `analogWrite`.** El brillo satura en el primer cuarto del recorrido del mando. Hay que pasar por `map()`.
- **Poner el LED de brillo en un pin sin `~`.** `analogWrite` sobre un pin no-PWM no regula: el LED se comporta como si fuera digital.
- **Invertir los rangos de `map()` sin querer.** El mando funciona al revés. Revisa el orden de los cuatro números.
- **Fijar el umbral a ojo.** Primero observa los valores reales en el Serial y luego elige el corte.
- **Suponer que más luz siempre da un número mayor.** Depende de cómo hayas ordenado la LDR y la resistencia en el divisor. Compruébalo.
- **Leer sin ningún `delay`.** El Serial Monitor se vuelve ilegible aunque el programa sea correcto.

---

## Preguntas para pensar

- ¿Por qué `analogRead` no necesita `pinMode` y `digitalWrite` sí?
- Si el ADC es de 10 bits, ¿cuántos valores distintos hay y cuántos voltios vale un escalón?
- ¿Qué leerías en A0 si conectaras la LDR sin la resistencia de 10 kΩ, y por qué?
- ¿Qué pasa si intercambias la LDR y la resistencia fija en el divisor?
- ¿Por qué en el ejercicio 02 hace falta `map()` y no basta con pasar la lectura tal cual?
- Si el sensor se queda justo en el umbral, la salida parpadea sin parar. ¿Cómo lo evitarías?
- Con 1023 escalones para todo el recorrido de un potenciómetro, ¿cuántos grados de giro hay entre dos números consecutivos?

---

## Ejercicios

- [[Curso_Arduino/practica/04-entradas-analogicas/ej01|Ej 01 — Leer un potenciómetro por Serial (verde)]]
- [[Curso_Arduino/practica/04-entradas-analogicas/ej02|Ej 02 — El potenciómetro regula el brillo de un LED (verde)]]
- [[Curso_Arduino/practica/04-entradas-analogicas/ej03|Ej 03 — Leer una LDR con divisor de tensión (verde)]]
- [[Curso_Arduino/practica/04-entradas-analogicas/ej04|Ej 04 — Umbral de oscuridad: LED automático (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/03-salidas-analogicas-pwm]]
- Módulo siguiente: [[Curso_Arduino/modelo/05-comunicacion-serie]]
