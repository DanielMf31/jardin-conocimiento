---
title: "Módulo 08 — Pantallas"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/i2c, electronica/pantallas, programacion/librerias]
aliases: [i2c, lcd-1602, oled-ssd1306, escaner-i2c, pantallas-arduino, modulo-08-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/08-pantallas.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/08-pantallas.md (se regenera con gen_course.py). -->

# Módulo 08 — Pantallas

## Idea central

Hasta ahora, cuando tu programa tenía algo que decir, lo decía por el Monitor Serie: es decir, solo mientras estuviera enchufado al ordenador. Una pantalla rompe esa dependencia y convierte el montaje en un aparato de verdad. Y lo interesante no es la pantalla en sí, sino **cómo se habla con ella**: por el bus **I2C**, dos cables compartidos por los que caben decenas de dispositivos, cada uno identificado por una **dirección**. Aprender I2C aquí no es aprender a poner texto en un LCD: es aprender el mecanismo con el que se conectan la mayoría de los sensores y módulos del mundo Arduino.

---

## Qué aprendes

- Qué es un **bus** y por qué dos líneas (SDA y SCL) bastan para hablar con varios dispositivos a la vez.
- Qué es una **dirección I2C** y por qué es lo primero que hay que verificar cuando "no se ve nada".
- Conectar y usar un **LCD 1602** con módulo I2C: caracteres, filas y columnas, retroiluminación.
- Conectar y usar una **OLED SSD1306** de 128x64: píxeles, texto y gráficos con las librerías de Adafruit.
- La diferencia entre escribir **directo** (LCD) y dibujar en un **buffer** que hay que volcar (OLED).
- Escribir tu propio **escáner I2C** y usarlo como herramienta de diagnóstico.

---

## Explicación

### El problema que resuelve el I2C

Un LCD 1602 "a pelo", conectado en paralelo como se hacía tradicionalmente, necesita unos doce cables: cuatro u ocho de datos, más las líneas de control, más alimentación. Con eso ya te has comido medio Arduino UNO y todavía no has puesto ni un sensor. Y si mañana quieres añadir un reloj de tiempo real y un sensor de temperatura, no te quedan pines.

La alternativa es dejar de dar a cada dispositivo su propio juego de cables y **compartir** unos pocos entre todos. Eso es un **bus**: unas líneas comunes a las que todo el mundo se engancha en paralelo, más un convenio de quién habla y cuándo. El I2C (se lee "i cuadrado c" o "i dos c") lleva esa idea al extremo: **dos líneas de señal y ya está**.

### SDA y SCL: los dos únicos cables de señal

| Línea | Nombre | Qué lleva |
|---|---|---|
| **SDA** | Serial Data | los bits: direcciones, datos, confirmaciones |
| **SCL** | Serial Clock | el reloj: marca el ritmo al que se leen esos bits |

Con un solo cable de datos, los bits van **en serie**, uno detrás de otro. El problema de mandar bits por un cable es ponerse de acuerdo en cuándo mirar: si el emisor cambia el nivel cada milisegundo y el receptor mira cada dos, se pierde la mitad del mensaje. El I2C lo resuelve con el segundo cable: **SCL es la señal de "mira ahora"**. El maestro genera los pulsos de reloj y, en cada pulso, el valor que haya en SDA es el bit válido. Por eso el I2C no necesita que los dos extremos acuerden previamente una velocidad, a diferencia del puerto serie del módulo 05, donde los 9600 baudios tenían que coincidir a ambos lados.

En el Arduino UNO, esos dos pines **están fijados por el hardware y no se pueden mover**: **SDA = A4** y **SCL = A5**. Aunque se llamen A4 y A5 y en el módulo 04 los usaras como entradas analógicas, aquí trabajan como el bus I2C. En cuanto uses I2C, esos dos pines dejan de estar disponibles para otra cosa.

Los otros dos cables de cada pantalla no son señal, son alimentación: **VCC a 5V** y **GND a masa**. De ahí la frase del módulo: cuatro cables por pantalla, y dos de ellos los comparten todas.

### La dirección I2C: cómo se llama a uno solo entre varios

Si todos los dispositivos están enganchados a los mismos dos cables, todos oyen todo. Hace falta una forma de decir "esto va para ti y no para el resto". Esa forma es la **dirección**: un número de **7 bits** (de 0 a 127, aunque unas cuantas están reservadas) grabado de fábrica en cada chip.

Toda conversación I2C empieza igual: el **maestro** (tu Arduino) pone en el bus la dirección del dispositivo con el que quiere hablar. Los dispositivos escuchan esa dirección, la comparan con la suya y todos menos uno se desentienden. El que la reconoce responde con un **ACK** (una confirmación) y a partir de ahí la conversación es entre esos dos.

Las direcciones se escriben casi siempre en **hexadecimal**, porque así se ven directamente como dos dígitos: `0x27`, `0x3C`, `0x3F`. En C++, el prefijo `0x` significa exactamente eso, "lo que viene es hexadecimal": `0x27` es el número 39 en decimal, y son el mismo número escrito de dos maneras.

Direcciones que te vas a encontrar en este módulo:

| Dispositivo | Dirección habitual | Alternativa frecuente |
|---|---|---|
| LCD 1602 con backpack I2C | `0x27` | `0x3F` (clones con otro chip) |
| OLED SSD1306 0.96" | `0x3C` | `0x3D` |

Dos consecuencias importantes. La primera: **la dirección la fija el fabricante**, tú solo la escribes en el código, y si te equivocas la pantalla se queda en blanco sin dar ningún error, porque el Arduino está llamando a un dispositivo que no existe. La segunda: **dos dispositivos con la misma dirección en el mismo bus no pueden convivir**, porque responderían los dos a la vez y el bus se vuelve inservible. Por eso muchos módulos traen un puentecito o unos pads soldables para cambiar un bit de su dirección.

### El escáner: la herramienta que te salva

Como el error de dirección es silencioso y es el más frecuente del módulo, existe un truco estándar: recorrer **todas** las direcciones posibles, intentar hablar con cada una, y anotar cuáles contestan. Eso es un **escáner I2C**, y es el ejercicio 03.

La idea es que en I2C se puede "llamar y colgar" sin mandar datos: abres una transmisión hacia una dirección, la cierras y miras qué te devuelve la operación de cierre. Si devuelve `0`, hubo ACK: **allí hay alguien**. Cualquier otro valor significa que nadie contestó.

Este programa deberías guardártelo para siempre. Cuando montes un módulo I2C nuevo (un reloj, un acelerómetro, un sensor de luz) y no responda, el escáner te dice en treinta segundos si el problema es de **cableado** (no aparece nada) o de **dirección** (aparece un número distinto al que tienes en el código). Distinguir esas dos situaciones es la mitad de la depuración.

### Pull-ups: por qué el bus necesita resistencias (y por qué no las pones tú)

Las líneas SDA y SCL funcionan en **drenador abierto**: los dispositivos conectados solo saben hacer una cosa, **tirar la línea a 0 V**. Ninguno la empuja activamente a 5 V. Esto se hace así a propósito, para que dos dispositivos que hablen a la vez por error no se cortocircuiten entre sí (uno mandando 5 V contra otro mandando 0 V).

El precio es que, si nadie tira de la línea hacia abajo, hace falta algo que la devuelva arriba: una **resistencia de pull-up** (típicamente entre 4,7 kΩ y 10 kΩ) entre la línea y 5 V. Sin pull-ups el bus no sube nunca a 1 y no funciona nada.

En la práctica no te preocupa, y conviene saber por qué: **los módulos LCD-I2C y OLED ya traen sus pull-ups soldados**. El detalle a recordar es el caso contrario: si apilas muchos módulos con pull-ups en el mismo bus, las resistencias quedan en paralelo, la resistencia total baja demasiado y el bus se sobrecarga. Con dos pantallas no pasa nada; con seis módulos empieza a pasar.

### Dos pantallas, dos filosofías

El bus es el mismo para las dos, pero lo que hay al otro lado es muy distinto.

El **LCD 1602** es una pantalla de **caracteres**: 16 columnas por 2 filas, 32 huecos, y en cada hueco cabe una letra de un alfabeto que el chip ya tiene grabado. No puedes dibujar una línea diagonal porque no hay píxeles a los que llegar. A cambio es muy sencillo de usar: colocas el cursor en una posición y escribes; lo que escribes se queda ahí hasta que lo sobrescribas.

De esa persistencia sale un detalle sutil: el LCD **no borra solo**. Si escribes `Contador: 10` y después `Contador: 9`, el `0` del `10` se queda en pantalla y lees `Contador: 90`. La solución barata es imprimir unos espacios detrás del número para tapar lo que sobra.

La **OLED SSD1306** es una matriz de **128 x 64 píxeles** que puedes encender uno a uno. Eso permite texto en varios tamaños, líneas, rectángulos, barras de progreso, iconos. Además no lleva retroiluminación: cada píxel emite su propia luz, así que el negro es negro de verdad y el contraste es enorme.

El precio de esa libertad es que el chip trabaja con un **buffer**: una copia de toda la pantalla en la memoria del Arduino. Cuando dibujas, estás modificando esa copia en RAM, no la pantalla. Hasta que no llamas a la función que vuelca el buffer, en el cristal no cambia nada. Esta es la fuente número uno de frustración con las OLED: el código parece correcto, compila, y la pantalla sigue negra. Falta el volcado.

Puestas una al lado de otra:

| | LCD 1602 | OLED SSD1306 |
|---|---|---|
| Unidad mínima | un carácter (16x2) | un píxel (128x64) |
| Gráficos | no | sí |
| Librería | `LiquidCrystal I2C` | `Adafruit GFX` + `Adafruit SSD1306` |
| Dirección típica | `0x27` | `0x3C` |
| Se ve al escribir | sí, directo | no, hay que volcar el buffer |
| Memoria que consume | muy poca | el buffer ocupa 1 KB de la RAM del UNO |

Ese último dato conviene tenerlo presente: el Arduino UNO tiene 2 KB de RAM en total, y el buffer de una OLED 128x64 se lleva la mitad. No es un problema en estos ejercicios, pero explica por qué en programas grandes con OLED empiezan a salir avisos de memoria baja.

### Las librerías hacen el trabajo sucio

En ninguno de los ejercicios vas a componer tramas I2C a mano. `Wire.h` (incluida con el IDE) gestiona el bus, y encima se apoyan las librerías de cada pantalla: `LiquidCrystal_I2C` para el LCD, y el par `Adafruit_GFX` + `Adafruit_SSD1306` para la OLED.

Ese par merece una explicación, porque es un patrón de diseño que vas a ver mucho. **Adafruit GFX** no sabe nada de tu pantalla: sabe de geometría (dibujar texto, líneas, rectángulos, círculos) sobre una superficie abstracta. **Adafruit SSD1306** sabe de tu pantalla concreta: cómo arrancarla y cómo mandarle el buffer por I2C. Separado así, el mismo código de dibujo sirve para una OLED, para una TFT en color o para una matriz de LEDs: solo cambias la librería de abajo. Por eso hay que instalar las dos: una sin la otra no hace nada.

---

## El montaje: cuatro cables por pantalla

Para todo el módulo necesitas un Arduino UNO con su cable USB, una protoboard para repartir alimentación y bus, un **LCD 1602 con módulo I2C** (el backpack lleva un chip PCF8574, que es el que traduce del I2C a las doce patillas del LCD), una **OLED SSD1306 de 0,96" y 128x64** y unos ocho cables Dupont macho-macho. Si no tienes el kit físico, cada ejercicio trae su montaje listo en Wokwi.

El conexionado es idéntico para las dos pantallas:

| Señal | Pin del UNO | Pin de la pantalla |
|---|---|---|
| Datos | **A4** | SDA |
| Reloj | **A5** | SCL |
| Alimentación | 5V | VCC |
| Masa | GND | GND |

```
UNO A4 ─────┬───── SDA (LCD)
            └───── SDA (OLED)
UNO A5 ─────┬───── SCL (LCD)
            └───── SCL (OLED)
UNO 5V ──── VCC de ambas
UNO GND ─── GND de ambas
```

Ese dibujo es el montaje real del ejercicio 03, y es la demostración física de todo lo anterior: **dos dispositivos distintos colgando de los mismos dos cables de señal**, distinguidos solo por su dirección. Si tuvieras que cablearlos en paralelo necesitarías más de veinte hilos y no te cabrían en el UNO.

Dos avisos de seguridad. Estas pantallas van a **5V en el UNO** sin problema, pero en el ESP32 del módulo 09 todo es de **3,3 V**: no le metas 5 V a un GPIO. Y no cruces SDA con SCL: es un fallo invisible (nada se quema, simplemente el escáner no encuentra nada) y por eso conviene cablear siempre con el mismo criterio de colores.

---

## Worked example: encender una OLED y escribir en ella

Este es el esqueleto mínimo de cualquier programa con OLED, sin gráficos ni bucle, para que se vean las piezas:

```cpp
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define ANCHO 128
#define ALTO   64
#define DIR_OLED 0x3C

Adafruit_SSD1306 oled(ANCHO, ALTO, &Wire, -1);

void setup() {
    oled.begin(SSD1306_SWITCHCAPVCC, DIR_OLED);  // arranca la pantalla en esa dirección
    oled.clearDisplay();                         // limpia el buffer en memoria
    oled.setTextSize(1);                         // fuente de 6x8 píxeles
    oled.setTextColor(SSD1306_WHITE);            // píxeles encendidos

    oled.setCursor(0, 0);                        // esquina superior izquierda
    oled.println("Hola");
    oled.display();                              // VUELCA el buffer a la pantalla
}

void loop() {
}
```

Léelo por partes. Las tres constantes describen el hardware: tamaño de la matriz y dirección en el bus. La línea del objeto `oled` es la que ata la librería a tu pantalla concreta: dimensiones, el bus por el que se habla (`&Wire`, es decir, el I2C del UNO) y `-1` para decir "esta pantalla no tiene un pin de reset propio".

En `setup()`, `begin` es la conversación inicial de arranque, y el `SSD1306_SWITCHCAPVCC` significa que la pantalla genera internamente la tensión que necesitan sus píxeles a partir de los 5 V. Después, todo lo que hacen `setCursor` y `println` ocurre **en la RAM del Arduino**: el cristal sigue negro. Solo la última línea, `display()`, envía ese kilobyte por el bus I2C y hace visible el resultado.

Fíjate en que todo esto está en `setup()` y `loop()` está vacío: si el contenido no cambia, no hay ninguna razón para redibujar sesenta veces por segundo. Cuando el contenido sí cambia, como en el ejercicio 02, el ciclo pasa a ser siempre el mismo: limpiar el buffer, dibujar el fotograma entero, volcarlo, esperar.

---

## Errores típicos

- **Dirección equivocada.** `0x27` en vez de `0x3F` en el LCD, `0x3C` en vez de `0x3D` en la OLED. La pantalla se queda en blanco y el programa no da ningún error. Corre el escáner y pon la dirección que salga.
- **Olvidar el volcado del buffer en la OLED.** Dibujas todo perfectamente en RAM y nunca lo mandas a la pantalla. Si la OLED enciende pero está negra, sospecha de esto antes que de nada.
- **SDA y SCL cruzados.** A4 con SCL y A5 con SDA. El escáner no encuentra absolutamente nada, que es justo la pista para distinguirlo de un fallo de dirección.
- **No instalar las librerías, o instalar una parecida.** Hay varias con nombres casi iguales. Para el LCD, `LiquidCrystal I2C`; para la OLED hacen falta **las dos** de Adafruit, GFX y SSD1306.
- **Olvidar la retroiluminación del LCD.** El programa funciona, el texto está escrito, pero sin luz de fondo no se lee nada y parece que no va.
- **Contraste mal ajustado en el LCD.** Se ven bloques negros o no se ve nada. Se corrige con el potenciómetro del propio backpack, no con código.
- **No borrar lo anterior en el LCD.** Al pasar de un número de dos cifras a uno de una, queda el dígito viejo colgando. Tapa el resto con espacios.
- **Alimentar la pantalla desde un pin digital** en vez de desde 5V. Un pin no da corriente suficiente para una pantalla.

---

## Preguntas para pensar

- ¿Por qué con I2C bastan dos cables para cinco sensores y con conexión directa harían falta decenas?
- ¿Qué crees que ocurre si dos dispositivos del mismo bus tienen la misma dirección? ¿Podría el escáner detectarlo?
- ¿Por qué la OLED necesita volcar un buffer y el LCD no? ¿Qué gana cada uno con su forma de trabajar?
- Los pull-ups son necesarios, pero casi nunca los pones tú. ¿Dónde están y qué pasaría si conectaras ocho módulos que los llevan?
- Si el escáner encuentra un dispositivo pero la pantalla sigue en blanco, ¿qué has descartado ya y qué te queda por mirar?
- El buffer de la OLED ocupa 1 KB de los 2 KB de RAM del UNO. ¿Cómo mostrarías gráficos si te quedaras sin memoria?

---

## Ejercicios

- [[Curso_Arduino/practica/08-pantallas/ej01|Ej 01 — LCD 1602 por I2C con contador (verde)]]
- [[Curso_Arduino/practica/08-pantallas/ej02|Ej 02 — OLED SSD1306: texto y barra de progreso (verde)]]
- [[Curso_Arduino/practica/08-pantallas/ej03|Ej 03 — Escáner de direcciones I2C (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/07-actuadores-y-potencia]]
- Módulo siguiente: [[Curso_Arduino/modelo/09-esp32-wifi]]
