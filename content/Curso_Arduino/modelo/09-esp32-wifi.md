---
title: "Módulo 09 — Salto a ESP32 + WiFi"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/esp32, redes/wifi, redes/http]
aliases: [esp32, wifi-esp32, WiFi.h, HTTPClient, WebServer, modulo-09-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/09-esp32-wifi.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/09-esp32-wifi.md (se regenera con gen_course.py). -->

# Módulo 09 — Salto a ESP32 + WiFi

## Idea central

Hasta aquí todo el curso ha vivido en un Arduino UNO. A partir de ahora la placa es otra: un **ESP32**. Se programa igual (`setup()`, `loop()`, el mismo IDE, las mismas funciones de GPIO), pero es un microcontrolador de otra generación: más pines, mucha más memoria, mucha más velocidad y, sobre todo, **WiFi dentro del chip**. El precio de esa potencia es una regla que no admite excepciones: sus pines trabajan a **3.3 V**, y meterle 5 V a un GPIO lo daña. Con la placa nueva aparece una idea nueva: la placa deja de estar sola en la mesa y pasa a ser **un dispositivo más de una red**, capaz de pedir datos a un servidor y de responder a un navegador.

---

## Qué aprendes

- Qué cambia realmente al pasar del UNO al ESP32: tensión, pines, memoria, velocidad y radio integrada.
- Por qué **nunca** se meten 5 V a un GPIO del ESP32, y qué pines conviene evitar.
- La diferencia entre los dos modos de WiFi: **STA** (unirse a una red) y **AP** (crear una red propia).
- Conectarse a una red con `WiFi.h` y entender qué es la **IP** que devuelve el router.
- Actuar como **cliente HTTP** con `HTTPClient`: pedir datos a una API y leer el código de respuesta.
- Actuar como **servidor HTTP** con `WebServer`: publicar una página y responder a rutas desde el navegador.

---

## Explicación

### El cambio de placa: ESP32 frente a UNO

El UNO y el ESP32 se programan con el mismo lenguaje y el mismo modelo mental. Lo que cambia es el hardware que hay debajo:

| | Arduino UNO | ESP32 DevKit |
|---|---|---|
| Tensión de los GPIO | 5 V | **3.3 V** |
| Velocidad | 16 MHz | 240 MHz (doble núcleo) |
| Memoria RAM | 2 KB | ~520 KB |
| Memoria de programa | 32 KB | ~4 MB (típico) |
| Pines de entrada/salida | 20 | ~34 GPIO |
| Entradas analógicas | 6 (10 bits) | ~15 (12 bits) |
| Conectividad | ninguna | **WiFi y Bluetooth integrados** |
| Velocidad serie habitual | 9600 | **115200** |

Nada de lo aprendido se tira: `pinMode`, `digitalWrite`, `analogRead`, `millis()`, los arrays, las funciones y las máquinas de estados funcionan igual. Lo que ganas es sitio para programas mucho más grandes y una radio que te conecta al mundo sin hardware extra. Lo que pierdes es el margen eléctrico del UNO.

### La regla de oro: 3.3 V

Esta es la única frase del módulo que hay que memorizar literalmente: **nunca metas 5 V a un GPIO del ESP32**. En el UNO, un pin puede recibir 5 V sin problema porque toda su lógica trabaja a 5 V. En el ESP32 la lógica es de 3.3 V, y una entrada por encima de ese nivel castiga el pin y puede dejar la placa inservible. No hay aviso, no hay error de compilación: simplemente un día ese GPIO deja de funcionar.

Consecuencias prácticas:

- Un sensor o un módulo que solo funciona a 5 V **no se conecta directamente**. Hay que alimentarlo a 3.3 V si lo admite, o intercalar un adaptador de nivel entre su salida y el GPIO.
- Cuando el pin manda un `HIGH`, la tensión de salida es **3.3 V**, no 5 V. Para un LED con resistencia de 220 Ω eso solo significa que brilla un poco menos: sigue siendo un montaje seguro.
- El pin marcado `5V` o `VIN` de la placa **es una entrada de alimentación**, no una salida lógica. Sirve para alimentar la placa desde una fuente externa, no para dar 5 V a un circuito de señal.

### Pines: hay muchos más, pero no todos valen para todo

El ESP32 tiene alrededor de 34 GPIO, y en el código se nombran por su **número de GPIO** (GPIO 2, GPIO 4, GPIO 15...), no por una numeración de placa como en el UNO. Ese número es el que va en `pinMode` y `digitalWrite`. La serigrafía del DevKit lo indica, pero conviene mirarla: dos placas con el mismo chip pueden colocar los pines en distinto orden físico.

Algunas restricciones que ahorran horas de depuración:

- **GPIO 34 a 39 son solo de entrada.** No tienen etapa de salida, así que un `digitalWrite` sobre ellos no hace nada. Tampoco tienen resistencia de pull-up interna, de modo que un botón con `INPUT_PULLUP` ahí no funciona.
- **GPIO 6 a 11 están ocupados** por la memoria flash del propio chip. Usarlos cuelga la placa.
- Algunos pines son **pines de arranque** (GPIO 0, 2, 12, 15): su estado en el momento del reset decide cómo arranca el chip. Si les conectas algo que los fuerza a un nivel, la placa puede no arrancar o entrar en modo de programación.
- El **ADC2** (varios canales analógicos) no se puede usar mientras el WiFi está activo. En un proyecto con red, las lecturas analógicas van al ADC1 (GPIO 32 a 39).
- El **LED integrado** del DevKit está en **GPIO 2** y ya lleva su resistencia en la placa.

### Los dos modos de WiFi: STA y AP

Una placa con radio puede jugar dos papeles distintos:

- **STA (estación)**: la placa **se une** a una red que ya existe, como haría un móvil con el router de casa. Es el modo de todo este módulo, y se pide con `WiFi.mode(WIFI_STA)`.
- **AP (punto de acceso)**: la placa **crea** su propia red, y son otros dispositivos los que se conectan a ella. Es lo que se usa cuando no hay router disponible o para configurar el aparato la primera vez.

En modo STA, conectarse es siempre la misma secuencia: dices a qué red y con qué contraseña, y luego **esperas**. La conexión no es instantánea, tarda entre décimas de segundo y varios segundos, así que hace falta un bucle que pregunte por el estado hasta que sea `WL_CONNECTED`. Cuando termina, el router ha asignado a la placa una **dirección IP** por DHCP, y esa IP es la dirección a la que hay que hablarle desde fuera.

### Cliente y servidor: los dos papeles en HTTP

Con la placa en la red, hay dos cosas distintas que puede hacer, y conviene no mezclarlas:

- **Cliente**: la placa **pide**. Abre una conexión hacia otra máquina, lanza una petición y espera la respuesta. Es lo que hace un navegador cuando abres una web, y es el ejercicio 02.
- **Servidor**: la placa **responde**. Se queda escuchando en un puerto y, cuando alguien le pide algo, le contesta. Es lo que hace la web que abres, y es el ejercicio 03.

Una petición HTTP tiene siempre una **ruta** (`/`, `/on`, `/off`) y una respuesta tiene siempre un **código**: 200 significa que fue bien, 404 que la ruta no existe, 500 que el servidor falló. En el lado cliente, la librería `HTTPClient` devuelve además códigos **negativos** para señalar que la petición ni siquiera llegó a hablar con un servidor (no hay red, el nombre no resuelve, se agotó el tiempo). Por eso el patrón habitual es comprobar `codigo > 0` antes de intentar leer el cuerpo.

El otro concepto es el **puerto**. Una IP identifica la máquina; el puerto identifica el servicio dentro de ella. El puerto 80 es el de HTTP por convenio, y por eso al escribir `http://192.168.1.50` en el navegador no hace falta decir nada más: el navegador ya supone el 80.

### Un servidor no puede dormir

En cuanto la placa hace de servidor, `delay()` deja de ser inofensivo. El servidor de `WebServer` no atiende peticiones por su cuenta: solo revisa si hay alguien esperando cuando tú llamas a `server.handleClient()`. Si el `loop()` se pasa dos segundos dentro de un `delay`, durante esos dos segundos el navegador se queda colgado. La regla es: `server.handleClient()` en **cada vuelta** del `loop()`, y cualquier temporización se hace con `millis()`, como en el módulo 06.

---

## El montaje

Este es probablemente el módulo con menos cableado del curso, y no es casualidad: lo que cambia está dentro del chip, no en la protoboard.

Lo que necesitas por puesto es una **placa ESP32 DevKit** (DevKit C o WROOM) y su **cable USB**. Nada más. Los ejercicios 01 y 02 no llevan ningún componente: solo la placa conectada al ordenador. El ejercicio 03 usa el **LED integrado en GPIO 2**, que ya viene soldado con su resistencia, así que tampoco hay que montar nada.

Opcionalmente, si quieres ver un LED externo en vez del de la placa, basta un **LED de 5 mm** con una **resistencia de 220 Ω** y dos cables Dupont macho-macho, montados igual que en el módulo 01: GPIO elegido, resistencia, ánodo del LED, cátodo a GND. Con 3.3 V en el pin, 220 Ω sigue siendo un valor seguro.

Antes de la primera compilación hay que preparar el entorno, que es distinto al del UNO:

- Instalar el **core ESP32** de Espressif desde el gestor de placas del IDE (buscar "esp32"). Sin él, el IDE no conoce esta placa y `WiFi.h` no existe.
- Seleccionar la placa **ESP32 Dev Module** y el puerto serie correcto. El FQBN, si usas `arduino-cli`, es `esp32:esp32:esp32`.
- Poner el **monitor serie a 115200**. Si lo dejas en 9600, verás caracteres basura y pensarás que la placa está rota.

Y si no tienes placa física, los tres ejercicios funcionan en **Wokwi**, que sí simula WiFi: ofrece una red abierta llamada `Wokwi-GUEST`, sin contraseña.

---

## Worked example: conectarse y decir quién eres

```cpp
#include <WiFi.h>

const char* SSID     = "Wokwi-GUEST";
const char* PASSWORD = "";

void setup() {
    Serial.begin(115200);
    delay(100);

    WiFi.mode(WIFI_STA);              // nos unimos a una red existente
    WiFi.begin(SSID, PASSWORD);       // arranca el intento; NO bloquea

    while (WiFi.status() != WL_CONNECTED) {   // esperar a que termine
        delay(250);
        Serial.print(".");
    }

    Serial.print("IP asignada: ");
    Serial.println(WiFi.localIP());   // la dirección que nos dio el router
}

void loop() {
    // nada: la conexión ya está hecha
}
```

Léelo como una frase: *arranca el serie; declara que quieres unirte a esta red con esta contraseña; espera, imprimiendo un punto cada 250 ms, hasta que el estado sea "conectado"; y entonces di qué IP te han dado*.

Las tres piezas que merecen atención son estas. `WiFi.begin()` **no espera**: lanza el proceso y devuelve el control inmediatamente, por eso hace falta el bucle. El bucle consulta `WiFi.status()`, que va cambiando de estado mientras la placa negocia con el router, hasta llegar a `WL_CONNECTED`. Y `WiFi.localIP()` solo tiene sentido después de ese punto, porque la IP la reparte el router, no la placa: preguntarla antes devuelve `0.0.0.0`.

El detalle de imprimir un punto en cada vuelta no es decorativo: es la única señal visible de que la placa sigue intentándolo. Sin él, un fallo de conexión y una placa colgada se ven exactamente igual desde el monitor serie.

---

## Errores típicos

- **Dejar seleccionado el Arduino UNO en el IDE.** El sketch no compila (`WiFi.h` no existe) o no sube. Al cambiar de placa hay que cambiar también la selección de placa y el puerto.
- **El monitor serie a 9600.** El ESP32 habla a 115200; a otra velocidad solo verás símbolos ilegibles. No es un fallo del programa.
- **Meter 5 V a un GPIO.** Es el error caro: daña la placa y no avisa. Todo lo que se conecte a un pin del ESP32 tiene que hablar a 3.3 V.
- **Esperar una contraseña en Wokwi.** La red del simulador es `Wokwi-GUEST` y la contraseña es la cadena vacía `""`, no un espacio ni un texto inventado.
- **Leer la IP antes de estar conectado.** Sale `0.0.0.0`. La IP la asigna el router y solo existe tras `WL_CONNECTED`.
- **Poner un `delay()` largo en el `loop()` de un servidor.** La página deja de responder. `server.handleClient()` tiene que ejecutarse en cada vuelta.
- **Olvidar abrir la IP en el navegador.** El servidor arranca sin decir nada más; la dirección la imprime el monitor serie y hay que copiarla a mano.
- **Dar por hecho que la petición HTTP salió bien.** Hay que mirar el código devuelto: si es negativo, ni siquiera hubo respuesta y el cuerpo estará vacío.
- **Usar GPIO 34-39 como salida** o un ADC2 con el WiFi encendido. Ninguna de las dos cosas da error de compilación; simplemente no funcionan.

---

## Preguntas para pensar

- ¿Qué diferencia hay entre que la placa sea cliente (ejercicio 02) y servidor (ejercicio 03)? ¿Quién empieza la conversación en cada caso?
- ¿Por qué el ESP32 puede hacer esto y el UNO no, sin hardware adicional?
- ¿Qué pasaría si la red tuviera contraseña? ¿Y si la red no existe: cuánto tiempo se quedaría el programa en el bucle de espera, y cómo lo arreglarías?
- Si `WiFi.localIP()` te da una IP como `192.168.1.50`, ¿podría alguien de fuera de tu casa abrir esa dirección? ¿Por qué?
- El servidor del ejercicio 03 controla un LED. Si en vez de un LED hubiera un relé conectado a una lámpara, ¿qué precauciones cambiarían y cuáles no?

---

## Ejercicios

- [[Curso_Arduino/practica/09-esp32-wifi/ej01|Ej 01 — Conectar al WiFi y mostrar la IP (verde)]]
- [[Curso_Arduino/practica/09-esp32-wifi/ej02|Ej 02 — Cliente HTTP: GET a una API pública (verde)]]
- [[Curso_Arduino/practica/09-esp32-wifi/ej03|Ej 03 — Servidor web para encender el LED (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/08-pantallas]]
- Módulo siguiente: [[Curso_Arduino/modelo/10-esp32-iot-mqtt]]
