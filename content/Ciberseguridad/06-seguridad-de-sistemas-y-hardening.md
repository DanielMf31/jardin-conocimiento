---
title: Seguridad de sistemas y hardening
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, sistemas/linux, sistemas/permisos, sistemas/hardening]
type: nota
status: en-progreso
source: claude-code
aliases: [hardening linux, seguridad sistemas, system hardening]
---

# Seguridad de sistemas y hardening

## ¿Por qué existe este documento?

Antes de atacar la capa web o la red, un adversario puede atacar **el sistema operativo en sí**: escalar privilegios, instalar malware persistente o explotar un servicio mal configurado. El *hardening* (endurecimiento) es la práctica de reducir la superficie de ataque del propio OS reduciendo servicios, ajustando permisos y aplicando controles de acceso obligatorio.

Este documento cubre la capa del sistema operativo (Linux principalmente) desde el modelo de permisos hasta el aislamiento de procesos. Es el complemento defensivo del [[07-pentesting-y-ciclo-del-ataque]] y se apoya en la base de [[MOC_CS_Fundamentos]] (teoría de OS).

---

## Mapa mental del área

```
Sistema Operativo
├── Modelo de permisos (DAC)
│   ├── Usuarios / Grupos / Otros
│   ├── rwx + bits especiales (setuid, setgid, sticky)
│   └── sudo / su
├── Control de Acceso Obligatorio (MAC)
│   ├── SELinux
│   └── AppArmor
├── Hardening de superficie
│   ├── Servicios mínimos
│   ├── Actualizaciones / parches
│   ├── Firewall (ufw / nftables)
│   └── SSH hardening
├── Sandboxing y aislamiento
│   ├── Firejail
│   └── Contenedores (namespaces + cgroups)
└── Malware y detección
    ├── Tipos de malware
    └── EDR / AV / herramientas de análisis
```

---

## 1. Modelo de permisos Unix (DAC)

**DAC** (*Discretionary Access Control* — control de acceso discrecional): el *dueño* de un recurso decide quién puede acceder. Es el modelo nativo de Linux/Unix.

### 1.1 Usuarios, grupos y otros

Cada archivo tiene tres dimensiones de acceso:

| Dimensión | Quién | Abreviatura |
|-----------|-------|-------------|
| **Owner** | el usuario propietario del archivo | `u` |
| **Group** | el grupo propietario | `g` |
| **Others** | todos los demás | `o` |

Y tres permisos básicos:

| Permiso | Archivos | Directorios |
|---------|----------|-------------|
| `r` (4) | leer contenido | listar entradas |
| `w` (2) | escribir/modificar | crear/borrar dentro |
| `x` (1) | ejecutar | traversar (entrar) |

Ejemplo de `ls -l`:
```
-rwxr-x--- 1 daniel developers 4096 jun 14 12:00 script.sh
 ^^^---     ^   ^          ^
  |  |      |   owner      group
  |  group+others
  owner perms
```
`chmod 750 script.sh` = rwx para owner, r-x para grupo, nada para otros.

### 1.2 Bits especiales: setuid, setgid, sticky bit

Estos bits son la primera fuente de escalada de privilegios si se configuran mal.

| Bit | Símbolo | Efecto en archivos | Efecto en directorios |
|-----|---------|--------------------|-----------------------|
| **setuid** (4xxx) | `s` en `x` de owner | El proceso se ejecuta con el UID del *propietario del archivo*, no del usuario que lo lanza | Raro / no estándar |
| **setgid** (2xxx) | `s` en `x` de grupo | El proceso corre con GID del grupo del archivo | Los archivos nuevos heredan el grupo del directorio |
| **sticky bit** (1xxx) | `t` en `x` de others | Sin efecto moderno | En `/tmp`: solo el dueño puede borrar su propio archivo aunque todos tengan `w` |

**Por qué importa setuid**: `/usr/bin/passwd` necesita modificar `/etc/shadow` (solo root puede). Tiene setuid root. Si un binario setuid tiene una vulnerabilidad, el atacante hereda UID=0.

```bash
# Ver todos los binarios setuid en el sistema (diagnóstico)
find / -perm -4000 -type f 2>/dev/null
```

### 1.3 sudo vs su

- `su` — cambia de identidad completamente; requiere la contraseña del usuario destino.
- `sudo` — ejecuta un comando puntual con privilegios elevados; requiere la contraseña del *propio* usuario y está limitado por `/etc/sudoers`.

**Regla de oro**: nadie debería trabajar habitualmente como root. `sudo` + `sudoers` bien configurado limita el radio de daño si una sesión se ve comprometida.

---

## 2. Privilege Escalation (escalada de privilegios)

**Concepto**: un atacante que ha entrado al sistema con un usuario de bajos privilegios intenta obtener privilegios de administrador (root/SYSTEM). Es uno de los pasos centrales del [[07-pentesting-y-ciclo-del-ataque]] (fase post-explotación).

### 2.1 Vectores comunes en Linux

| Vector | Descripción | Indicador en el sistema |
|--------|-------------|------------------------|
| **SUID malconfigurado** | Binario con setuid que permite ejecutar comandos arbitrarios | `find / -perm -4000` encuentra `/usr/bin/vim` con setuid |
| **sudo misconfiguration** | `sudoers` permite `NOPASSWD: ALL` o un comando explotable | `sudo -l` como usuario no privilegiado |
| **Cron jobs escribibles** | Script que corre como root, pero cualquiera puede editarlo | `ls -la /etc/cron*` |
| **Kernel exploit** | CVE en el kernel que permite pasar de UID>0 a UID=0 | Kernel desactualizado |
| **Path hijacking** | Script root llama a `python` sin ruta absoluta; atacante pone un `python` falso antes en `$PATH` | Scripts root con rutas relativas |
| **Capabilities** | `cap_net_raw` o `cap_setuid` asignadas innecesariamente a binarios | `getcap -r / 2>/dev/null` |
| **Contraseñas en archivos** | `.bash_history`, `.env`, configs con credenciales en texto plano | — |

### 2.2 Cómo se previene

- **Principio de mínimo privilegio**: ningún proceso ni usuario debe tener más derechos de los que necesita.
- Auditar periódicamente binarios setuid: solo los estrictamente necesarios del sistema.
- Revisar `sudoers` con `visudo`; evitar `NOPASSWD` salvo en automatización específica y controlada.
- Scripts de cron que corren como root: propiedad root, permisos 700.
- Mantener el kernel actualizado.
- Usar herramientas de análisis: `linpeas`, `linenum` en laboratorios propios para entender qué expone el sistema.

---

## 3. Hardening de Linux

El hardening reduce la **superficie de ataque** (attack surface): la cantidad de puntos donde el sistema puede ser atacado. La idea es: lo que no existe no puede ser vulnerado.

### 3.1 Servicios mínimos

```bash
# Ver servicios activos
systemctl list-units --type=service --state=running

# Deshabilitar un servicio que no se usa
sudo systemctl disable --now cups   # impresora: ¿la necesitas en un servidor?
sudo systemctl disable --now avahi-daemon
```

**Regla**: en un servidor de producción, deshabilita todo lo que no tenga una justificación explícita. Cada servicio abierto es una posible puerta de entrada.

### 3.2 Actualizaciones y gestión de parches

La mayoría de brechas reales explotan vulnerabilidades **ya parcheadas**. La organización simplemente no había actualizado.

```bash
# Debian/Ubuntu
sudo apt update && sudo apt upgrade -y

# Habilitar actualizaciones de seguridad automáticas (Ubuntu)
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

**`unattended-upgrades`** aplica automáticamente parches de seguridad sin intervención manual. En producción, combinar con tests de rollback.

### 3.3 Firewall con ufw

`ufw` (*Uncomplicated Firewall*) es la interfaz amigable sobre `iptables`/`nftables`.

```bash
sudo ufw default deny incoming   # bloquear todo entrante por defecto
sudo ufw default allow outgoing  # permitir tráfico saliente
sudo ufw allow ssh               # abrir SSH (puerto 22)
sudo ufw allow 443/tcp           # HTTPS
sudo ufw enable
sudo ufw status verbose
```

**Principio**: *whitelist* de puertos (permitir lo explícito, denegar el resto), nunca *blacklist*.

Para limitar intentos de fuerza bruta en SSH:
```bash
sudo ufw limit ssh   # bloquea IPs que intenten >6 conexiones en 30 s
```

### 3.4 SSH hardening

SSH es el protocolo de administración remota más extendido en Linux. Una configuración deficiente es uno de los vectores de entrada más comunes.

Archivo: `/etc/ssh/sshd_config`

| Directiva | Valor seguro | Por qué |
|-----------|-------------|---------|
| `PermitRootLogin` | `no` | Nunca exponer root directamente |
| `PasswordAuthentication` | `no` | Usar solo claves criptográficas |
| `PubkeyAuthentication` | `yes` | Clave pública/privada en lugar de contraseña |
| `Port` | Cambiar de 22 a otro (ej. 2222) | Reduce ruido de bots (no es seguridad real, pero limpia logs) |
| `MaxAuthTries` | `3` | Limitar intentos |
| `AllowUsers` | `daniel` | Lista blanca de usuarios SSH |
| `Protocol` | `2` | Solo SSHv2; v1 tiene vulnerabilidades conocidas |
| `X11Forwarding` | `no` | Salvo que sea necesario |

Después de editar:
```bash
sudo sshd -t          # validar config sin aplicar
sudo systemctl restart sshd
```

**Generar y usar claves SSH**:
```bash
ssh-keygen -t ed25519 -C "daniel@maquina"   # genera par de claves
ssh-copy-id usuario@servidor                 # copia la clave pública al servidor
```

### 3.5 Auditoría: herramientas de referencia

| Herramienta | Qué hace |
|-------------|---------|
| `lynis` | Auditoría de hardening del sistema; da puntuación y recomendaciones |
| `chkrootkit` / `rkhunter` | Detecta rootkits conocidos |
| `fail2ban` | Banea IPs que hacen demasiados intentos fallidos (SSH, web, etc.) |
| `auditd` | Log detallado de llamadas al sistema (syscalls) para forensics |

```bash
sudo apt install lynis && sudo lynis audit system
```

---

## 4. Control de acceso obligatorio (MAC): SELinux y AppArmor

**MAC** (*Mandatory Access Control*): a diferencia del DAC, aquí el administrador del sistema define la política y **ni siquiera root puede saltársela** (en teoría). Añade una capa de defensa en profundidad: aunque un proceso sea comprometido, el kernel filtra qué puede hacer.

### 4.1 SELinux

Desarrollado por la NSA, integrado en el kernel Linux. Cada proceso, archivo y puerto tiene una **etiqueta** (contexto de seguridad). El kernel comprueba si la política permite esa interacción.

```
usuario:rol:tipo:nivel
system_u:system_r:httpd_t:s0
```

Modos:
- **Enforcing**: aplica la política, deniega y registra.
- **Permissive**: solo registra (modo diagnóstico).
- **Disabled**: apagado.

```bash
getenforce          # ver modo actual
setenforce 0        # cambiar a permissive (temporal)
sestatus            # estado detallado
```

**Distribuciones**: predeterminado en Red Hat, CentOS, Fedora.

### 4.2 AppArmor

Alternativa a SELinux, más sencilla de configurar. Define perfiles por aplicación que especifican a qué archivos y capacidades puede acceder.

```bash
sudo aa-status              # ver perfiles activos
sudo aa-enforce /usr/sbin/nginx   # poner perfil en modo enforcing
```

**Distribuciones**: predeterminado en Ubuntu, Debian.

### 4.3 ¿Cuándo importa esto?

Si un servicio web (nginx, apache) tiene una vulnerabilidad de ejecución remota de código, **sin MAC** el atacante puede leer `/etc/passwd`, escribir en `/var/www`, etc. **Con AppArmor/SELinux** en enforcing, el proceso nginx solo puede acceder a lo que su perfil permite, conteniendo el daño.

---

## 5. Sandboxing y aislamiento de procesos

### 5.1 Namespaces y cgroups (base de los contenedores)

El kernel Linux tiene primitivas de aislamiento:

| Primitiva | Qué aisla |
|-----------|----------|
| **PID namespace** | Árbol de procesos: el proceso no ve los PIDs del host |
| **NET namespace** | Interfaces de red propias |
| **MNT namespace** | Sistema de archivos propio |
| **USER namespace** | Mapeo de UIDs (root dentro ≠ root fuera) |
| **cgroups** | Límites de CPU, memoria, I/O |

Docker, Podman y systemd-nspawn usan estas primitivas. Un contenedor mal configurado puede "escapar" al host si tiene acceso a `/var/run/docker.sock` o capabilities excesivas.

### 5.2 Firejail

Herramienta de sandboxing para aplicaciones de escritorio en Linux. Usa namespaces para aislar un proceso sin necesidad de ser root.

```bash
sudo apt install firejail
firejail firefox        # ejecutar Firefox en sandbox
firejail --seccomp vlc  # añadir filtro de syscalls
```

Útil para aislar navegadores, clientes de correo o cualquier app que procese contenido no confiable.

### 5.3 Reglas de seguridad en contenedores

- Nunca montar `/var/run/docker.sock` en un contenedor de aplicación.
- Usar imágenes mínimas (alpine, distroless): menos software = menos CVEs.
- No ejecutar el proceso de la app como root dentro del contenedor.
- Usar `--read-only` y montar solo los volúmenes necesarios.
- Escanear imágenes con `trivy` o `grype` antes de desplegar.

```bash
trivy image mi-imagen:latest
```

---

## 6. Malware: tipos y detección

### 6.1 Tipos de malware

| Tipo | Qué hace | Ejemplo conocido |
|------|---------|-----------------|
| **Virus** | Se replica adjuntándose a archivos ejecutables | Concepto clásico; raro en Linux moderno |
| **Troyano** (*trojan*)| Software aparentemente legítimo con código malicioso oculto | Backdoors en paquetes de npm/pip comprometidos |
| **Ransomware** | Cifra los datos del sistema y pide rescate | LockBit, WannaCry |
| **Rootkit** | Se oculta en el OS (kernel o espacio usuario) para persistir sin ser detectado | Azazel, Necurs |
| **Keylogger** | Captura pulsaciones de teclado | Componente de muchos RATs |
| **RAT** (*Remote Access Trojan*) | Control remoto del sistema; C2 (*Command & Control*) | njRAT, AsyncRAT |
| **Cryptominer** | Usa los recursos del sistema para minar criptomonedas | XMRig instalado ilegítimamente |
| **Worm** | Se propaga por la red sin intervención del usuario | Morris Worm (histórico) |
| **Spyware** | Recopila información del usuario sin su consentimiento | — |
| **Bootkit** | Infecta el MBR/UEFI; carga antes del OS | — |

### 6.2 Persistencia: cómo el malware sobrevive a los reinicios

El malware quiere persistir. Vectores comunes en Linux:

- Crontab del usuario o del sistema (`/etc/cron*`, `crontab -l`)
- Servicios systemd no reconocidos (`/etc/systemd/system/`)
- Archivos de inicio de shell (`.bashrc`, `.profile`)
- Binarios troyanizados en `/usr/local/bin/`
- Módulos del kernel (rootkits avanzados)

### 6.3 EDR y antivirus

**AV** (*Antivirus*): detecta malware conocido por firma (*signature*). Eficaz contra amenazas catalogadas.

**EDR** (*Endpoint Detection and Response* — Detección y Respuesta en Endpoint): monitoriza el comportamiento del proceso en tiempo real. Detecta anomalías aunque la firma no esté catalogada.

| Característica | AV clásico | EDR |
|---------------|-----------|-----|
| Detección | Firmas | Firmas + comportamiento |
| Respuesta | Cuarentena/borrado | Aislamiento, forensics, rollback |
| Visibilidad | Archivo | Proceso, red, registro |
| Ejemplos Linux | ClamAV | Wazuh, Elastic Defend, CrowdStrike Falcon |

**ClamAV** para Linux (open source):
```bash
sudo apt install clamav clamav-daemon
sudo freshclam           # actualizar base de datos de firmas
clamscan -r /home/daniel # escanear directorio
```

**Wazuh**: plataforma EDR/SIEM open source; ideal para laboratorio propio.

### 6.4 Indicadores de compromiso (IoC)

Señales de que el sistema puede estar comprometido:

- Procesos desconocidos consumiendo CPU (`top`, `htop`)
- Conexiones de red inesperadas (`ss -tulnp`, `netstat -an`)
- Archivos modificados recientemente en rutas del sistema (`find /usr -newer /tmp/ref -type f`)
- Cuentas de usuario nuevas no autorizadas (`cat /etc/passwd`)
- Entradas en `/etc/sudoers` no reconocidas
- Logs con gaps (el atacante borró registros)

---

## 7. Errores comunes

| Error | Consecuencia | Corrección |
|-------|-------------|-----------|
| Root SSH habilitado | Acceso directo a root si se compromete la contraseña | `PermitRootLogin no` en sshd_config |
| `PasswordAuthentication yes` en SSH | Brute-force posible | Solo claves; `PasswordAuthentication no` |
| Binarios setuid innecesarios | Vector de escalada | Auditar con `find / -perm -4000` y eliminar los no necesarios |
| Kernel desactualizado | Exploits de kernel públicos | `apt upgrade` regular + `unattended-upgrades` |
| AppArmor/SELinux en modo permissive en producción | Sin protección real | Enforcing en producción; permissive solo para diagnóstico |
| Permisos 777 en scripts de cron | Cualquiera puede modificarlos | `chmod 700`; propietario root |
| Contenedor corriendo como root | Escape de contenedor más sencillo | `USER nonroot` en Dockerfile |
| `sudo NOPASSWD: ALL` | Un proceso comprometido tiene root | Limitar a comandos específicos |

---

## 8. Aplícalo / practica

### En laboratorio propio (VMs)

1. **Audita una VM Ubuntu limpia con `lynis`**: `sudo lynis audit system`. Lee las recomendaciones y aplica las 5 más prioritarias. Compara el score antes/después.
2. **Escalada de privilegios en laboratorio**:
   - Crear en una VM un binario setuid vulnerable (ej. `cp` o `vim` con setuid).
   - Intentar explotarlo para obtener shell root.
   - Luego eliminar el setuid y verificar que ya no funciona.
3. **SSH hardening**: configura una VM como servidor SSH. Aplica todas las directivas de la sección 3.4. Intenta conectar con contraseña (debe fallar) y con clave (debe funcionar).
4. **AppArmor en Ubuntu**: instala nginx, mira su perfil (`aa-status`). Pon el perfil en modo complain y observa los logs al navegar por el servidor.
5. **Detección de malware**: instala ClamAV, descarga un archivo de test EICAR (no es malware real, es el estándar de prueba de AV) y escanea:
   ```bash
   curl -O https://www.eicar.org/download/eicar.com
   clamscan eicar.com
   ```

### CTFs y plataformas

- **TryHackMe**: rooms "Linux Privilege Escalation", "Linux Hardening", "Blue" (Wazuh/ELK).
- **HackTheBox**: máquinas de dificultad fácil/media con PrivEsc en Linux.
- **PortSwigger** no aplica aquí (es web), pero los conceptos de OS son base para todo.
- **PentesterLab**: retos de escalada de privilegios con explicación.

### En tus propios proyectos

- Audita el Dockerfile del (app web): ¿corre como root? ¿montáis docker.sock? Aplica `USER nonroot`.
- Revisa que tu servidor (si tienes VPS) tiene `ufw` activo y SSH hardening aplicado.
- Ejecuta `find / -perm -4000 2>/dev/null` en tu máquina diaria y valida cada entrada.

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[MOC_CS_Fundamentos]]
- [[01-fundamentos-y-mentalidad]]
- [[03-seguridad-de-redes]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[08-vulnerabilidades-y-explotacion]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
- [[05-identidad-auth-y-secretos]]
