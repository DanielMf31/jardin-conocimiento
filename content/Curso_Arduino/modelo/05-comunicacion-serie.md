---
title: "Módulo 05 — Comunicación serie"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/comunicacion-serie, programacion/depuracion]
aliases: [serial, monitor-serie, Serial.print, Serial.available, mini-cli-arduino, modulo-05-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/05-comunicacion-serie.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/05-comunicacion-serie.md (se regenera con gen_course.py). -->

# Módulo 05 — Comunicación serie

## Idea central

Hasta ahora la placa era muda: hacía cosas, pero no contaba nada. El mismo cable USB por el que la programas es también un canal de conversación en las dos direcciones. Con dos funciones (`Serial.print` para hablar y `Serial.read` para escuchar) el Arduino pasa de ser una caja que parpadea a algo con lo que se dialoga: te dice lo que está pensando y obedece las órdenes que le escribes.

---

## Qué aprendes

- Qué es el puerto serie, qué son los baudios y por qué los dos extremos tienen que ir a la misma velocidad.
- Abrir el canal con `Serial.begin(9600)` e imprimir con `Serial.print` y `Serial.println`.
- Usar la impresión por serie como la herramienta número uno de depuración.
- Leer datos que llegan del PC: el buffer, `Serial.available()` y `Serial.read()`.
- Leer una línea completa con `Serial.readStringUntil('\n')` y limpiarla con `trim()`, para construir una mini-CLI de comandos.
- Leer números con `Serial.parseInt()` y devolver un eco de lo que la placa ha entendido.

---

## Explicación

### El puerto serie: una conversación por el cable USB

Cuando conectas la placa al ordenador, ese cable USB hace dos trabajos: le da corriente y transporta una **comunicación serie** (UART). "Serie" significa que los datos viajan **de uno en uno**, bit tras bit por un solo hilo en cada sentido, en vez de viajar todos a la vez por muchos hilos en paralelo. Es más lento en teoría y muchísimo más barato en cables, y para mandar texto sobra.

La conversación es bidireccional y simétrica:

| Sentido | Quién habla | Con qué |
|---|---|---|
| Placa → PC | el sketch | `Serial.print`, `Serial.println` |
| PC → placa | tú, en el monitor serie | `Serial.available`, `Serial.read`, `Serial.readStringUntil`, `Serial.parseInt` |

El **monitor serie** es la ventana del IDE (o de Wokwi) donde ves lo que la placa escribe y desde donde le escribes tú. No es parte del programa: es el otro extremo del cable.

### Baudios: ponerse de acuerdo en la velocidad

Los dos extremos de un enlace serie tienen que acordar **a qué ritmo** se mandan los bits. Esa velocidad se mide en **baudios** (bits por segundo aproximadamente) y en este curso siempre son **9600**.

```cpp
void setup() {
    Serial.begin(9600);   // abre el canal a 9600 baudios
}
```

`Serial.begin` va en `setup()`, porque abrir el canal se hace una vez. Si lo olvidas, el programa compila y funciona, pero **no sale nada** por el monitor: es el fallo más habitual de este módulo.

El segundo fallo es igual de común: el sketch abre a 9600 y el desplegable del monitor serie está en otro valor (115200, por ejemplo). Entonces el monitor interpreta los bits con un reloj distinto al que se enviaron y aparece **texto basura**, símbolos raros que no significan nada. No es un fallo del código: cuadra los baudios abajo a la derecha del monitor y el texto se arregla solo.

### Hablar: print y println

```cpp
Serial.print("Contador = ");   // escribe y deja el cursor donde está
Serial.println(contador);      // escribe y añade un salto de línea ('\n')
```

La única diferencia entre las dos es ese salto de línea final. Con `print` vas componiendo una línea a trozos y con `println` la cierras. Si usas `println` para todo, cada trozo cae en una línea distinta; si no usas `println` nunca, todo sale pegado en una única línea interminable.

Ambas aceptan texto entre comillas, números, variables, resultados de cuentas. Un número se convierte automáticamente a los caracteres que lo representan: `Serial.println(65)` escribe los dos caracteres `6` y `5`.

Conviene saber que existe `Serial.write()`, que es otra cosa: manda el **byte** crudo. `Serial.write(65)` no escribe "65", escribe el carácter cuyo código es 65, que es la letra `A`. En este curso se usan siempre `print` y `println`, que son las que dan texto legible.

### El serie como herramienta de depuración

Esta es la razón principal por la que este módulo importa. Un microcontrolador no tiene pantalla ni depurador paso a paso a mano: cuando algo no funciona, no puedes "mirar dentro". Imprimir por serie es la manera de ver qué está pensando el programa.

```cpp
Serial.print("valor leido = ");
Serial.println(analogRead(A0));
```

Con dos líneas así, dentro de un `if` que no se cumple o justo antes de una decisión rara, se resuelven la mayoría de los misterios. La técnica es siempre la misma: sospechas de un valor, lo imprimes, y compruebas si la placa está viendo lo que tú crees que está viendo. La mayoría de las veces no lo está, y ahí estaba el fallo.

### Escuchar: el buffer y Serial.available()

Recibir es más delicado que enviar, porque los datos del PC llegan **cuando llegan**, no cuando al `loop()` le conviene. Para que no se pierdan, la placa los va guardando en un **buffer**: una pequeña memoria de espera donde los caracteres recibidos se acumulan hasta que alguien los recoja.

`Serial.available()` devuelve **cuántos caracteres hay esperando** en ese buffer. `Serial.read()` saca **uno** y lo elimina del buffer. De ahí el patrón que se repite en todo el módulo:

```cpp
void loop() {
    if (Serial.available() > 0) {    // ¿hay algo que leer?
        char c = Serial.read();      // saca un carácter
        // ...decidir qué hacer con c
    }
}
```

Preguntar primero no es una formalidad: si llamas a `Serial.read()` con el buffer vacío, devuelve `-1`, que no es ningún carácter que hayas escrito, y a partir de ahí el programa toma decisiones sobre un dato que nunca existió. Como el `loop()` da millones de vueltas por segundo y tú escribes una vez cada varios segundos, la inmensa mayoría de las vueltas el buffer está vacío: sin el `if`, casi todas las lecturas serían basura.

Fíjate también en que `Serial.read()` devuelve un `char`, un carácter, no un número. Lo que llega cuando pulsas la tecla 1 es el carácter `'1'`, con comillas simples, no el valor `1`. Por eso las comparaciones se escriben `if (c == '1')`.

### Escuchar líneas enteras: readStringUntil y trim

Un carácter suelto sirve para órdenes de una tecla, pero no para comandos como `led on`. Para eso hay que leer **hasta el final de la orden**, y el final de una orden es el Enter, que viaja como el carácter de salto de línea `'\n'`.

```cpp
String linea = Serial.readStringUntil('\n');   // lee y acumula hasta encontrar '\n'
linea.trim();                                  // quita espacios y '\r' de los extremos
```

`readStringUntil` va sacando caracteres del buffer y los junta en un `String` hasta encontrar el delimitador que le pides (aquí `'\n'`), que consume pero no incluye en el resultado.

Aquí aparece el detalle que más quebraderos de cabeza da: **el monitor serie tiene que enviar ese `'\n'`**. En el IDE de Arduino hay un desplegable con las opciones "Sin ajuste de línea", "Nueva línea", "Retorno de carro" y "Ambos NL & CR". Si está en "Sin ajuste de línea", al pulsar Enviar solo se manda tu texto y nunca llega el delimitador. Elige **"Nueva línea"**.

Y si el monitor manda "Ambos NL & CR", antes del `'\n'` viene un `'\r'` (retorno de carro) que sí acaba dentro del `String`. Tu comando pasa a ser `"led on\r"`, que **no** es igual a `"led on"`, y la comparación falla por un carácter invisible. `trim()` existe justo para esto: elimina los espacios y caracteres de control de los dos extremos del texto. Cuesta una línea y te ahorra una tarde de desconcierto.

### Leer números: parseInt

Cuando lo que quieres no es un comando sino una cifra, `Serial.parseInt()` recorre el buffer, descarta lo que no sean dígitos y devuelve el primer número entero que encuentra.

```cpp
int brillo = Serial.parseInt();
brillo = constrain(brillo, 0, 255);   // lo encierra en el rango válido
```

Dos avisos sobre `parseInt`. El primero: **solo entiende números**. Si escribes texto, no hay número que extraer y devuelve `0`, así que "hola" acaba apagando el LED en vez de dar un error. El segundo: lo que devuelve es un entero cualquiera, y si lo mandas a `analogWrite` sin comprobarlo, un `999` o un `-5` no significan nada como valor de PWM. `constrain(valor, min, max)` recorta el valor al intervalo: por debajo devuelve el mínimo, por encima el máximo, y en medio lo deja igual.

### El eco: confirmar lo que se ha entendido

Cuando la placa recibe una orden, conviene que **conteste** con lo que ha entendido:

```cpp
Serial.print("Eco -> brillo = ");
Serial.println(brillo);
```

Eso es un **eco**. No es decoración: separa dos fallos que desde fuera se parecen mucho. Si escribes `128`, el eco dice `128` y el LED no cambia de brillo, el problema está en el montaje o en el pin. Si el eco dice `0`, el problema está en lo que se ha recibido o interpretado. Sin eco, tendrías un LED que no hace lo esperado y ninguna pista de por qué.

---

## El montaje: casi nada, y un LED de apoyo

El protagonista de este módulo es software: el monitor serie. El **cable USB ya es el canal serie**, así que el ejercicio 01 no necesita montar absolutamente nada.

Del ejercicio 02 en adelante hace falta un LED, no porque el serie lo requiera, sino para **ver físicamente** que un comando recibido por el cable tiene efecto en el mundo real. Con una protoboard, un LED de 5 mm, una resistencia de 220 Ω y un par de cables Dupont vas sobrado para todo el módulo.

```
UNO pin 8 ──[ 220Ω ]──►|── GND        (ej02 y ej03: encendido/apagado)
UNO pin 9 ──[ 220Ω ]──►|── GND        (ej04: pin PWM, marcado con ~)
                        LED
                 (▲ patilla larga = ánodo hacia la resistencia)
```

Las reglas del módulo 01 siguen valiendo enteras: la resistencia de 220 Ω **nunca** se omite, la patilla larga (ánodo) va hacia la resistencia y la corta (cátodo) a GND, y sin la vuelta a GND no circula nada. La única novedad es el pin: los ejercicios 02 y 03 usan el **pin 8**, que solo tiene que encender y apagar; el 04 usa el **pin 9**, que lleva la marca `~` y por tanto admite PWM, porque ahí hay que graduar el brillo.

Si no tienes el kit físico, cada ejercicio tiene su versión en Wokwi dentro de `wokwi/<ej>/`, con monitor serie integrado y gratis.

---

## Worked example: contar en voz alta

```cpp
int contador = 0;                       // variable que va a ir creciendo

void setup() {
    Serial.begin(9600);                 // abre el puerto serie a 9600 baudios
    Serial.println("Arduino listo.");   // mensaje inicial + salto de línea
}

void loop() {
    Serial.print("Contador = ");        // print NO añade salto de línea
    Serial.println(contador);           // println SÍ lo añade
    contador = contador + 1;
    delay(1000);                        // una línea por segundo
}
```

Léelo como una frase: *abre el canal y saluda una vez; luego, para siempre: escribe la etiqueta, escribe el número, súmale uno y espera un segundo*.

Hay tres cosas que merecen atención. La primera: `Serial.begin` y el saludo están en `setup()` porque son preparación, mientras que la impresión repetida vive en `loop()`. La segunda: la combinación `print` + `println` produce **una línea limpia por vuelta**, `Contador = 0`, `Contador = 1`, `Contador = 2`; con dos `println` saldrían cuatro líneas por vuelta, y con dos `print` una sola línea infinita. La tercera: `contador` se declara **fuera** de las dos funciones, porque una variable declarada dentro de `loop()` se crearía de cero en cada vuelta y siempre valdría 0. Es la primera vez en el curso que hace falta que algo **sobreviva** de una vuelta a la siguiente.

Sin el `delay(1000)` el programa seguiría siendo correcto, pero escupiría miles de líneas por segundo y el monitor sería ilegible.

---

## Errores típicos

- **Olvidar `Serial.begin()` en `setup()`.** El programa funciona pero el monitor está vacío. Es lo primero que hay que mirar cuando "no sale nada".
- **Baudios descuadrados.** El sketch abre a 9600 y el monitor está en otro valor: salen símbolos ilegibles. Ajusta el desplegable del monitor a 9600.
- **Leer sin comprobar `Serial.available()`.** Con el buffer vacío, `Serial.read()` devuelve `-1` y el programa decide sobre un dato inventado.
- **Comparar con un número en vez de con un carácter.** Lo que llega al pulsar la tecla 1 es `'1'`, no `1`. Se compara `c == '1'`.
- **El monitor no envía `'\n'`.** Con "Sin ajuste de línea", `readStringUntil('\n')` no encuentra nunca el delimitador. Selecciona "Nueva línea".
- **El `'\r'` invisible.** Con "Ambos NL & CR" el comando llega como `"led on\r"` y no coincide con `"led on"`. Para eso está `trim()`.
- **Confundir `print` con `write`.** `Serial.print(65)` escribe "65"; `Serial.write(65)` manda el byte 65, que es la letra `A`.
- **Esperar que `parseInt` lea texto.** Solo extrae números; si no hay ninguno, devuelve `0` sin avisar.
- **Mandar a `analogWrite` un número sin recortar.** Un `999` o un `-5` no son valores de PWM válidos: `constrain(brillo, 0, 255)`.
- **Imprimir dentro del `loop()` sin ningún `delay`.** Miles de líneas por segundo hacen el monitor inservible.

---

## Preguntas para pensar

- ¿Por qué hay que preguntar `Serial.available()` antes de `Serial.read()`, si el `loop()` va a volver a pasar por ahí de todas formas dentro de un microsegundo?
- ¿Qué diferencia hay entre `Serial.print(65)` y `Serial.write(65)`? ¿Cuándo querrías la segunda?
- En la mini-CLI, ¿qué pasa exactamente si el monitor no manda `'\n'` al final? ¿Y por qué `trim()` salva tantos casos aunque no arregle ese?
- ¿Para qué sirve el eco del ejercicio 04, si el usuario ya sabe lo que ha escrito?
- Si `Serial.readStringUntil` se queda esperando el delimitador, ¿qué le pasa al resto del programa mientras tanto? ¿Se parece esto al problema de `delay`?
- ¿Cómo comprobarías, imprimiendo por serie, si un `if` que "no funciona" se está ejecutando o no?

---

## Ejercicios

- [[Curso_Arduino/practica/05-comunicacion-serie/ej01|Ej 01 — Contador por el monitor serie (verde)]]
- [[Curso_Arduino/practica/05-comunicacion-serie/ej02|Ej 02 — Encender un LED con '1' y '0' (verde)]]
- [[Curso_Arduino/practica/05-comunicacion-serie/ej03|Ej 03 — Mini-CLI de comandos por serie (amarillo)]]
- [[Curso_Arduino/practica/05-comunicacion-serie/ej04|Ej 04 — Brillo por PWM con parseInt y eco (amarillo)]]

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo anterior: [[Curso_Arduino/modelo/04-entradas-analogicas]]
- Módulo siguiente: [[Curso_Arduino/modelo/06-sensores-comunes]]
- El serie es el puente hacia todo lo que viene después: primero para leer sensores y ver sus valores en pantalla, y más adelante para que la placa hable por WiFi con un servidor, donde la conversación es la misma idea con otro cable (o sin cable).
