---
title: "Módulo 10 — ESP32 IoT (MQTT / API)"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/esp32, iot/mqtt, redes/http, programacion/apis]
aliases: [mqtt-esp32, publish-subscribe, broker-mqtt, PubSubClient, HTTPClient, modulo-10-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/10-esp32-iot-mqtt.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/10-esp32-iot-mqtt.md (se regenera con gen_course.py). -->

# Módulo 10 — ESP32 IoT (MQTT / API)

## Idea central

Una placa conectada a WiFi que no habla con nadie no sirve de mucho. Un dispositivo IoT es útil cuando **manda datos** a algún sitio y **recibe órdenes** de algún sitio. Hay dos formas de hacerlo y este módulo trata las dos: **HTTP**, donde tu placa llama a un servidor concreto y espera respuesta, y **MQTT**, donde tu placa se engancha una vez a un intermediario (el **broker**) y a partir de ahí publica o escucha sin saber quién hay al otro lado. La segunda idea, publicar y suscribirse en vez de preguntar, es el concepto grande del módulo.

---

## Qué aprendes

- Qué es el patrón publicar/suscribir: broker, topic, publisher y subscriber.
- Publicar datos periódicos a un topic MQTT con la librería `PubSubClient`.
- Suscribirse a un topic y reaccionar a lo que llega mediante un **callback**.
- Por qué `mqtt.loop()` es obligatorio y qué se rompe si falta.
- Enviar una lectura como **JSON** por HTTP POST con `HTTPClient`, listo para que lo reciba una API.
- Cuándo conviene MQTT y cuándo conviene HTTP, que es la decisión de diseño de verdad.
- Qué implica usar un broker público y qué haría falta para llevar esto a producción.

---

## Explicación

### El esquema IoT: dispositivo, red, servidor

Todo lo de este módulo cabe en tres cajas: el **dispositivo** (el ESP32, que mide o actúa), la **red** (el WiFi del módulo 09, que ya das por sabido) y el **servidor** (algo, en algún ordenador, que guarda los datos o manda órdenes). Lo único que cambia entre MQTT y HTTP es cómo se hablan la primera y la tercera caja.

### HTTP: preguntar y esperar respuesta

Es el modelo que ya conoces de navegar por internet. El dispositivo **abre una conexión** hacia una dirección concreta, manda una petición (`GET` para pedir, `POST` para entregar), el servidor contesta con un código y un cuerpo, y la conexión se cierra. Es una conversación de dos: el que pregunta y el que responde, y hay que saber **a quién** se le pregunta.

Es universal (cualquier servidor del mundo entiende HTTP) y muy fácil de depurar, pero es pesado: por cada dato que mandas se abre y se cierra un socket, se negocia TLS si es HTTPS y viajan cabeceras que ocupan más que el propio dato. Y sobre todo, es **de ida**: el servidor no puede hablarte a ti si tú no le preguntas primero.

### MQTT: publicar y suscribirse

MQTT le da la vuelta a la conversación. Existe una pieza intermedia, el **broker**, y todo el mundo se conecta a él **una sola vez** y mantiene esa conexión abierta.

- Quien tiene un dato lo **publica** en un *topic*.
- Quien quiere ese dato se **suscribe** a ese topic.
- El broker se encarga de que lo publicado llegue a todos los suscritos.

Un **topic** es simplemente una ruta jerárquica de texto, con niveles separados por barras: `esibot/demo/contador`, `esibot/demo/led`. No hay que crearlo ni registrarlo en ningún sitio: en cuanto alguien publica en un topic, el topic existe.

Lo interesante es el **desacoplamiento**: el que publica no sabe quién escucha, ni cuántos son, ni si hay alguien. El que escucha no sabe de qué placa viene el dato. Los dos solo conocen al broker y el nombre del topic. Añadir un segundo receptor (un panel, una base de datos, tu móvil) no obliga a tocar el firmware de la placa: se suscribe al mismo topic y ya está.

### Las dos vías, comparadas

| | HTTP | MQTT |
|---|---|---|
| Modelo | petición / respuesta | publicar / suscribir |
| Quién empieza | siempre el dispositivo | cualquiera, en cualquier momento |
| Conexión | se abre y se cierra en cada envío | una sola, permanente |
| Quién conoce a quién | el dispositivo conoce al servidor | los dos conocen solo al broker |
| Coste por mensaje | alto (cabeceras, handshake) | muy bajo (unos pocos bytes) |
| Recibir órdenes | difícil (hay que preguntar cada poco) | natural (te suscribes y esperas) |
| Cuándo usarlo | pocos envíos, integrar con una API que ya existe | muchos sensores, mensajes frecuentes, control bidireccional |

La regla práctica: si tienes **un** dispositivo que manda **de vez en cuando** un dato a un backend que ya habla REST, HTTP. Si tienes **muchos** dispositivos, mensajes frecuentes, ancho de banda escaso o necesitas mandarles órdenes, MQTT.

### Publicar: PubSubClient

MQTT no viene con el core del ESP32; se usa la librería **`PubSubClient`** de Nick O'Leary. El patrón de montaje es siempre el mismo:

```cpp
WiFiClient   espClient;          // el socket TCP por debajo
PubSubClient mqtt(espClient);    // el cliente MQTT montado sobre ese socket
```

`PubSubClient` no sabe nada de WiFi: solo sabe hablar el protocolo MQTT por encima de un socket que le des. Por eso primero se conecta el WiFi y luego se le dice a qué broker apuntar, con `mqtt.setServer(broker, puerto)`, y se conecta con `mqtt.connect(clientId)`.

El **clientId** es el nombre con el que el broker te identifica y **debe ser único**: si dos placas se presentan con el mismo, el broker echa a la primera cuando entra la segunda, y acabas con dos placas desconectándose la una a la otra sin parar. Por eso en los ejercicios se le pega un sufijo aleatorio.

Publicar es una sola línea, `mqtt.publish(topic, payload)`, donde el payload es **texto**: MQTT transporta bytes, no números. Un entero hay que convertirlo antes, con `snprintf` o con `String`.

### Suscribirse: el callback

Recibir no se hace con una función que "espera un mensaje", porque eso bloquearía la placa. Se registra una **función callback** y la librería la llama ella cuando hay algo:

```cpp
void alRecibir(char* topic, byte* payload, unsigned int length) { ... }
mqtt.setCallback(alRecibir);
mqtt.subscribe("esibot/demo/led");
```

Hay un detalle que sorprende a todo el mundo: **el payload no es un texto terminado en `\0`**. Llega como un puntero a bytes y una longitud aparte. Si lo tratas como si fuera una cadena de C, leerás basura de memoria más allá del mensaje. Hay que reconstruirlo recorriendo los `length` bytes.

### Por qué `mqtt.loop()` es obligatorio

`PubSubClient` no tiene un hilo propio ni interrupciones: **no hace nada por su cuenta**. Todo su trabajo (leer del socket lo que ha llegado, invocar tu callback, contestar los pings de mantenimiento del broker) ocurre dentro de `mqtt.loop()`. Si te olvidas de llamarlo en cada vuelta del `loop()`, los mensajes no llegan nunca y, al cabo de unos segundos sin responder al keepalive, el broker te desconecta. Es el error número uno con esta librería.

De ahí se sigue algo importante: **nada de `delay()` largos**. Si bloqueas la placa un segundo, durante ese segundo `mqtt.loop()` no se ejecuta. La temporización se hace con `millis()`, como en el módulo 02: comparas el reloj y actúas cuando toca, sin dejar de dar vueltas.

### Enviar JSON por HTTP

La otra vía usa `HTTPClient`, que sí viene con el core del ESP32. La secuencia es literal:

```cpp
HTTPClient http;
http.begin(URL);                                     // a dónde
http.addHeader("Content-Type", "application/json");  // qué mando
int code = http.POST(cuerpo);                        // mandarlo
http.end();                                          // cerrar
```

Dos cosas que hay que interiorizar. La primera: la cabecera `Content-Type: application/json` **no es decorativa**. Sin ella el servidor recibe el cuerpo como texto plano y una API tipo FastAPI se niega a interpretarlo como JSON. La segunda: el número que devuelve `POST` es el **código HTTP** si la petición llegó (200 y 201 son éxito, 4xx es culpa tuya, 5xx del servidor), pero si es **negativo** significa que ni siquiera hubo conversación: fallo de red, DNS, TLS o URL mal escrita. Distinguir "el servidor me dijo que no" de "no llegué al servidor" es media depuración.

El JSON se puede montar a mano con `snprintf` cuando es sencillo, y así no dependes de ninguna librería extra. Ojo con el tamaño del buffer y con escapar las comillas.

### La red en Wokwi

En el simulador no hay que configurar nada raro: la red se llama **`Wokwi-GUEST`** y **no tiene contraseña**. Es una red simulada, pero **con salida real a internet**, así que un broker público o `httpbin.org` funcionan de verdad desde la simulación: lo que publica tu placa virtual lo puedes ver llegar en la consola web del broker desde tu navegador. Con placa física, tu red doméstica de **2.4 GHz**: el ESP32 no se conecta a 5 GHz.

### Seguridad: qué estás haciendo exactamente

Los ejercicios usan un broker **público** y sin cifrar, `broker.hivemq.com` en el puerto **1883**. Eso significa, literalmente, que cualquier persona del mundo puede suscribirse a tu topic y leer lo que publicas, y puede publicar en él haciéndose pasar por ti. Está bien para aprender, y para nada más: no mandes ahí datos reales ni nada que identifique a alguien, y no te sorprendas si ves mensajes de desconocidos en topics con nombres genéricos.

Para algo serio hacen falta tres cosas: **TLS** (MQTT cifrado en el puerto 8883, HTTPS en vez de HTTP), **credenciales** de usuario y contraseña o certificados en el broker, y **no escribir esos secretos en el sketch**. Lo habitual es sacarlos a un `secrets.h` que se queda fuera del control de versiones, o inyectarlos al compilar. Un repositorio público con el WiFi de tu casa dentro de un `.ino` es un problema real, no una hipótesis.

---

## El montaje

Este módulo es casi todo software: **los dos primeros ejercicios no necesitan montar nada**. Basta un **ESP32 DevKit** (DevKit-C v4 o similar) con su cable USB, porque el ej02 usa el LED que la propia placa lleva soldado. En un ESP32 DevKit genérico ese LED está en el **GPIO2**, y el core no siempre define `LED_BUILTIN`, así que los sketches lo definen ellos con un `#ifndef` por si acaso.

El tercer ejercicio funciona con una lectura **simulada**: `analogRead` sobre un pin al aire devuelve ruido, que para demostrar el envío vale igual. Si quieres una lectura de verdad, lo único que se añade es un **potenciómetro de 10 kΩ** (o una **LDR con una resistencia de 10 kΩ** en divisor) con su salida al **GPIO34**, más protoboard y unos cables.

Dos recordatorios de ESP32 que siguen valiendo aquí. El primero: la placa es de **3.3 V**, el ADC lee de 0 a 3.3 V devolviendo de 0 a 4095, y meterle 5 V a un GPIO lo daña. El segundo: **GPIO34, 35, 36 y 39 son solo entrada**, no tienen salida ni pull-up interno; por eso son el sitio natural para un sensor analógico.

En cuanto al software, `WiFi.h` y `HTTPClient.h` vienen con el core ESP32 y no se instalan aparte; **`PubSubClient` sí hay que instalarla**, desde el Gestor de Librerías del IDE o declarándola en el `libraries.txt` del proyecto de Wokwi.

---

## Worked example: publicar un contador

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
const char* TOPIC       = "esibot/demo/contador";

WiFiClient   espClient;
PubSubClient mqtt(espClient);

int contador = 0;
unsigned long ultimo = 0;

void setup() {
    Serial.begin(115200);
    conectarWiFi();                          // igual que en el módulo 09
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);  // a qué broker apuntamos
}

void loop() {
    if (!mqtt.connected()) conectarMQTT();   // si se cayó, reconectar
    mqtt.loop();                             // imprescindible en cada vuelta

    if (millis() - ultimo >= 2000) {         // cada 2 s, sin bloquear
        ultimo = millis();
        contador++;
        char payload[16];
        snprintf(payload, sizeof(payload), "%d", contador);
        mqtt.publish(TOPIC, payload);
    }
}
```

Léelo como una frase: *prepara la red y apunta al broker; luego, para siempre: asegúrate de seguir conectado, deja que la librería haga su trabajo y, cuando hayan pasado dos segundos desde la última vez, incrementa el contador y publícalo*.

Las tres piezas del `loop()` no son intercambiables. La reconexión va primero porque publicar sin conexión no hace nada. `mqtt.loop()` va siempre, pase lo que pase, incluso en las vueltas en las que no toca publicar. Y el bloque temporizado va con `millis()` y no con `delay(2000)` justamente para que las dos primeras piezas puedan ejecutarse miles de veces entre publicación y publicación.

---

## Errores típicos

- **Olvidar `mqtt.loop()`.** No llega ningún mensaje al callback y la conexión se cae sola a los pocos segundos. Es el fallo número uno de `PubSubClient`.
- **Usar el mismo clientId en dos placas.** El broker solo admite uno: se echan mutuamente y ninguna consigue estar conectada. Sufijo aleatorio y listo.
- **Tratar el payload del callback como una cadena.** Llega como `byte*` más `length`, **sin `\0`**. Hay que reconstruirlo byte a byte, o leerás basura.
- **Meter `delay()` largos en el `loop()`.** Bloquear la placa corta la conexión MQTT. Temporiza con `millis()`.
- **Olvidar el header `Content-Type: application/json`.** La petición llega, pero el servidor no interpreta el cuerpo como JSON y responde con un error de validación.
- **Confundir un código HTTP de error con un fallo de red.** Un valor negativo significa que no hubo conexión; un 4xx o 5xx significa que sí la hubo y el servidor no aceptó la petición.
- **Publicar en un topic demasiado genérico de un broker público.** Verás mensajes de otras personas y otras personas verán los tuyos.
- **Mandar el número sin convertirlo a texto.** MQTT transporta bytes: el entero se formatea antes de publicarlo.
- **Intentar conectar el ESP32 a una red de 5 GHz.** No la ve. Solo 2.4 GHz.

---

## Preguntas para pensar

- Si tuvieras 50 sensores mandando una lectura por segundo, ¿abrirías 50 conexiones HTTP o los engancharías a un broker MQTT? ¿Qué se rompe primero en cada caso?
- ¿Quién recibe lo que publica una placa si en ese momento no hay nadie suscrito? ¿Se pierde el mensaje? (busca qué son los mensajes *retained* y los niveles de *QoS*)
- Si dos placas se suscriben al mismo topic, ¿reciben las dos el mensaje o se lo reparten? ¿Y si las dos publican en el mismo topic?
- El broker de los ejercicios es público. ¿Qué podría hacer alguien que se suscriba a tu topic? ¿Y si publica él en el topic al que escucha tu placa?
- ¿Por qué `PubSubClient` necesita que le pases un `WiFiClient` en vez de conectarse él mismo al WiFi?
- Tu placa manda una lectura y no aparece en el servidor. ¿Cómo distingues si el problema es el WiFi, el DNS, la URL o el formato del cuerpo?

---

## Ejercicios

- [[Curso_Arduino/practica/10-esp32-iot-mqtt/ej01|Ej 01 — Publicar un contador a un topic MQTT (verde)]]
- [[Curso_Arduino/practica/10-esp32-iot-mqtt/ej02|Ej 02 — Suscribirse a un topic y encender el LED (verde)]]
- [[Curso_Arduino/practica/10-esp32-iot-mqtt/ej03|Ej 03 — Enviar una lectura como JSON por HTTP POST (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/09-esp32-wifi]]
- A partir de aquí el curso deja de practicar piezas sueltas y las junta: el siguiente paso es el proyecto integrador, una estación de sensores que lee de verdad (módulos 04, 06 y 08), decide qué hacer con los datos y los manda por WiFi a un servidor propio, que es exactamente el JSON del ejercicio 03 llegando a un endpoint de FastAPI en vez de a `httpbin`. Todo lo de este módulo vuelve allí: el temporizado con `millis()`, la reconexión, la elección entre publicar a un broker o hacer POST a una API, y la conversación pendiente sobre credenciales y TLS.
