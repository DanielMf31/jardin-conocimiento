---
title: "Módulo 01 — Fundamentos y GPIO digital"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/gpio, programacion/fundamentos]
aliases: [gpio-digital, setup-loop, pinMode, digitalWrite, modulo-01-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/01-fundamentos.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/01-fundamentos.md (se regenera con gen_course.py). -->

# Módulo 01 — Fundamentos y GPIO digital

## Idea central

Un microcontrolador no "corre un programa y termina": arranca, hace una preparación **una sola vez** y luego repite el mismo bloque de instrucciones para siempre, millones de veces. Sobre ese ciclo infinito se construye todo lo demás. Y la operación más elemental que sabe hacer es poner un pin a **5 voltios** o a **0 voltios**. Encender un LED no es más que eso.

---

## Qué aprendes

- El modelo mental de `setup()` y `loop()`, y por qué el código se escribe en uno o en otro.
- Qué es un pin digital y qué significa que esté en HIGH o en LOW.
- Configurar un pin como salida con `pinMode` y accionarlo con `digitalWrite`.
- Temporizar con `delay`, y por qué eso va a ser un problema más adelante.
- Montar un LED con su resistencia sin quemar nada.

---

## Explicación

### El ciclo: setup y loop

Todo sketch de Arduino tiene exactamente dos funciones obligatorias:

```cpp
void setup() {
    // se ejecuta UNA vez, al encender o resetear la placa
}

void loop() {
    // se ejecuta una y otra vez, sin parar, mientras haya corriente
}
```

`setup()` es la preparación: aquí dices cómo va a usarse cada pin, arrancas la comunicación serie, inicializas pantallas. Cosas que se hacen una vez y ya está.

`loop()` es el comportamiento: lo que la placa hace continuamente. Cuando llega al final de `loop()`, vuelve a empezar por arriba. No hay un `main()` que decida cuándo parar, porque un microcontrolador no está pensado para terminar: está pensado para estar encendido.

De aquí sale el error más común del módulo: poner el parpadeo en `setup()`. El LED se enciende y se apaga una vez, tan rápido que no lo ves, y luego no pasa nada más. El parpadeo vive en `loop()` porque el parpadeo es repetición.

### El pin digital: dos estados y nada más

Un **pin digital** solo entiende dos valores:

| Valor | Tensión en el pin (Arduino UNO) | Significado |
|---|---|---|
| `HIGH` | 5 V | hay corriente |
| `LOW` | 0 V | no hay corriente |

No hay término medio. Un pin digital no sabe poner "medio voltio" ni "3 voltios": eso es el módulo 03 (PWM) y el 04 (entradas analógicas). Aquí, encendido o apagado.

En el Arduino UNO, los pines digitales van numerados del 0 al 13. El pin 13 tiene además un LED soldado en la propia placa, el **LED integrado**, que en el código se llama `LED_BUILTIN`. Es perfecto para el primer contacto: no hay que montar nada.

### Declarar la intención: pinMode

Antes de usar un pin hay que decir si va a mandar corriente (salida) o a leerla (entrada). Eso se hace **una vez**, en `setup()`:

```cpp
void setup() {
    pinMode(8, OUTPUT);      // el pin 8 va a mandar corriente
}
```

Si te saltas el `pinMode`, el comportamiento es errático: el pin queda en un estado indefinido y el LED puede parpadear débilmente, encenderse a medias o no hacer nada. No da un error de compilación, así que es un fallo difícil de ver. Cuando algo "casi funciona", lo primero que hay que mirar es si falta el `pinMode`.

### Accionar el pin: digitalWrite

```cpp
digitalWrite(8, HIGH);   // pin 8 a 5V  -> LED encendido
digitalWrite(8, LOW);    // pin 8 a 0V  -> LED apagado
```

Nada más. `digitalWrite` es instantáneo: en cuanto la instrucción se ejecuta, la tensión del pin cambia.

### Esperar: delay

```cpp
delay(1000);   // no hacer nada durante 1000 milisegundos = 1 segundo
```

`delay` recibe **milisegundos**: `delay(1000)` es un segundo, `delay(500)` medio, `delay(50)` una vigésima parte. Con esta pieza ya se puede hacer un parpadeo, que es encender, esperar, apagar, esperar.

Hacen falta **dos** `delay` y no uno: si solo esperas después de encender, la placa apaga el LED y vuelve inmediatamente al principio del `loop()` para encenderlo otra vez. El LED estaría apagado unos microsegundos, invisibles, y lo verías encendido todo el rato.

Merece la pena que quede claro desde ya: `delay` **congela la placa entera**. Durante ese segundo el microcontrolador no puede leer un botón, ni atender un sensor, ni nada. Para un LED que parpadea da igual; en cuanto quieras leer un botón mientras algo parpadea, se convierte en un problema. Esa es la puerta al módulo 02.

### Dar nombre a los pines

En cuanto hay más de un LED, referirse a ellos por su número se vuelve ilegible y frágil:

```cpp
const int LED_A = 8;         // mucho mejor que escribir 8 por todas partes
const int LED_B = 9;
```

`const int` declara un valor con nombre que no va a cambiar. Si mañana mueves el LED del pin 8 al 7, cambias una línea en vez de buscar todos los `8` del fichero (y de acertar cuáles eran el pin y cuáles otra cosa).

---

## El montaje: LED y resistencia

Un LED es un diodo: deja pasar la corriente en **un solo sentido** y casi no ofrece resistencia. Conectado directamente entre un pin y masa, deja pasar toda la corriente que puede, y eso le quema a él y castiga al pin de la placa. Por eso siempre va acompañado de una **resistencia** que limita esa corriente.

```
UNO pin 8 ──[ 220Ω ]──►|── GND
                        LED
                 (▲ patilla larga = ánodo hacia la resistencia)
```

Dos cosas que hay que interiorizar:

- **La resistencia de 220 Ω no es opcional.** Sin ella el LED brilla muchísimo un rato y luego se muere, y el pin sufre.
- **El LED tiene polaridad.** La patilla **larga** es el **ánodo** (el `+`, va hacia la resistencia y el pin); la **corta** es el **cátodo** (el `−`, va a GND). Al revés no se rompe, simplemente no enciende. Si un LED no se enciende, gíralo antes de dudar del código.

La corriente sale del pin, atraviesa la resistencia, atraviesa el LED y vuelve a la placa por **GND** (masa). Si no cierras ese camino de vuelta a GND, no circula nada.

---

## Worked example: el parpadeo mínimo

```cpp
void setup() {
    pinMode(LED_BUILTIN, OUTPUT);     // el pin del LED, configurado como SALIDA
}

void loop() {
    digitalWrite(LED_BUILTIN, HIGH);  // 5V -> LED encendido
    delay(1000);                      // esperar 1000 ms = 1 s
    digitalWrite(LED_BUILTIN, LOW);   // 0V -> LED apagado
    delay(1000);
}
```

Léelo como una frase: *prepara el pin del LED como salida; luego, para siempre: enciéndelo, espera un segundo, apágalo, espera un segundo*.

Este programa no necesita ningún montaje, porque `LED_BUILTIN` es el LED que la placa ya lleva soldado. Es el "hola mundo" de los microcontroladores, y aunque parezca tonto, contiene ya todas las ideas del módulo: preparación única, ciclo infinito, pin en dos estados y tiempo.

---

## Errores típicos

- **Olvidar la resistencia.** El LED brilla exageradamente y se degrada; el pin sufre. Siempre 220 Ω en serie.
- **El LED al revés.** No enciende y el código parece correcto. Gira el LED (patilla larga hacia la resistencia).
- **Olvidar `pinMode` en `setup()`.** Comportamiento errático sin ningún mensaje de error.
- **Poner el parpadeo en `setup()`.** Ocurre una vez, invisible. La repetición va en `loop()`.
- **Un solo `delay`.** El LED parece encendido siempre. Hacen falta dos: uno para el encendido y otro para el apagado.
- **Olvidar GND.** Sin camino de vuelta a masa no circula corriente y no pasa nada.
- **Escribir los números de pin a pelo** en un montaje con varios LEDs. Usa `const int` con nombres.

---

## Preguntas para pensar

- ¿Por qué hay dos `delay` en el parpadeo y no uno?
- ¿Qué verías con `delay(50)` en vez de `delay(1000)`? (pruébalo en el simulador)
- En un semáforo, ¿por qué hay que **apagar** el LED anterior y no basta con encender el nuevo?
- Si `delay` congela la placa, ¿cómo harías para leer un botón mientras un LED parpadea?

---

## Ejercicios

- [[Curso_Arduino/practica/01-fundamentos/ej01|Ej 01 — Parpadear el LED integrado de la placa (verde)]]
- [[Curso_Arduino/practica/01-fundamentos/ej02|Ej 02 — Parpadear un LED externo en el pin 8 (verde)]]
- [[Curso_Arduino/practica/01-fundamentos/ej03|Ej 03 — Dos LEDs que se alternan (verde)]]
- [[Curso_Arduino/practica/01-fundamentos/ej04|Ej 04 — Semáforo: rojo, verde, amarillo (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Antes de empezar: `[[Curso_Arduino/modelo/00-onboarding]]`
- Módulo siguiente: [[Curso_Arduino/modelo/02-entradas-digitales]] — botón, `digitalRead`, `INPUT_PULLUP` y antirrebote. Ahí se ve por qué `delay` estorba en cuanto hay que atender algo mientras pasa el tiempo.
