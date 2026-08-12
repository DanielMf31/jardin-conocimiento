---
title: "Onboarding — montar el entorno del curso de Arduino"
date: 2026-08-12
tags: [programacion/arduino, curso/arduino, electronica/herramientas]
aliases: [onboarding-arduino, wokwi-vscode, instalar-wokwi, modulo-00-arduino]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-arduino/modelo/00-onboarding.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-arduino/modelo/00-onboarding.md (se regenera con gen_course.py). -->

# Onboarding — montar el entorno del curso de Arduino

## Idea central

Para hacer este curso **no necesitas comprar una placa**. Todos los ejercicios se pueden simular: escribes el mismo código que escribirías para una placa real y ves el circuito funcionar en pantalla, con sus LEDs encendiéndose y su monitor serie. El simulador se llama **Wokwi** y se usa de dos maneras: en el navegador, sin instalar nada, o dentro de VS Code, que es la forma cómoda si vas a hacer el curso entero.

---

## Qué aprendes

- Qué hace falta para ejecutar un ejercicio, con placa y sin ella.
- Cómo simular en el navegador en un minuto, sin instalar nada.
- Cómo montar VS Code con la extensión de Wokwi y activar su licencia gratuita.
- Qué son el `diagram.json` y el `wokwi.toml`, y por qué hacen falta los dos.

---

## Las dos vías, y cuál te conviene

| | En el navegador | En VS Code |
|---|---|---|
| Instalar algo | No | VS Code + extensión + licencia (una vez) |
| Empezar cuesta | Un minuto | Un cuarto de hora |
| Para qué es buena | Probar un ejercicio suelto, o trabajar desde un ordenador que no es tuyo | Hacer el curso entero: tienes el código, el circuito y el monitor serie en la misma ventana |

Si solo quieres curiosear un ejercicio, ve al navegador. Si vas a seguir el curso, monta VS Code una vez y olvídate.

---

## Vía 1 — simular en el navegador

Cada nota de ejercicio del curso trae dos cosas que necesitas: el **código** y el **circuito** (un bloque `diagram.json` plegado, al final de la nota).

1. Entra en [wokwi.com](https://wokwi.com) y crea un proyecto nuevo de la placa que pida el ejercicio: **Arduino UNO** en los módulos 01 a 08, **ESP32** en el 09 y el 10.
2. En la pestaña `sketch.ino`, borra el código de ejemplo y pega el tuyo (o la solución del ejercicio).
3. Abre la pestaña `diagram.json`, borra lo que haya y pega el circuito que viene en la nota.
4. Pulsa el botón de play.

Eso es todo: no hay que compilar nada a mano, Wokwi lo hace por ti.

---

## Vía 2 — simular dentro de VS Code

### Paso 1: instalar VS Code

Descárgalo de [code.visualstudio.com](https://code.visualstudio.com) e instálalo. En Ubuntu también sirve `sudo snap install code --classic`.

Comprueba que el comando `code` funciona desde la terminal (`code --version`). El curso lo usa en algunos atajos; si no lo tienes, abre las carpetas a mano y no pasa nada.

### Paso 2: instalar la extensión de Wokwi

En VS Code, abre el panel de extensiones (`Ctrl+Shift+X`) y busca **"Wokwi for VS Code"**. También puedes instalarla desde la terminal:

```bash
code --install-extension wokwi.wokwi-vscode
```

### Paso 3: activar la licencia gratuita

La extensión es gratis para uso personal, pero pide activar una licencia una sola vez:

1. Pulsa `F1` (o `Ctrl+Shift+P`) y escribe **Wokwi: Request a new License**.
2. VS Code te pedirá permiso para abrir el navegador. Acepta.
3. En la página que se abre, pulsa **GET YOUR LICENSE**. Si no tienes cuenta, créala (es gratis).
4. Confirma la transferencia de la licencia: puede que tengas que aceptar tanto en el navegador como en VS Code.
5. Sabrás que ha ido bien porque VS Code muestra **"License activated for [tu nombre]"**.

La licencia queda guardada; no hay que repetir esto nunca más en ese ordenador.

### Paso 4: montar el repo del curso

```bash
git clone <url-del-repo> curso-arduino
cd curso-arduino
./instalar.sh
```

`instalar.sh` instala la toolchain (`arduino-cli` con los cores de Arduino UNO y ESP32 y las librerías que usa el curso) y copia los esqueletos de práctica a `mi-trabajo/`, que es tu zona de trabajo y nunca se sobrescribe.

### Paso 5: lanzar tu primera simulación

```bash
make list                          # ver los ejercicios disponibles
make sim EJ=01-fundamentos/ej01    # cargar el primero
```

Y en VS Code: `F1` → **Wokwi: Start Simulator**. Deberías ver una placa Arduino UNO con su LED parpadeando.

Merece la pena asignarle un atajo de teclado a ese comando (por ejemplo `F6`): lo vas a usar en cada ejercicio.

---

## Qué son el diagram.json y el wokwi.toml

La extensión de Wokwi necesita dos ficheros, y confundirlos es la causa habitual de que "no arranque":

- **`diagram.json`** describe el **circuito**: qué componentes hay y cómo están cableados entre sí. Es lo que ves en pantalla.
- **`wokwi.toml`** describe **qué firmware ejecutar**: la ruta al binario ya compilado (`firmware`) y, opcionalmente, al fichero de símbolos (`elf`). Las rutas van con barras normales `/` y son relativas a la raíz de la carpeta que tienes abierta en VS Code.

Aquí está la trampa que descoloca a todo el mundo: **la extensión de Wokwi no compila**. Solo simula un firmware que ya existe. De compilarlo se encarga el `make sim` del curso, que además genera el `wokwi.toml` apuntando al binario correcto. Si le das a "Start Simulator" sin haber hecho `make sim`, se quejará de que no encuentra el firmware.

---

## Si algo no funciona

- **"No firmware found" o similar** — no has compilado. Ejecuta `make sim EJ=<modulo>/<ej>` antes de arrancar el simulador.
- **`arduino-cli: command not found`** — la toolchain se instala en `~/.local/bin`. Añádelo a tu `PATH` (el `Makefile` del curso ya lo hace por su cuenta).
- **El simulador arranca pero es otro circuito** — `make sim` carga el ejercicio elegido en la raíz del repo. Vuelve a lanzarlo con el `EJ=` correcto.
- **Los módulos 09 y 10 tardan un montón la primera vez** — es normal: el firmware de ESP32 es grande y su toolchain también. La primera compilación puede irse a un buen rato; las siguientes van rápidas.
- **Quieres usar placa real** — abre el `.ino` en el Arduino IDE, elige placa y puerto y pulsa Subir. Para acceder al puerto serie en Linux, una vez: `sudo usermod -aG dialout $USER` y vuelve a entrar en la sesión.

---

## Conexiones

- [[Curso_Arduino/00_README]]
- Módulo siguiente: `[[Curso_Arduino/modelo/01-fundamentos]]`
