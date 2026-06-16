---
title: Meow (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, telnet, enumeracion, credenciales-por-defecto, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [meow htb, htb meow, starting point meow]
---

# Meow — HTB Starting Point (Tier 0)

**Tier 0 · SO: Linux · Dificultad: Very Easy · Skills: enumeracion nmap, cliente Telnet**

Primera maquina de Starting Point. No requiere exploits ni contraseñas robadas: el vector es un servicio de administracion remota expuesto sin autenticacion. Perfecta para interiorizar el ciclo recon → enum → foothold antes de añadir complejidad.

> HTB Starting Point es un laboratorio legal y autorizado. Todo lo documentado aqui se ejecuta exclusivamente en entornos propios de Hack The Box.

---

## Objetivo

Obtener acceso al sistema y leer la flag en `/root/flag.txt`.

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

**Categoria: escaneo de puertos / fingerprinting de servicios.**

El primer paso siempre es mapear la superficie de ataque: que puertos escuchan y que servicio/version corre en cada uno.

```bash
nmap -sV <IP>
```

Resultado relevante:

```
23/tcp  open  telnet  Linux telnetd
```

- `-sV` activa la deteccion de versiones (service version detection).
- Puerto 23 = Telnet. Un protocolo de administracion remota de los anos 70, sin cifrado, practicamente obsoleto en produccion moderna.
- El resto de puertos estara cerrado/filtrado en esta maquina; Telnet es el unico vector.

> Si nmap no devuelve resultados rapido, prueba primero `nmap -p- <IP>` para escanear todos los puertos y luego `-sV` sobre los abiertos. Ajusta contra la maquina en vivo.

---

## Enumeracion

**Categoria: identificacion del servicio y su banner.**

Con un puerto Telnet abierto, el siguiente paso es conectarse y leer el banner de bienvenida: puede revelar nombre de host, version del SO o pistas sobre usuarios validos.

```bash
telnet <IP>
```

El servidor responde con un prompt de login. La enumeracion aqui es minima porque Telnet no ofrece mucha superficie antes de autenticarse, pero el banner ya confirma que es un sistema Linux sin bastionado visible.

---

## Acceso inicial (foothold)

**Categoria: credenciales ausentes / cuenta sin password.**

El patron de ataque es: probar el usuario `root` con contrasena vacia. En sistemas mal configurados o recien instalados, la cuenta de administrador puede no tener password asignada.

```bash
telnet <IP>
```

```
Meow login: root
Password:          ← pulsar Enter (sin escribir nada)
```

Si la autenticacion tiene exito, obtienes directamente una shell como `root`. No hay escalada de privilegios porque ya eres el usuario con maximos permisos desde el primer momento.

```bash
whoami   # → root
```

---

## Escalada de privilegios

No requiere privesc: el foothold via Telnet con usuario `root` sin password ya otorga shell de root. La flag se obtiene directamente desde ese contexto.

---

## Flags

Esta maquina tiene una sola flag (no hay `user.txt` separado):

| Flag | Ruta | Como obtenerla |
|------|------|----------------|
| root | `/root/flag.txt` | `cat /root/flag.txt` desde la shell de root |

```bash
cat /root/flag.txt
# → <flag>
```

---

## Patron y teoria

**Este es el nucleo del writeup. El resto es mecanica; esto es lo que debes llevarte.**

### Patron: servicio de administracion expuesto + credencial ausente

Dos fallos que se combinan y se amplifican mutuamente:

1. **Telnet en un puerto accesible desde la red** — Telnet transmite todo en texto plano (usuario, password, comandos, respuestas). Cualquier posicion de Man-in-the-Middle captura la sesion completa. En 2026 no hay justificacion tecnica para usar Telnet en produccion.

2. **Cuenta `root` sin password** — Una cuenta de administrador sin autenticacion es equivalente a dejar la puerta del servidor abierta. No hay barrera: ni credencial, ni clave, ni token.

La combinacion convierte acceso de red en acceso root en un solo paso.

### Como se defiende / como se disena (clave dev/purple team)

| Capa | Medida concreta |
|------|-----------------|
| **Protocolo** | Sustituir Telnet por SSH. SSH cifra el canal y soporta autenticacion por clave publica (sin passwords). |
| **Credenciales** | Obligar password no vacio en todas las cuentas del sistema. En Linux: `passwd -l root` bloquea login directo a root; `PermitRootLogin no` en `sshd_config` impide login SSH como root. |
| **Red** | Segmentar: los puertos de administracion (22, 23, 3389…) solo deben ser accesibles desde una red de gestion o VPN, nunca desde Internet. Firewall/iptables/nftables con politica por defecto DROP. |
| **Inventario** | Escanear periodicamente tu propia infraestructura con nmap o herramientas como Shodan para detectar servicios expuestos no intencionalmente. |
| **Principio de minimo privilegio** | Si un proceso/usuario no necesita ser root, no lo seas. Separar cuentas de servicio de cuentas de administracion. |

### Lectura del atacante vs. del defensor

Desde el lado ofensivo, nmap + telnet es un flujo de dos comandos. Desde el lado defensivo, una maquina como esta representa semanas de exposicion silenciosa si nadie monitoriza: sin credencial no hay log de autenticacion fallida que alertar.

> Tip de diseno: en cualquier sistema que construyas, el primer checklist de hardening debe incluir "¿que puertos escuchan?", "¿que usuarios existen sin password?" y "¿que protocolos legacy estan activos?". Meow es el caso base de ese checklist.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
