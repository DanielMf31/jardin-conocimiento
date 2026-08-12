---
title: "Módulo 06 — Sensores comunes"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/sensores, electronica/librerias, programacion/fundamentos]
aliases: [sensores-arduino, DHT22, HC-SR04, PIR, pulseIn, librerias-arduino, modulo-06-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/06-sensores-comunes.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/06-sensores-comunes.md (se regenera con gen_course.py). -->

# Módulo 06 — Sensores comunes

## Idea central

Un sensor convierte una magnitud del mundo físico —temperatura, distancia, movimiento— en algo que el microcontrolador puede leer. Lo que cambia de un sensor a otro no es la magnitud: es **la forma en que te entrega el dato**. Unos te dan un voltaje, otros un simple HIGH o LOW, y otros una secuencia de bits con su propio protocolo. Aprender sensores no es memorizar sensores, es reconocer a cuál de esas tres familias pertenece el que tienes delante, porque de eso depende todo el código que vas a escribir.

---

## Qué aprendes

- Las tres maneras en que un sensor puede entregar su dato, y cómo se lee cada una.
- Qué es una librería, por qué el DHT22 necesita una y el PIR no, y cómo se instala.
- Leer temperatura y humedad con un DHT22, incluyendo qué hacer cuando la lectura falla.
- Medir distancia por tiempo de vuelo con un HC-SR04 usando `pulseIn`, sin ninguna librería.
- Detectar presencia con un PIR y reaccionar con un actuador.
- Que cada sensor impone su propio ritmo: hay lecturas que no puedes pedir más rápido de lo que el sensor sabe darlas.

---

## Explicación

### Las tres formas de dar un dato

Todo lo que llega a la placa desde el exterior entra por un pin, y solo hay tres maneras de que entre:

| Familia | Qué llega al pin | Cómo se lee | Ejemplo de este módulo |
|---|---|---|---|
| Analógica | Un voltaje continuo entre 0 V y 5 V | `analogRead` (módulo 04) | LDR, potenciómetro |
| Digital simple | HIGH o LOW, y nada más | `digitalRead` | PIR |
| Protocolo propio | Una secuencia de bits con tiempos precisos | Una librería, o código de temporización a mano | DHT22 |

El HC-SR04 es un caso curioso que no encaja del todo en ninguna: entrega el dato en **la duración** de un pulso digital. El pin solo está en HIGH o en LOW, así que técnicamente es digital, pero la información no está en el valor sino en cuánto tiempo dura. Por eso no se lee con `digitalRead` sino con `pulseIn`.

Lo importante es el hábito: cuando te llegue un sensor nuevo, la primera pregunta no es "¿qué código escribo?" sino "¿en cuál de estas familias cae?". La hoja de características del sensor te lo dice en la primera página.

### Qué es una librería y por qué hace falta

Un DHT22 no te manda un voltaje proporcional a la temperatura. Cuando le pides una lectura, contesta con una ristra de 40 bits por un único cable, y cada bit se distingue del siguiente por **cuántos microsegundos** dura el pulso: un pulso corto significa 0, uno largo significa 1. Descifrar eso a mano significa escribir código que mide tiempos con precisión de microsegundos, cuenta bits, los agrupa en bytes y comprueba la suma de verificación. Es perfectamente posible, y es exactamente el tipo de trabajo que no quieres repetir cada vez que usas el sensor.

Una **librería** es código que ya escribió otra persona, empaquetado para que puedas usarlo sin leerlo. Alguien resolvió el problema del protocolo del DHT una vez, lo publicó, y tú te limitas a decir "dame la temperatura".

Usar una librería son dos pasos, y el segundo se olvida siempre:

1. **Instalarla.** En el Arduino IDE, `Herramientas > Gestionar bibliotecas`, buscar por nombre e instalar. Para el DHT22 hacen falta **dos**: `DHT sensor library` (de Adafruit) y `Adafruit Unified Sensor`, de la que depende la primera. En Wokwi se declaran en el fichero `libraries.txt`.
2. **Incluirla** en el sketch: `#include <DHT.h>`.

Si haces solo el segundo, el compilador te contesta `DHT.h: No such file or directory`. Ese mensaje no significa que tu código esté mal: significa que el fichero de la librería no está en tu ordenador. Es el error número uno del módulo y tiene arreglo en veinte segundos.

Al revés también conviene entenderlo: el PIR **no** necesita librería porque no tiene protocolo. Su salida es un cable que está a 5 V cuando detecta movimiento y a 0 V cuando no. `digitalRead` y listo. Una librería no es una obligación ni un signo de sofisticación: aparece solo cuando el sensor habla un idioma que hay que traducir.

### DHT22: objeto, arranque y lecturas que fallan

El uso de la librería del DHT introduce una forma de escribir que verás mucho:

```cpp
#define DHTPIN  2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
```

Esa línea crea un **objeto**: una variable que no guarda un número, sino un sensor entero, con todo lo que hace falta para hablar con él. Al construirlo le dices las dos cosas que la librería no puede adivinar: en qué pin está conectado y de qué modelo es, porque la misma librería sirve para el DHT11 y para el DHT22, que se manejan igual pero tienen tiempos y precisiones distintas. A partir de ahí, todo lo que quieras del sensor se lo pides al objeto con un punto: `dht.begin()`, `dht.readHumidity()`, `dht.readTemperature()`.

El `dht.begin()` va en `setup()`, igual que el `Serial.begin(9600)`: es preparación que se hace una vez.

Y hay dos detalles del DHT22 que no son negociables:

**No se le puede pedir una lectura nueva más de una vez cada dos segundos.** El sensor tarda ese tiempo en medir. Si le preguntas antes, te contesta lo que puede, que normalmente es basura. Por eso el código pone `delay(2000)`.

**Cuando la lectura falla, no da un error: devuelve `NaN`.** `NaN` significa *Not a Number*, y es el valor especial que tiene un `float` cuando el número que debería contener no existe. Lo traicionero de `NaN` es que se propaga en silencio: si lo sumas, lo multiplicas o lo comparas, el resultado sigue siendo `NaN` o falso, y tú acabas viendo un `nan` por el Monitor Serie sin saber de dónde salió. Comprobarlo se hace con `isnan(valor)`, nunca con `valor == NaN` (esa comparación es falsa incluso cuando el valor *es* `NaN`).

### HC-SR04: medir distancia midiendo tiempo

El ultrasonidos no mide distancia. Mide **tiempo**, y la distancia se calcula. El sensor emite un chasquido de ultrasonido, ese sonido rebota en el primer objeto que encuentra y vuelve; el sensor cronometra ese viaje de ida y vuelta y te lo entrega.

Tiene dos pines de señal con papeles opuestos:

- `TRIG` es una **salida** de la placa: por ahí le ordenas que dispare. La orden es un pulso en HIGH de 10 microsegundos, ni más ni menos, así que se construye con `delayMicroseconds`.
- `ECHO` es una **entrada**: el sensor lo pone en HIGH desde que emite el chasquido hasta que recibe el eco. La duración de ese HIGH es la medida.

Para cronometrar el eco existe `pulseIn(ECHO, HIGH)`, que se queda esperando a que el pin se ponga en HIGH y devuelve **cuántos microsegundos** ha durado. Devuelve un `long` porque los microsegundos se acumulan rápido y no caben en un `int`.

De ahí sale la fórmula, que conviene deducir y no copiar. El sonido viaja a unos 340 metros por segundo, que pasado a las unidades que aquí interesan son **0,034 centímetros por microsegundo**. Si multiplicas los microsegundos medidos por esa velocidad obtienes los centímetros recorridos, pero ese recorrido es **el de ida y vuelta**: el sonido hizo dos veces el camino hasta el objeto. Por eso se divide entre 2.

```cpp
float distancia = duracion * 0.034 / 2;
```

Olvidar ese `/2` es un error precioso desde el punto de vista didáctico, porque el programa funciona: las lecturas suben y bajan coherentemente cuando acercas la mano. Solo que todas valen exactamente el doble. Un error que no rompe nada y solo se detecta comparando con una regla.

Merece la pena saber también que `pulseIn` es una función **bloqueante**: mientras espera el eco, la placa no hace nada más. Si no llega ningún eco (porque no hay ningún objeto delante, o está demasiado lejos), `pulseIn` acaba rindiéndose y devuelve `0`, lo que se traduce en una distancia de 0 cm que en realidad significa "infinito". Es la misma tensión que ya vimos con `delay` en el módulo 01, y una de las razones por las que un sensor de distancia no es tan inofensivo como parece.

### PIR: el sensor más simple del módulo

Un PIR (*Passive InfraRed*) detecta el calor en movimiento. Los cuerpos emiten radiación infrarroja; el sensor vigila su campo de visión y, cuando el patrón de calor cambia de sitio, lo interpreta como presencia. Es pasivo porque no emite nada: solo mira.

Todo el trabajo de decidir "esto es movimiento" ya lo ha hecho la electrónica del propio módulo. Lo que sale por su pin `OUT` es la conclusión, ya digerida: HIGH cuando hay movimiento, LOW cuando no. Desde el punto de vista del código, un PIR es indistinguible de un botón: `pinMode(PIR, INPUT)` y `digitalRead(PIR)`.

Dos peculiaridades físicas que sí conviene conocer, porque parecen bugs del programa y no lo son. La primera es el **calentamiento**: recién alimentado, el PIR necesita unas decenas de segundos para calibrar el nivel de infrarrojo de fondo de la habitación, y durante ese rato dispara falsos positivos. Si nada más subir el programa el LED se enciende solo, espera un poco antes de dudar del código. La segunda es que el PIR **mantiene su salida en HIGH un tiempo fijo** después de detectar, del orden de segundos, ajustable con los potenciómetros del módulo. No es un sensor instantáneo: si te mueves y te paras, la salida seguirá en HIGH un rato.

---

## El montaje

Los tres sensores de este módulo funcionan a **5 V** con el Arduino UNO, así que los tres comparten el mismo par de cables de alimentación: `VCC` al pin de 5 V de la placa y `GND` a GND. Lo que cambia de uno a otro son los cables de señal.

El material del módulo es: la placa UNO con su cable USB, una protoboard, un **DHT22**, un **HC-SR04**, un **PIR** (modelo HC-SR501), un LED de 5 mm con su resistencia de 220 Ω para el ejercicio 03, y una docena de cables Dupont macho-macho. Si no tienes el kit físico, cada ejercicio trae su montaje ya hecho en Wokwi dentro de `wokwi/<ej>/`.

Las conexiones, sensor a sensor:

```
DHT22   (ej01):   VCC → 5V     DATA → pin 2      GND → GND
HC-SR04 (ej02):   VCC → 5V     TRIG → pin 9      ECHO → pin 10     GND → GND
PIR     (ej03):   VCC → 5V     OUT  → pin 2      GND → GND
                  LED: pin 8 ──[220 Ω]──►|── GND
```

Tres avisos sobre el montaje:

**El DHT22 y el pull-up.** Un DHT22 "pelado", de cuatro patas, necesita una resistencia de unos 10 kΩ entre `DATA` y `VCC` para que la línea de datos se mantenga alta en reposo. La mayoría de los módulos que se venden montados en una placa pequeña ya la traen soldada y no hay que hacer nada; en Wokwi tampoco hace falta. Comprueba cuál de los dos tienes antes de dar por hecho que el sensor está roto.

**TRIG y ECHO no son intercambiables.** Uno es salida y otro es entrada. Si los cruzas, el programa compila, sube y funciona sin quejarse, pero las distancias salen siempre 0 o completamente erráticas. Cuando un HC-SR04 da 0 cm sin parar, mira los cables antes que el código.

**La resistencia del LED no se omite nunca**, tampoco aquí. El LED del ejercicio 03 lleva sus 220 Ω en serie como en el módulo 01.

Y una nota mirando adelante: en el ESP32, que trabaja a 3,3 V, esto no se copia tal cual. El `ECHO` del HC-SR04 saca 5 V y meterlos directamente a un GPIO de 3,3 V lo puede dañar, así que hará falta un divisor de tensión. Lo verás en el módulo 09.

---

## Worked example: leer un DHT22 sin fiarse de la lectura

```cpp
#include <DHT.h>

#define DHTPIN  2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    dht.begin();
}

void loop() {
    delay(2000);                                // el DHT22 no da lecturas más rápido

    float humedad     = dht.readHumidity();
    float temperatura = dht.readTemperature();

    if (isnan(humedad) || isnan(temperatura)) { // la lectura ha fallado
        Serial.println("Error leyendo el DHT22");
        return;                                 // salimos del loop; volverá a intentarlo
    }

    Serial.print("Temperatura: ");
    Serial.print(temperatura);
    Serial.print(" C   Humedad: ");
    Serial.print(humedad);
    Serial.println(" %");
}
```

Hay dos decisiones en este programa que van más allá del DHT22 y que vale la pena señalar.

La primera es que el `delay(2000)` está **al principio** del `loop()`, no al final. El efecto en régimen permanente es el mismo, porque el bucle es circular, pero ponerlo arriba garantiza que también hay una espera antes de la primerísima lectura, justo después de `dht.begin()`, cuando el sensor todavía se está despertando.

La segunda es el `return`. Cuando la lectura falla, no hay nada sensato que imprimir, así que se avisa y se abandona la vuelta actual del bucle. `return` dentro de `loop()` no termina el programa: termina **esta pasada** y devuelve el control a Arduino, que inmediatamente vuelve a llamar a `loop()`. Es una forma limpia de decir "aquí ya no hay nada que hacer" sin meter el resto del código dentro de un `else` que iría creciendo hacia la derecha.

---

## Errores típicos

- **No instalar la librería del DHT.** El compilador dice `DHT.h: No such file or directory` y no llega ni a subir. Hay que instalar `DHT sensor library` **y** `Adafruit Unified Sensor`.
- **Pedirle al DHT22 lecturas más rápidas de 2 s.** Devuelve `NaN` y por el Monitor Serie aparece `nan`. El `delay(2000)` no es decorativo.
- **No comprobar el `NaN`.** El programa no falla, pero imprime valores sin sentido que luego contaminan cualquier cálculo. Se comprueba con `isnan()`, nunca comparando con `==`.
- **Cruzar TRIG y ECHO.** Distancias de 0 cm o disparatadas, sin ningún mensaje de error.
- **Olvidar dividir entre 2** en la fórmula de distancia. Todas las medidas salen exactamente al doble y el programa parece funcionar perfectamente.
- **Dar por rota la lectura del ultrasonidos cuando devuelve 0.** Es lo que devuelve `pulseIn` al no recibir eco: significa "no hay nada delante", no "el sensor falla".
- **Impacientarse con el PIR recién encendido.** Los primeros segundos son de calibración y da falsos positivos.
- **Montar el LED del ejercicio 03 sin resistencia.** Los 220 Ω siguen siendo obligatorios.

---

## Preguntas para pensar

- ¿Por qué el DHT22 necesita una librería y el PIR no? ¿Qué tendría que cambiar en el PIR para que empezara a necesitar una?
- ¿De dónde sale el `0.034` de la fórmula del ultrasonidos? Compruébalo tú: pasa 340 m/s a cm/µs.
- Si el HC-SR04 no recibe ningún eco, `pulseIn` devuelve 0 y la distancia sale 0 cm. ¿Cómo distinguirías en el código "hay algo pegado al sensor" de "no hay nada delante"?
- ¿Qué verías por el Monitor Serie si leyeras el DHT22 cada 100 ms?
- `pulseIn` bloquea la placa mientras espera el eco. Si además quisieras atender un botón, ¿qué problema aparece? ¿Te suena de algún módulo anterior?
- Los tres ejercicios imprimen sus datos por serie y ahí se quedan. ¿Qué harías para guardarlos o enviarlos a otro sitio?

---

## Ejercicios

- [[Curso_Arduino/practica/06-sensores-comunes/ej01|Ej 01 — Temperatura y humedad con el DHT22 (verde)]]
- [[Curso_Arduino/practica/06-sensores-comunes/ej02|Ej 02 — Medir distancia con el HC-SR04 (amarillo)]]
- [[Curso_Arduino/practica/06-sensores-comunes/ej03|Ej 03 — Detector de movimiento con el PIR (verde)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/05-comunicacion-serie]]
- Módulo siguiente: [[Curso_Arduino/modelo/07-actuadores-y-potencia]]
