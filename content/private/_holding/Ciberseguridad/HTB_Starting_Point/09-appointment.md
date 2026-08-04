---
title: Appointment (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, sqli, web, autenticacion, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [Appointment HTB, HTB Appointment, sqli-login-bypass]
---

# Appointment — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: SQL Injection (login bypass), reconocimiento web con nmap**

> Este laboratorio es parte de Hack The Box Starting Point, un entorno **legal y autorizado** diseñado para aprender pentesting de forma ética y guiada.

Appointment introduce la vulnerabilidad más clásica de aplicaciones web: el bypass de autenticación por inyección SQL. El atacante manipula la query de login enviando SQL en el campo de usuario, haciendo que la condición de autenticación sea siempre verdadera.

---

## Objetivo

Obtener acceso a una aplicación web con formulario de login explotando SQL Injection, sin conocer credenciales válidas. La flag se obtiene tras autenticarse correctamente.

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

**Categoría: escaneo de puertos y fingerprinting de servicio.**

```bash
nmap -sC -sV -oN appointment.nmap <IP>
```

Lo que revela:

- Puerto **80/tcp** abierto — servidor web HTTP (Apache, nginx u otro; confirmar con el output).
- Sin otros puertos relevantes en este nivel.

Navegar al target en el navegador:

```bash
http://<IP>/
```

Se presenta un formulario de login estándar con campos `username` y `password`. No hay más rutas visibles inicialmente.

---

## Enumeracion

**Categoría: análisis de la superficie de ataque en la aplicación web.**

Con el formulario identificado, el siguiente paso es caracterizar cómo gestiona la entrada:

- Intentar credenciales obvias (`admin/admin`, `admin/password`) para confirmar que no hay cuentas por defecto activas.
- Observar los mensajes de error: si el mensaje distingue "usuario no existe" de "contraseña incorrecta", el servidor filtra información útil (user enumeration). En este nivel el mensaje es genérico.
- No es necesario fuzzing de directorios para este foothold; el vector está en el propio formulario.

---

## Acceso inicial (foothold)

**Categoría: SQL Injection — bypass de autenticación por condición siempre verdadera.**

El backend construye la query de autenticación concatenando directamente el input del usuario, algo similar a:

```sql
SELECT * FROM users WHERE username = '$input_usuario' AND password = '$input_password';
```

Si el input no se sanea, un atacante puede inyectar SQL que haga la condición siempre verdadera.

**Payload en el campo `username`:**

```
admin'-- -
```

O alternativamente:

```
' or '1'='1
```

**Campo `password`:** cualquier valor (se ignora por el comentario SQL o por la condición OR).

Cómo funciona el primer payload: el apóstrofe cierra la cadena del nombre de usuario, y `-- -` comenta el resto de la query, incluyendo la comprobación de contraseña. La query resultante queda:

```sql
SELECT * FROM users WHERE username = 'admin'-- -' AND password = '...';
-- equivale a:
SELECT * FROM users WHERE username = 'admin';
```

Con el segundo payload (`' or '1'='1`), la condición OR hace que la expresión completa sea verdadera para cualquier fila:

```sql
SELECT * FROM users WHERE username = '' or '1'='1' AND password = '...';
```

> Ajuste en vivo: el payload exacto puede variar según el motor de base de datos (MySQL, SQLite, PostgreSQL) y cómo esté construida la query. Si `-- -` no funciona, probar `#` (comentario MySQL) o `' or 1=1-- -`. La técnica es la misma; solo cambia el delimitador de comentario.

Al enviar el formulario con el payload, la aplicación autentica al atacante y muestra la flag directamente en la página.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente tras el bypass de autenticación en la interfaz web. No hay acceso a shell ni movimiento lateral en este nivel.

---

## Flags

| Flag | Ubicación | Cómo se obtiene |
|---|---|---|
| `<flag>` | Página web tras login exitoso | Visible en el dashboard después del bypass |

> Nota: Appointment es una máquina de una sola flag. No hay `user.txt` ni `root.txt` en el sistema de archivos; la flag aparece en la respuesta HTTP del login exitoso.

---

## Patron y teoria

Esta es la sección central: el patrón que se repite en producción real y cómo prevenirlo.

### El patron: concatenacion de input en queries SQL

**Categoria: CWE-89 — Improper Neutralization of Special Elements used in an SQL Command.**

Cada vez que una aplicación construye una query SQL pegando strings con input del usuario, el input puede redefinir la estructura lógica de la query. No es un bug oscuro: es la vulnerabilidad web más documentada desde los años 90 y sigue apareciendo en auditorías reales.

El flujo vulnerable es:

```
Input usuario → concatenación directa → string SQL → ejecución en DB
```

El flujo seguro es:

```
Input usuario → binding de parámetro tipado → query parametrizada → ejecución en DB
```

### Como se defiende (clave dev/purple team)

**1. Consultas parametrizadas (prepared statements) — la solución primaria.**

El motor de base de datos recibe la estructura de la query separada del valor. El valor nunca puede reinterpretar la sintaxis SQL.

```python
# Vulnerable
cursor.execute(f"SELECT * FROM users WHERE username = '{user}' AND password = '{pwd}'")

# Seguro
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user, pwd))
```

```javascript
// Node.js / MySQL2 — vulnerable
db.query(`SELECT * FROM users WHERE username = '${user}'`)

// Seguro
db.query("SELECT * FROM users WHERE username = ?", [user])
```

**2. ORM con binding automático.** Frameworks como SQLAlchemy, Django ORM, Prisma, TypeORM parametrizan por defecto. Usar la capa ORM elimina el riesgo si no se cae en raw queries con f-strings.

**3. Principio de mínimo privilegio en DB.** El usuario de base de datos de la aplicación web solo debe tener `SELECT/INSERT/UPDATE` sobre sus tablas. Nunca `DROP`, `GRANT`, ni acceso a tablas del sistema. Limita el radio de daño si hay SQLi.

**4. WAF como capa adicional (no como sustituto).** Un Web Application Firewall puede detectar payloads conocidos, pero no reemplaza el código seguro. Los WAFs se bypasean.

**5. No filtrar por mensaje de error.** Mensajes distintos para "usuario no existe" vs "contraseña incorrecta" permiten enumerar usuarios válidos. Usar siempre el mismo mensaje genérico de fallo de autenticación.

**6. Rate limiting y bloqueo por intentos.** Aunque no bloquea SQLi directamente, dificulta el fuzzing y el brute force asociado.

### Donde aparece esto en codigo real

- Formularios de login escritos "a mano" sin framework.
- Endpoints de búsqueda con filtros dinámicos (`WHERE campo LIKE '%$input%'`).
- Aplicaciones legacy en PHP sin PDO, o en Python 2 con `%s % variable`.
- Integraciones que construyen queries desde parámetros de URL.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
