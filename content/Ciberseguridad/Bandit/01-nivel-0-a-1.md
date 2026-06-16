---
title: Bandit Nivel 0 -> 1
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit nivel 0, Bandit 0 a 1, bandit-ssh-intro]
---

# Bandit Nivel 0 -> 1

> Página oficial del nivel: https://overthewire.org/wargames/bandit/bandit1.html
> Marco: OverTheWire Bandit es un wargame **legal y educativo** para aprender terminal Linux. No es hacking malicioso.

---

## Objetivo

Conectarte al servidor de Bandit por SSH como el usuario `bandit0`, localizar un archivo llamado `readme` en su directorio home y leer su contenido para obtener la contraseña del siguiente nivel.

---

## Qué aprendes

- **SSH** — qué es y cómo conectarse a un servidor remoto con usuario, host y puerto.
- **`ls`** — listar archivos y directorios del directorio actual.
- **`cat`** — mostrar el contenido de un archivo de texto en pantalla.
- **Directorio home** — el directorio personal de cada usuario en Linux (normalmente `/home/<usuario>`); al conectarte por SSH, aterrizas directamente en él.
- **Flags de `ssh`** — el flag `-p` para especificar un puerto distinto al 22 por defecto.

---

## Paso a paso

### 1. Conectarte al nivel 0 (el punto de entrada)

Antes de resolver nada, tienes que **entrar al servidor**. Bandit usa SSH (*Secure Shell*: protocolo cifrado para conectarte a un ordenador remoto por red).

```bash
ssh bandit0@bandit.labs.overthewire.org -p 2220
```

Desglose del comando:
- `ssh` — herramienta de conexión remota.
- `bandit0` — el nombre de usuario con el que entras.
- `@bandit.labs.overthewire.org` — el host (servidor) al que te conectas.
- `-p 2220` — el puerto. Por defecto SSH usa el 22; aquí OverTheWire usa el 2220.

**La primera vez** que te conectes a un servidor nuevo, SSH no tiene registrada su huella digital (*fingerprint*). Verás algo así:

```
The authenticity of host '[bandit.labs.overthewire.org]:2220 ([...])'
can't be established.
ED25519 key fingerprint is SHA256:C2ihUBV7ihnV1wUXRb4RrEcLfXC5CXlhmAAM/urerLY.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Escribe `yes` y pulsa Enter. SSH guardará la huella para futuras conexiones.

A continuación te pedirá la contraseña de `bandit0`. La contraseña del nivel 0 es pública: es `bandit0`.

```
bandit0@bandit.labs.overthewire.org's password:
```

Escribe `bandit0` y pulsa Enter. No verás los caracteres mientras escribes (es normal en Linux: la terminal oculta contraseñas).

Si todo va bien, verás el banner de bienvenida de OverTheWire y un prompt como este:

```
bandit0@bandit:~$
```

El `~` indica que estás en el **directorio home** de `bandit0`. Ya estás dentro.

---

### 2. Ver qué hay en el directorio home

```bash
ls
```

Salida esperada:

```
readme
```

`ls` (*list*) lista los archivos y carpetas del directorio actual. Ves un único archivo: `readme`.

---

### 3. Leer el archivo `readme`

```bash
cat readme
```

Salida esperada:

```
<cadena_de_~32_caracteres>
```

> ⚠️ `<cadena_de_~32_caracteres>` es un **placeholder**. Lo que verás en tu terminal será la contraseña real del nivel siguiente (bandit1): una cadena de caracteres alfanuméricos de aproximadamente 32 caracteres. **Cópiala** — la necesitarás para el paso siguiente.

`cat` (*concatenate*) lee el contenido de uno o más archivos y lo vuelca en pantalla. Es la forma más directa de leer un archivo de texto en Linux.

---

## Por qué funciona

### SSH: acceso remoto seguro

SSH (*Secure Shell*) crea un **túnel cifrado** entre tu máquina y el servidor. Todo lo que escribes viaja cifrado, por eso ni la contraseña ni los comandos son visibles por terceros en la red. El servidor se identifica mediante una *fingerprint* (huella criptográfica) para que puedas verificar que te conectas al servidor correcto y no a un impostor (*man-in-the-middle*).

### El directorio home y `~`

En Linux cada usuario tiene un directorio personal en `/home/<usuario>`. El shell lo abrevia como `~`. Cuando SSH te auttentica, te deja directamente en ese directorio. Por eso `ls` sin argumentos muestra los archivos de tu directorio home.

### `ls` y `cat`: los dos comandos más básicos de exploración

| Comando | Para qué sirve | Analogía |
|---|---|---|
| `ls` | Ver qué archivos/carpetas hay | Abrir una carpeta en el explorador de archivos |
| `cat` | Leer el contenido de un archivo | Abrir un archivo de texto con el bloc de notas |

---

## Errores comunes

- **"Connection refused" o "port 22"**: olvidaste el flag `-p 2220`. El servidor no escucha en el puerto 22 por defecto; prueba de nuevo con `-p 2220`.
- **"Permission denied"**: escribiste mal la contraseña o el usuario. Verifica que pones exactamente `bandit0` tanto en el usuario como en la contraseña.
- **El cursor se queda parado tras escribir la contraseña**: la terminal oculta los caracteres de contraseñas. No pasa nada, sigue escribiendo y pulsa Enter.
- **`cat: readme: No such file or directory`**: no estás en el directorio home. Escribe `cd ~` para volver y luego repite `cat readme`.
- **`ls` no muestra nada o muestra algo distinto**: puede que hayas navegado a otro directorio sin darte cuenta. Usa `pwd` para saber dónde estás y `cd ~` para volver al home.
- **Confundir `readme` con `README`**: en Linux los nombres de archivo distinguen mayúsculas de minúsculas. El archivo se llama `readme` en minúsculas.

---

## Pasar al siguiente nivel

Una vez que tienes la contraseña del nivel 1 (la que obtuviste con `cat readme`), sal del servidor actual con:

```bash
exit
```

Y conéctate como `bandit1`:

```bash
ssh bandit1@bandit.labs.overthewire.org -p 2220
```

Cuando te pida la contraseña, introduce `<cadena_de_~32_caracteres>` (la que copiaste del archivo `readme`).

---

## Conexiones

- [[Bandit/00_README]]
- [[MOC_Ciberseguridad]]
- Página oficial del nivel: https://overthewire.org/wargames/bandit/bandit1.html
- Manual de SSH: `man ssh` en tu terminal
- Fundamentos de navegación Linux: `man ls`, `man cat`
