---
title: Preignition (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, web, gobuster, credenciales-por-defecto, enumeracion-directorios]
type: nota
status: en-progreso
source: claude-code
aliases: [Preignition HTB, preignition starting point]
---

# Preignition — HTB Starting Point (Tier 0)

**Tier 0 · SO: Linux · Dificultad: Very Easy · Skills: gobuster, HTTP, credenciales por defecto**

Máquina introductoria centrada en dos técnicas fundamentales del reconocimiento web: enumeración de directorios ocultos y explotación de credenciales por defecto en paneles de administración. Ideal para interiorizar el flujo recon → enumeración → foothold sin ninguna complejidad adicional.

> HTB Starting Point es un laboratorio legal y autorizado por Hack The Box para aprender pentesting de forma ética y controlada.

---

## Objetivo

Encontrar un panel de administración web oculto, acceder con credenciales por defecto y recuperar la flag.

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

**Categoría: escaneo de puertos activos**

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Resultado relevante:

```
80/tcp  open  http  nginx
```

Solo hay un servicio expuesto: HTTP en el puerto 80 sobre nginx. No hay SSH ni otro vector obvio. El siguiente paso lógico es enumerar el contenido web.

---

## Enumeración

**Categoría: fuerza bruta de directorios (directory/content discovery)**

El patrón: los servidores web pueden tener rutas no enlazadas desde la interfaz principal pero igualmente accesibles si conoces la URL. Un fuzzer de directorios las descubre por fuerza bruta contra una wordlist.

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

> La wordlist exacta puede variar según tu instalación (`/usr/share/seclists/Discovery/Web-Content/common.txt` es otra opción común). Lo esencial es incluir extensiones PHP (`-x php`) porque el servidor corre nginx con PHP.

Resultado relevante:

```
/admin.php  (Status: 200)
```

Se descubre `/admin.php`, una ruta no visible desde la página principal.

---

## Acceso inicial (foothold)

**Categoría: credenciales web por defecto**

Navegar a `http://<IP>/admin.php` muestra un formulario de login estándar. El patrón de ataque es probar credenciales por defecto antes de cualquier otra técnica: muchos paneles de administración se despliegan sin cambiar las credenciales de fábrica.

Credenciales a probar:

| Usuario | Contraseña |
|---------|-----------|
| `admin` | `admin`   |
| `admin` | `password`|
| `admin` | `1234`    |

En esta máquina, `admin` / `admin` concede acceso inmediato. El panel muestra la flag directamente en pantalla.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente tras el login en el panel `/admin.php`. No hay shell que escalar ni usuario adicional que comprometer.

---

## Flags

| Flag | Ubicación |
|------|-----------|
| Única flag | Mostrada en el panel `/admin.php` tras login exitoso |

Copia el valor y entrégalo en la plataforma HTB. Formato típico: `HTB{<flag>}`.

---

## Patrón y teoría

Esta máquina combina dos patrones que aparecen de forma recurrente en entornos reales:

### Patrón 1 — Contenido oculto por oscuridad (Security through Obscurity)

**Schema**: el servidor sirve recursos accesibles que no están enlazados desde la UI → no aparecen en el HTML pero existen en disco.

**Técnica**: directory/content brute-forcing con gobuster, ffuf, dirsearch o similares contra wordlists de rutas comunes.

```bash
# Con ffuf (alternativa a gobuster):
ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -e .php,.html
```

**Como se defiende (dev/purple team)**:
- Los paneles de administración no deben ser accesibles desde internet: colocarlos en una ruta interna, detrás de una VPN o con restricción por IP a nivel de servidor (`allow` / `deny` en nginx/apache).
- No confiar en que "nadie sabrá la URL": cualquier ruta predecible (`/admin`, `/admin.php`, `/dashboard`, `/wp-admin`) está en todas las wordlists.
- Añadir autenticación a nivel de red (HTTP Basic Auth como primera capa, MFA en la capa de aplicación) aunque la ruta no sea pública.

### Patrón 2 — Credenciales por defecto (Default Credentials)

**Schema**: aplicación desplegada sin cambiar las credenciales de fábrica del vendedor/framework → cualquiera que conozca el software puede autenticarse.

**Clasificación OWASP**: [[04-seguridad-web-owasp]] → A07:2021 Identification and Authentication Failures.

**Como se defiende (dev/purple team)**:
- **Forzar cambio de credenciales en el primer arranque**: bloquear la aplicación hasta que el admin establezca una contraseña distinta a la de defecto.
- **Auditar el inventario de servicios internos**: routers, paneles CMS, Grafana, Jenkins, MongoDB Express... todos tienen credenciales por defecto documentadas públicamente (ver `https://github.com/ihebski/DefaultCreds-cheat-sheet`).
- **Política de contraseñas con entropía mínima**: rechazar `admin`, `password`, `1234` mediante validación en backend, no solo en frontend.
- **Alerta ante N intentos fallidos consecutivos**: implementar rate-limiting y bloqueo temporal + notificación.

### Flujo completo (mental model)

```
nmap (¿qué puertos/servicios?)
  → gobuster (¿qué rutas existen en HTTP?)
    → credenciales por defecto (¿está sin configurar?)
      → flag / foothold
```

Este flujo se repite en decenas de CVEs reales: paneles Grafana expuestos, instancias Jenkins sin autenticación, phpMyAdmin con `root/` vacío, etc.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
