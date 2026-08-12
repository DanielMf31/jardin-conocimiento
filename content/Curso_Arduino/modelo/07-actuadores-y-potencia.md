---
title: "Módulo 07 — Actuadores y potencia"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/actuadores, electronica/potencia, electronica/motores]
aliases: [actuadores-arduino, servo-arduino, rele-arduino, motor-dc-arduino, buzzer-tone, masa-comun, modulo-07-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/07-actuadores-y-potencia.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/07-actuadores-y-potencia.md (se regenera con gen_course.py). -->

# Módulo 07 — Actuadores y potencia

## Idea central

Hasta ahora la placa ha encendido luces y ha leído sensores: ha manejado **información**. Este módulo es el salto a mover el mundo físico — girar un eje, hacer sonar algo, abrir un contacto, arrancar un motor. Y en cuanto hay movimiento hay **potencia**, que es la idea grande del módulo: un pin del Arduino manda *señales*, no *fuerza*. Un pin da del orden de 20 mA; un motor pide cientos de miliamperios o amperios. Así que la estructura de todo lo que hagamos aquí es siempre la misma: el pin controla un **interruptor de potencia** (un transistor, un MOSFET, un módulo relé) y es una **fuente aparte** la que alimenta la carga, con las **masas unidas**. Aprender eso importa más que cualquier función nueva de este módulo.

---

## Qué aprendes

- Por qué un pin no puede alimentar un motor, y qué números hay detrás de esa afirmación.
- El patrón universal de potencia: pin → driver → carga con fuente propia, y masa común.
- Qué es un servo y por qué se manda en **grados de posición**, no en velocidad ni en HIGH/LOW.
- Hacer sonido con `tone()` y la diferencia entre un buzzer pasivo y uno activo.
- Qué es un relé, qué son sus contactos COM / NA / NC, y por qué muchos módulos son activos en bajo.
- Regular la velocidad de un motor DC con PWM a través de un transistor, con su diodo flyback.

---

## Explicación

### El límite del pin: la idea que gobierna el módulo

Un pin digital del Arduino UNO entrega cómodamente unos **20 mA** (el máximo absoluto ronda los 40 mA, y ahí ya se está maltratando el chip). Un LED con su resistencia de 220 Ω consume unos 15 mA: encaja justo, y por eso los seis módulos anteriores han funcionado enchufando cosas directamente al pin.

Un motor DC pequeño arrancando pide fácilmente **300 mA o más**. Una bobina de relé de potencia, entre 50 y 100 mA. Una tira de LEDs, amperios. Todos esos números están una o dos órdenes de magnitud por encima de lo que el pin puede dar. Conectar cualquiera de ellos al pin no es "que vaya flojo": es que el pin no puede suministrar esa corriente, la tensión se hunde, la placa se resetea sola o el pin se degrada de forma permanente.

Conviene decirlo con el modelo mental correcto: un pin no es una fuente de energía, es un **interruptor lógico diminuto**. Sirve para *decir* cosas, no para *empujar* cosas.

### El patrón de potencia: pin, driver, fuente, masa común

De ese límite sale la única arquitectura válida cuando hay potencia de por medio:

```
              (señal, poca corriente)
   pin ────────────────────────────► DRIVER ──┐
                                              │  (mucha corriente)
   FUENTE EXTERNA + ─────────────────────── CARGA
   FUENTE EXTERNA GND ───────┬───────────────┘
                             │
   GND de la placa ──────────┘   ← MASA COMÚN, no es opcional
```

Tres piezas y una condición:

- El **pin** solo manda la señal de control. Consume lo que consuma esa señal, que es muy poco: unos pocos miliamperios hacia la base de un transistor, o hacia la entrada opto-aislada de un módulo relé.
- El **driver** es el interruptor de potencia: un transistor NPN, un MOSFET, un módulo relé, o un integrado tipo L298N o DRV8833 si hace falta controlar también el sentido de giro. Es la pieza que soporta la corriente de verdad.
- La **fuente externa** alimenta la carga. Pilas, un adaptador, una fuente de laboratorio; lo que sea menos el regulador de la placa.

Y la condición: **masa común**. El GND de la placa y el GND de la fuente externa tienen que estar unidos con un cable. Es el error más silencioso de todo el módulo, porque no rompe nada — simplemente hace que las cosas funcionen "a ratos". La razón es que una tensión no existe por sí sola: siempre es una diferencia respecto a una referencia. Cuando el pin pone 5 V, quiere decir 5 V *respecto al GND de la placa*. Si el transistor tiene su emisor en el GND de la fuente externa y esa masa no está unida a la de la placa, esos 5 V no significan nada para el transistor: no hay una referencia compartida, la señal "flota" y el comportamiento se vuelve aleatorio. Unir las masas es dar a los dos circuitos el mismo cero.

### Cargas inductivas y el diodo flyback

Un motor y la bobina de un relé son **inductivos**: almacenan energía en un campo magnético mientras circula corriente. Cuando cortas esa corriente de golpe, la bobina se niega a que la corriente caiga a cero de repente y responde generando un pico de tensión inverso que puede ser de decenas o cientos de voltios durante un instante. Ese pico va a parar al transistor que acaba de abrir, y lo perfora; o se cuela como ruido por la alimentación y cuelga el microcontrolador.

La solución es un **diodo flyback** (por ejemplo un 1N4007) en paralelo con la carga, montado **al revés** respecto a la alimentación: el cátodo, la patilla marcada con la raya, va al positivo. Así, mientras el motor funciona normalmente el diodo no conduce y es como si no estuviera; en el instante del apagado, la tensión se invierte, el diodo conduce y ofrece a esa corriente un camino cerrado por el que extinguirse suavemente en vez de saltar por encima del transistor. Es un componente de céntimos que evita averías raras y difíciles de diagnosticar.

Cuando el motor va con un driver comercial (L298N, DRV8833) no hace falta añadirlo: el driver ya lleva los diodos dentro.

### El servo: posición, no velocidad

Un servo no es un motor normal. Por dentro tiene un motor pequeño, una reductora y un potenciómetro que le dice en qué ángulo está el eje, más una electrónica que compara el ángulo actual con el pedido y corrige hasta que coinciden. Es decir: es un lazo cerrado, y por eso no se le pide "gira", se le pide **una posición**.

Un servo estándar acepta ángulos de **0 a 180 grados**, y se controla con pulsos periódicos cuya anchura codifica el ángulo. Esa señal la genera la librería `Servo`, que viene con el IDE:

```cpp
#include <Servo.h>

Servo miServo;
const int PIN_SERVO = 9;

void setup() {
    miServo.attach(PIN_SERVO);   // asocia el objeto a un pin
}

void loop() {
    miServo.write(90);           // ir a 90 grados
    delay(500);
}
```

Dos avisos importantes. El primero: `miServo.write(90)` **no tiene nada que ver con `digitalWrite`**. Aquí el segundo argumento son **grados**, no `HIGH`/`LOW` ni un valor de PWM de 0 a 255. Es el mismo verbo con un significado distinto, y confundirlos es un clásico. El segundo: la librería `Servo` se apropia del temporizador que también usa `analogWrite` en los pines **9 y 10** del UNO, así que mientras haya un servo enganchado, esos dos pines pierden el PWM. Si en un montaje mezclas servo y `analogWrite`, mueve los `analogWrite` a otros pines (3, 5, 6 u 11).

Sobre alimentación: un micro servo SG90 suele tolerar el 5 V de la placa mientras esté solo y sin carga, pero en el arranque y al forzar el eje da tirones de corriente que pueden bajar la tensión y resetear el UNO. Con dos servos, o con uno grande, es directamente obligatorio alimentarlos desde una fuente aparte — y otra vez, con la masa unida a la de la placa.

### Sonido: tone() y el buzzer pasivo

Un sonido es una vibración a una frecuencia determinada. `tone()` genera en un pin una onda cuadrada de la frecuencia que le pidas, y esa onda hace vibrar el elemento piezoeléctrico del buzzer:

```cpp
tone(PIN_BUZZER, 440);        // sonar a 440 Hz indefinidamente
tone(PIN_BUZZER, 440, 300);   // sonar a 440 Hz durante 300 ms
noTone(PIN_BUZZER);           // callar
```

La frecuencia es la nota: 262 Hz es un do, 440 Hz el la de referencia, 523 Hz el do de la octava siguiente. Una melodía no es más que una lista de frecuencias y de duraciones.

Aquí importa mucho **qué buzzer tienes**. Un buzzer **pasivo** es un piezo desnudo: no suena por sí solo, hay que darle la onda desde fuera, y por eso puede reproducir cualquier frecuencia. Un buzzer **activo** lleva su propio oscilador dentro: le das tensión y pita, siempre en su única nota. Con un buzzer activo, `tone()` no sirve de nada — pitará igual con 262 Hz que con 523 Hz — y se maneja con `digitalWrite`. Si estás intentando tocar una escala y todas las notas suenan iguales, no busques el fallo en el código: mira el buzzer.

`tone()` no necesita `pinMode`: configura el pin él mismo. Y usa un temporizador interno, el mismo que el PWM de los pines 3 y 11 en el UNO, así que mientras suena una nota esos pines pierden `analogWrite`.

### El relé: un interruptor mecánico mandado por corriente

Un relé es un interruptor de verdad, con contactos metálicos, que se acciona con un electroimán. Le mandas corriente a la bobina, el campo magnético tira de una lámina y el contacto cambia de sitio; ese es el "clic" que se oye. Su gracia es que **el circuito de control y el circuito de potencia están físicamente separados**: puedes conmutar una carga de 230 V con una señal de 5 V sin que exista ninguna conexión eléctrica entre ambos lados.

Un módulo relé típico de un canal tiene dos grupos de pines:

| Lado | Pines | Qué es |
|---|---|---|
| Control | IN, VCC, GND | la señal del Arduino y la alimentación de la bobina |
| Potencia | COM, NA, NC | los contactos por los que pasa la carga |

**COM** es el común, el terminal móvil. **NA** (normalmente abierto) está desconectado de COM mientras el relé está en reposo y se conecta al activarlo. **NC** (normalmente cerrado) es lo contrario: conectado en reposo, se abre al activar. La elección no es un detalle: si quieres que una carga esté apagada cuando el sistema se queda sin corriente, la pones en NA; si quieres que siga funcionando aunque el control muera, en NC.

La carga va **siempre** por COM y NA/NC, con su propia alimentación, y **nunca** por el pin. El pin solo toca IN. Los módulos buenos llevan además un optoacoplador en la entrada, que aísla ópticamente la señal y protege la placa.

Y un detalle que desconcierta a todo el mundo la primera vez: muchos módulos relé son **activos en bajo**. Su entrada IN activa el relé con `LOW` y lo desactiva con `HIGH`, justo al revés de lo intuitivo. Si escribes `HIGH` y el relé clica *al arrancar* en vez de al activarlo, ya sabes cuál tienes: invierte la lógica del código o define una constante `ACTIVO` y úsala en todas partes.

### El motor DC: PWM detrás de un transistor

Un motor DC es el caso más exigente: es inductivo, tira mucha corriente y hay que regular su velocidad. La velocidad se controla con **PWM** — el mismo `analogWrite` del módulo 03 — pero el PWM nunca sale directo al motor: sale a la **base de un transistor**, y es el transistor el que deja pasar o no la corriente de la fuente externa.

El montaje clásico es un NPN (2N2222, BC547) como interruptor de lado bajo:

```
pin 6 (PWM) ──[ 1 kΩ ]── BASE
                          │
   +Vfuente ── MOTOR ── COLECTOR
                 ╫  (diodo flyback en paralelo, cátodo al +)
                       EMISOR ── GND ── (unido al GND de la placa)
```

La resistencia de 1 kΩ limita la corriente que entra por la base; sin ella el pin alimentaría la unión base-emisor sin freno. El motor va entre el positivo de la fuente y el colector, y el emisor a masa. El diodo flyback en paralelo con el motor, cátodo al positivo.

Con esto, `analogWrite(6, 128)` no significa "medio voltio en la base": significa que el pin conmuta muy rápido entre encendido y apagado con un ciclo de trabajo del 50 %, el transistor abre y cierra a esa misma cadencia, y el motor — que por inercia mecánica no puede seguir esos cambios tan rápidos — se comporta como si recibiera la mitad de la energía. Gira a media velocidad.

Un aviso realista: con valores bajos de PWM un motor a menudo no arranca, solo zumba. Vencer el rozamiento estático pide más par que mantener el giro. Por eso, si necesitas velocidades bajas, la técnica habitual es arrancar un instante a `255` y bajar enseguida al valor deseado.

Cuando además quieras **invertir el sentido de giro**, un transistor ya no basta: hace falta un puente en H, que es lo que traen los drivers L298N o DRV8833. La idea es la misma — el pin manda, el driver empuja — solo que con cuatro interruptores en vez de uno.

---

## El montaje: qué necesitas y cómo se conecta

Para el módulo entero hacen falta la placa UNO con su cable, una protoboard y unos diez cables Dupont, más lo específico de cada ejercicio.

**Servo (ej01).** Un micro servo SG90. Tiene tres cables con un código de color bastante estándar: **naranja o amarillo** es la señal y va a un pin PWM (usamos el **9**), **rojo** es V+ y va a 5 V, **marrón o negro** es GND y va a GND. Con un solo servo pequeño y sin carga, el 5 V de la placa suele aguantar; con más de uno, fuente externa y masas unidas.

**Buzzer (ej02).** Un buzzer **pasivo** (piezo). Una pata al pin **8** y la otra a GND; si el tuyo trae marcado el `+`, ese va al pin. Insistimos: un buzzer activo no sirve para melodías.

**Relé (ej03).** Un módulo relé de un canal de 5 V, preferiblemente con optoacoplador. Del lado de control: **IN al pin 7**, **VCC a 5 V**, **GND a GND** de la placa. Del lado de potencia, la carga con su propia alimentación entre COM y NA. En el curso simulamos esa carga con un LED de 5 mm y su resistencia de 220 Ω, para no manejar tensiones peligrosas. En Wokwi el módulo relé no existe como pieza estándar, así que el ejercicio se simula directamente con un LED en el pin 7: el código es idéntico, y lo que se pierde es el clic.

**Motor DC (ej04).** Un motor DC pequeño de 3 a 6 V, un transistor NPN 2N2222 o BC547, una resistencia de 1 kΩ hacia la base, un diodo 1N4007 de flyback y una fuente externa (pilas o adaptador) para el motor. La señal PWM sale del pin **6**. Y el cable que más se olvida: el que une el GND de esas pilas con el GND de la placa.

Sobre seguridad, dos líneas que valen para siempre. La primera: nada que consuma potencia se alimenta desde un pin — driver y fuente aparte, sin excepciones. La segunda: en este curso trabajamos solo a **baja tensión**. Conmutar red eléctrica de 230 V con un relé es perfectamente posible y es lo que hacen los domóticos comerciales, pero es material aislado, con supervisión y con conocimiento previo; no es un ejercicio de clase.

---

## Worked example: el servo que barre de 0 a 180 grados

```cpp
#include <Servo.h>

Servo miServo;
const int PIN_SERVO = 9;

void setup() {
    miServo.attach(PIN_SERVO);
}

void loop() {
    for (int angulo = 0; angulo <= 180; angulo++) {   // subir
        miServo.write(angulo);
        delay(15);
    }
    for (int angulo = 180; angulo >= 0; angulo--) {   // bajar
        miServo.write(angulo);
        delay(15);
    }
}
```

Léelo como una frase: *asocia el servo al pin 9; luego, para siempre: recorre los ángulos de 0 a 180 de uno en uno esperando 15 ms en cada uno, y después vuelve de 180 a 0 igual*.

Lo interesante es de dónde sale la **suavidad**. Si escribieras `miServo.write(0)`, `delay(1000)`, `miServo.write(180)`, el servo daría un latigazo de un extremo al otro tan rápido como pueda su motor. En cambio, mandando 181 posiciones consecutivas separadas 15 ms, cada orden pide un salto de un solo grado y el servo lo cubre sin esfuerzo; el resultado visible es un movimiento continuo. El barrido completo tarda unos 181 × 15 ≈ 2,7 segundos en cada sentido.

Ese `delay(15)` es también el mínimo razonable: el servo necesita un poco de tiempo para llegar. Si lo bajas demasiado, mandas ángulos más deprisa de lo que el eje puede moverse y el barrido se vuelve entrecortado o se acorta. Si lo subes, el movimiento se hace lento y a partir de cierto punto se percibe a saltos, un grado cada vez.

---

## Errores típicos

- **Alimentar el servo o el motor desde un pin.** La tensión se hunde, la placa se resetea o el pin se degrada. Fuente aparte y driver, siempre.
- **Olvidar la masa común** entre la placa y la fuente externa. No rompe nada: hace que todo funcione de forma errática e intermitente, que es peor de diagnosticar.
- **Motor o relé sin diodo flyback.** Chispazos, ruido en la alimentación, el micro que se cuelga sin motivo aparente, y a la larga el transistor perforado.
- **Usar un buzzer activo con `tone()`.** Suena, pero siempre la misma nota. Para melodías hace falta un buzzer pasivo.
- **No comprobar si el módulo relé es activo en bajo.** Pones `HIGH` y no pasa nada, o el relé clica nada más arrancar la placa.
- **Confundir `Servo.write()` con `digitalWrite()`.** El primero recibe grados de 0 a 180; el segundo, `HIGH` o `LOW`. Mismo verbo, significado distinto.
- **Mezclar la librería `Servo` con `analogWrite` en los pines 9 y 10.** El servo se queda con ese temporizador y ahí desaparece el PWM.
- **Esperar que un motor arranque con un PWM bajo.** Con valores pequeños solo zumba: arranca a 255 y baja después.
- **Conectar la carga del relé al pin en vez de a COM/NA.** El relé está justamente para que la carga no toque el Arduino.

---

## Preguntas para pensar

- ¿Por qué un pin no puede mover un motor directamente? Contéstalo con números, no con "no tiene fuerza".
- ¿Qué pasa exactamente si no unes las masas de la placa y de la fuente del motor? ¿Por qué "flota" la señal?
- En el relé, ¿en qué situaciones querrías la carga en NA y en cuáles en NC? Piensa en qué debe ocurrir si el sistema se queda sin corriente.
- ¿Para qué sirve el diodo en paralelo con el motor, y por qué se monta en sentido inverso a la alimentación?
- Un servo tiene un motor dentro. ¿Por qué entonces se le manda un ángulo y no una velocidad?
- Si `tone()` y `Servo` se quedan con temporizadores del chip, ¿qué problema te vas a encontrar el día que quieras un servo, un buzzer y un LED con fade a la vez?

---

## Ejercicios

- [[Curso_Arduino/practica/07-actuadores-y-potencia/ej01|Ej 01 — Barrido de un servo de 0 a 180 grados (verde)]]
- [[Curso_Arduino/practica/07-actuadores-y-potencia/ej02|Ej 02 — Escala musical con buzzer y tone() (verde)]]
- [[Curso_Arduino/practica/07-actuadores-y-potencia/ej03|Ej 03 — Conmutar un relé cada 2 segundos (amarillo)]]
- [[Curso_Arduino/practica/07-actuadores-y-potencia/ej04|Ej 04 — Velocidad de un motor DC con PWM y transistor (rojo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/06-sensores-comunes]]
- Módulo siguiente: [[Curso_Arduino/modelo/08-pantallas]]
