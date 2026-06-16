---
title: "Administración: backups y upgrades"
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/administracion, programacion/sysadmin]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab admin, gitlab backup, gitlab upgrade]
---

# 🛠️ Administración: backups y upgrades

## ¿Por qué importa esto?

Cuando usas GitLab en la nube (gitlab.com) alguien más hace todo lo que cubre este documento. Cuando **autohospedas** (ver [[10-autoalojamiento]]), tú eres ese alguien. Este documento cubre el "impuesto de mantenimiento" real: las tareas operativas que tienes que asumir si quieres control total sobre tu instancia.

El panorama de responsabilidades:

| Tarea | gitlab.com | Omnibus autohospedado |
|---|---|---|
| Backups | GitLab Inc. | **Tú** |
| Upgrades | Automático | **Tú** (con restricciones de ruta) |
| Configuración del servidor | No aplica | **Tú** (`gitlab.rb`) |
| Monitoreo | Dashboard básico | **Tú** (Prometheus integrado) |
| Usuarios / autenticación | Panel web | **Tú** (LDAP, SAML, etc.) |

Si no estás dispuesto a asumir estas tareas, **usa gitlab.com**. Si las asumes, tienes control total sobre datos, versiones y seguridad.

---

## 🗂️ `gitlab.rb` — el archivo de configuración maestro

### ¿Qué problema resuelve?

GitLab Omnibus empaqueta docenas de servicios (PostgreSQL, Redis, Nginx, Sidekiq, Gitaly...) en un solo paquete. `gitlab.rb` es el punto único donde configuras todos esos servicios sin tocar los archivos de cada componente directamente.

Ubicación: `/etc/gitlab/gitlab.rb`

```ruby
# /etc/gitlab/gitlab.rb — ejemplos comentados

# URL pública de tu instancia (CRÍTICO: debe ser la URL real)
external_url 'https://gitlab.miempresa.com'

# Configuración de correo saliente (SMTP)
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "smtp.gmail.com"
gitlab_rails['smtp_port'] = 587
gitlab_rails['smtp_user_name'] = "alerts@miempresa.com"
gitlab_rails['smtp_password'] = "secreto"
gitlab_rails['smtp_domain'] = "miempresa.com"
gitlab_rails['smtp_authentication'] = "login"
gitlab_rails['smtp_enable_starttls_auto'] = true

# Limitar uso de RAM de PostgreSQL
postgresql['shared_buffers'] = "256MB"

# Deshabilitar componentes que no usas (ahorra RAM)
# Si no usas Pages ni Registry, apágalos
pages_enabled = false
registry['enable'] = false

# Directorio de backups
gitlab_rails['backup_path'] = "/var/opt/gitlab/backups"

# Retención de backups (segundos): 7 días = 604800
gitlab_rails['backup_keep_time'] = 604800
```

### Aplicar cambios: `gitlab-ctl reconfigure`

Editar `gitlab.rb` **no tiene efecto inmediato**. Debes ejecutar:

```bash
sudo gitlab-ctl reconfigure
```

Esto lee `gitlab.rb`, regenera todos los archivos de configuración de los servicios internos, y reinicia los que necesiten cambios. Tarda 30–90 segundos.

**Comandos de gestión de servicios más usados:**

```bash
# Estado de todos los servicios internos
sudo gitlab-ctl status

# Reiniciar un servicio específico (sin reconfigure completo)
sudo gitlab-ctl restart sidekiq
sudo gitlab-ctl restart puma

# Ver logs en tiempo real
sudo gitlab-ctl tail
sudo gitlab-ctl tail nginx    # solo nginx
sudo gitlab-ctl tail gitlab-rails

# Verificar config (chequeo sin aplicar)
sudo gitlab-rake gitlab:check
```

> Regla: `reconfigure` = aplicar cambios de `gitlab.rb`. `restart` = solo reiniciar el proceso sin releer config.

---

## 👥 Usuarios y autenticación

### Autenticación local (por defecto)

GitLab crea una base de usuarios interna. El primer usuario (`root`) se configura durante la instalación con la contraseña en `/etc/gitlab/initial_root_password` (se borra tras 24h — cámbiala de inmediato).

```bash
# Resetear contraseña de root desde consola
sudo gitlab-rake "gitlab:password:reset[root]"
```

### Autenticación externa — LDAP / Active Directory

Para organizaciones con Active Directory o LDAP corporativo, GitLab puede autenticar contra él:

```ruby
# En gitlab.rb
gitlab_rails['ldap_enabled'] = true
gitlab_rails['ldap_servers'] = {
  'main' => {
    'label' => 'LDAP Empresa',
    'host' =>  'ldap.miempresa.com',
    'port' => 389,
    'uid' => 'sAMAccountName',     # atributo de usuario en AD
    'bind_dn' => 'CN=gitlab,OU=ServiceAccounts,DC=miempresa,DC=com',
    'password' => 'secreto_ldap',
    'base' => 'OU=Users,DC=miempresa,DC=com',
    'encryption' => 'start_tls'
  }
}
```

Tras `reconfigure`, los usuarios pueden hacer login con sus credenciales corporativas.

### SAML / OAuth (alternativas)

GitLab soporta SAML 2.0 (para SSO con Okta, Azure AD, etc.) y OAuth con GitHub, Google, etc. La configuración es similar — todo en `gitlab.rb`, en la sección `gitlab_rails['omniauth_providers']`.

### Gestión de usuarios desde admin

En la interfaz web: **Admin Area → Users** (accedida como root o usuario con rol Admin). Permite:
- Bloquear/desbloquear usuarios
- Impersonar (entrar como ese usuario para depurar)
- Ver actividad y proyectos

```bash
# Desde consola: listar usuarios activos
sudo gitlab-rails runner "User.active.each { |u| puts u.email }"
```

---

## 💾 Backups

### ¿Qué incluye un backup de GitLab?

Un backup de GitLab **no es solo una copia de la base de datos**. Incluye:

| Componente | Incluido en backup | Notas |
|---|---|---|
| Base de datos (PostgreSQL) | Sí | Usuarios, issues, MRs, CI logs... |
| Repositorios Git | Sí | Todos los repos de todos los proyectos |
| Subidas de archivos | Sí | Attachments, avatares |
| Configuración GitLab Pages | Sí | — |
| `/etc/gitlab/gitlab.rb` | **NO** | Debes copiarlo aparte |
| `/etc/gitlab/gitlab-secrets.json` | **NO** | Claves de cifrado — CRÍTICO |

> **CRÍTICO:** Sin `gitlab-secrets.json`, un backup es inútil. Las variables CI cifradas, tokens 2FA, y contraseñas cifradas en BD son ilegibles sin ese archivo. Cópialo aparte y guárdalo en un lugar seguro (gestor de secretos, no el mismo servidor).

### Crear un backup manual

```bash
# Crear backup (puede tardar varios minutos en instancias grandes)
sudo gitlab-backup create

# El backup se genera en /var/opt/gitlab/backups/ por defecto
# Nombre: EPOCH_YYYY_MM_DD_VERSION_gitlab_backup.tar
# Ejemplo: 1718352000_2026_06_14_17.1.0_gitlab_backup.tar

# Ver espacio disponible antes de hacer backup
df -h /var/opt/gitlab/backups/
```

### Restaurar desde backup

**Requisito:** La versión de GitLab al restaurar debe ser **exactamente la misma** que generó el backup.

```bash
# 1. Detener los servicios que escriben en BD
sudo gitlab-ctl stop puma
sudo gitlab-ctl stop sidekiq

# 2. Restaurar (sustituye TIMESTAMP por el del archivo)
sudo gitlab-backup restore BACKUP=1718352000_2026_06_14_17.1.0

# 3. Reiniciar todo
sudo gitlab-ctl restart

# 4. Verificar integridad
sudo gitlab-rake gitlab:check SANITIZE=true
```

Antes de restaurar, también necesitas reponer `gitlab-secrets.json` y `gitlab.rb` en `/etc/gitlab/`.

### Automatizar backups con cron

```bash
# Editar crontab del sistema
sudo crontab -e

# Backup cada día a las 2:00 AM
0 2 * * * /opt/gitlab/bin/gitlab-backup create CRON=1 2>&1 | logger -t gitlab-backup
```

La variable `CRON=1` suprime el output a stdout (solo registra errores). El flag `logger` envía la salida al syslog del sistema para poder revisarla con `journalctl`.

**Automatizar la copia a almacenamiento externo:**

```bash
# Después del backup, copiar a S3 o a otro servidor
# Ejemplo con rclone (igual que el backup-docs.sh del sistema)
0 2 * * * /opt/gitlab/bin/gitlab-backup create CRON=1 && \
  rclone copy /var/opt/gitlab/backups/ remote:gitlab-backups/ \
  --min-age 1s --max-age 24h
```

> Regla: el backup local es el primer anillo de seguridad. El backup remoto (S3, Drive, otro servidor) es el que te salva si pierdes el servidor.

---

## ⬆️ Upgrades — el punto más delicado

### Por qué los upgrades son especiales en GitLab

GitLab tiene migraciones de base de datos complejas entre versiones. **No puedes saltar versiones mayores arbitrariamente** — puedes corromper la BD o dejar la instancia en estado inconsistente.

La regla general:
- Puedes actualizar libremente dentro de una versión major (e.g., 17.0 → 17.5)
- Entre versiones major (e.g., 16.x → 17.x), debes pasar por **puntos de parada obligatorios** (llamados "upgrade stops")

### Upgrade Path Tool — úsala siempre

GitLab mantiene una herramienta oficial:

**https://gitlab-com.gitlab.io/support/toolbox/upgrade-path/**

Introduces la versión actual y la versión destino, y te dice la ruta exacta. Ejemplo:

```
Actual: 15.4.0  →  Destino: 17.1.0
Ruta obligatoria:
  15.4.0 → 15.11.x → 16.3.x → 16.11.x → 17.1.0
```

**No asumas la ruta, consulta la herramienta para cada upgrade.**

### Proceso de upgrade en Omnibus (Debian/Ubuntu)

```bash
# 1. Verificar versión actual
sudo gitlab-rake gitlab:env:info | grep "GitLab version"

# 2. Hacer backup ANTES (siempre)
sudo gitlab-backup create

# 3. Actualizar al siguiente punto de la ruta
sudo apt-get update
sudo apt-get install gitlab-ee=16.3.6-ee.0   # versión específica

# 4. Si la versión no está en los repos por defecto, añadir la versión en la URL
curl -sS "https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh" | sudo bash

# 5. Verificar que el reconfigure se ejecutó automáticamente
sudo gitlab-ctl status

# 6. Comprobar que no hay migraciones pendientes
sudo gitlab-rake db:migrate:status | grep down
```

### Errores comunes en upgrades

| Error | Causa | Solución |
|---|---|---|
| `ActiveRecord::Migration` falla | Saltaste un punto de parada | Restaurar backup, hacer la ruta correcta |
| Servicios no arrancan tras upgrade | Config incompatible en `gitlab.rb` | Revisar CHANGELOG de la versión, ajustar `gitlab.rb` |
| Timeout en `reconfigure` | Migraciones lentas en BD grande | Esperar (pueden tardar 30+ min en instancias grandes) |
| "500 Whoops" tras upgrade | Caché desactualizada | `sudo gitlab-rake cache:clear` |

```bash
# Limpiar caché si hay problemas tras upgrade
sudo gitlab-rake cache:clear

# Ver migraciones pendientes
sudo gitlab-rake db:migrate:status 2>/dev/null | grep "^\s*down"
```

---

## 📊 Monitoreo — Prometheus integrado

GitLab Omnibus incluye Prometheus y un conjunto de exporters preconfigurados. No necesitas instalar nada extra para tener métricas básicas.

### Acceso

Por defecto, Prometheus escucha en `http://localhost:9090` (solo accesible localmente por seguridad).

En la interfaz web, como admin: **Admin Area → Monitoring → Health Check** da un resumen rápido del estado.

### Métricas disponibles

GitLab expone métricas de:
- **Sidekiq**: jobs en cola, jobs fallidos, tiempo de proceso
- **Puma**: workers activos, requests por segundo
- **PostgreSQL**: conexiones, queries lentas
- **Redis**: memoria usada, comandos por segundo
- **Gitaly**: operaciones Git, latencia

```bash
# Ver métricas raw de Prometheus (desde el servidor)
curl http://localhost:9090/metrics | grep sidekiq_queue_size

# Health check rápido (devuelve 200 OK si todo va bien)
curl https://gitlab.miempresa.com/-/health
curl https://gitlab.miempresa.com/-/readiness
curl https://gitlab.miempresa.com/-/liveness
```

### Alertas básicas recomendadas

Si conectas Alertmanager (también incluido en Omnibus), configura alertas para:
- Espacio en disco `< 20%` en `/var/opt/gitlab/`
- Cola de Sidekiq `> 1000 jobs` (indica backlog)
- Tiempo de respuesta de Puma `> 5s`
- Último backup `> 25h` (el cron falló)

---

## 💸 El "impuesto de mantenimiento" real

Esto es lo que realmente cuesta operar GitLab autohospedado, más allá del hardware:

| Tarea | Frecuencia | Tiempo estimado |
|---|---|---|
| Revisar logs y alertas | Diario | 5–10 min |
| Verificar backups | Semanal | 10 min |
| Upgrades de seguridad (patch) | Mensual | 30–60 min |
| Upgrades de versión major | Trimestral/semestral | 1–3 horas |
| Revisión de espacio en disco | Mensual | 15 min |
| Prueba de restauración de backup | Semestral | 2–4 horas |

> El upgrade semestral con "upgrade path" de 3 saltos puede llevarte 2–3 horas si tienes una instancia grande con muchos datos. En una instancia pequeña (equipo de 5–10 personas, pocos repos), suele ser 30–45 minutos por salto.

**Cuando el impuesto NO vale la pena:**
- Equipos pequeños sin requisitos de compliance o datos sensibles
- No tienes un sysadmin o DevOps dedicado
- No necesitas customizaciones de servidor

**Cuando SÍ vale la pena:**
- Requisitos legales de soberanía de datos (datos no pueden salir de tu infraestructura)
- Integración con LDAP/AD corporativo que no quieres exponer externamente
- Volumen de repos/artifacts que haría cara la suscripción Premium/Ultimate de gitlab.com
- Control total sobre versiones (puedes quedarte en una versión estable el tiempo que necesites)

---

## Aplícalo a tus proyectos

**proyecto embebido / app web** — si en algún momento montas GitLab autohospedado para CI/CD de estos proyectos (en lugar de usar gitlab.com):

1. Configura `external_url` con tu dominio real desde el primer día — cambiarlo después rompe todos los webhooks y URLs de repos.
2. Añade el cron de backup desde el día 1, antes de meter código real.
3. Prueba la restauración en un servidor de prueba antes de necesitarla en producción.
4. Documenta la versión actual y la ruta de upgrade en una nota de la bóveda — GitLab lanza versiones cada mes, no pierdas el rastro.

---

## Conexiones

- [[MOC_GitLab]]
- [[10-autoalojamiento]]
- [[06-runners]]
- [[05-gitlab-cicd-fundamentos]]
- [[07-cicd-avanzado]]
- [[MOC_Desarrollo_Software]]
