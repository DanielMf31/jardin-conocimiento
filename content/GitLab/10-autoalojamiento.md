---
title: Autoalojamiento (self-hosting) de GitLab
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/infraestructura, programacion/docker, programacion/sysadmin]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab self-host, gitlab autoalojado, gitlab on-premise]
---

# 🏠 Autoalojamiento (self-hosting) de GitLab

## ¿Por qué autoalojar?

GitLab.com es la instancia pública gratuita de GitLab. Autoalojar significa correr **tu propio servidor GitLab** en hardware que controlas (un VPS, un homelab, una RPi robusta, un servidor de empresa).

| Motivo | Cuándo importa |
|---|---|
| **Privacidad / control total de código** | Proyectos con IP sensible, contratos NDA |
| **Sin límites de almacenamiento/runners** | CI/CD intensivo, repos grandes de firmware/HW |
| **Integración en red privada** | Empresa sin acceso a internet público, red de planta |
| **Coste a escala** | Muchos usuarios: la licencia self-managed es más barata que GitLab.com Premium por usuario |
| **Compliance / auditoría** | Sectores regulados (médico, defensa) donde los datos no pueden salir del edificio |

**Cuándo NO vale la pena:** proyectos personales pequeños, equipos sin nadie que quiera administrar un servidor. GitLab.com Free cubre el 90% de casos de hobby.

---

## 🏗️ Arquitectura: qué hay dentro de un GitLab

GitLab "pesa" porque no es una aplicación monolítica simple: es una plataforma completa. Entender los componentes te ayuda a dimensionar el hardware y diagnosticar problemas.

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENTE (browser/git)               │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
              ┌────────▼────────┐
              │     Nginx       │  Proxy inverso, TLS termination
              │   (Workhorse)   │  Workhorse: maneja uploads/downloads
              └────┬───────┬────┘  grandes (git push/pull, CI artifacts)
                   │       │
        ┌──────────▼──┐  ┌─▼──────────┐
        │   Puma      │  │  Registry   │  Registro Docker integrado
        │  (Rails app)│  │  (opcional) │
        └──────┬──────┘  └────────────┘
               │
    ┌──────────▼──────────┐
    │       Sidekiq        │  Jobs en background: emails, webhooks,
    │  (background jobs)   │  imports, CI scheduling, limpieza...
    └──────┬───────┬───────┘
           │       │
  ┌────────▼──┐  ┌─▼──────────┐
  │ PostgreSQL │  │   Redis    │  Cache, colas de Sidekiq, sesiones
  │  (BBDD)   │  │            │
  └───────────┘  └────────────┘
           │
  ┌────────▼──────────┐
  │      Gitaly        │  Servicio que habla con los repos Git en disco
  │  (git storage)     │  Abstracción sobre git-core; escala horizontal
  └────────────────────┘
```

### Por qué consume tanta RAM

- **Puma** (Ruby on Rails): cada worker carga todo el framework (~150-250 MB/worker)
- **Sidekiq**: más workers Ruby en background
- **PostgreSQL**: cache de BD en RAM (muy beneficioso darle espacio)
- **Gitaly**: procesa git objects, puede picar fuerte en repos grandes
- **Redis**: pequeño, pero imprescindible

Mínimo viable (homelab, pocos usuarios): **4 GB RAM**. Cómodo para un equipo pequeño: **8 GB**. Producción seria: **16+ GB**.

---

## 📦 Formas de instalar

### 1. Omnibus (paquete .deb / .rpm) — el método "oficial"

Omnibus empaqueta **todos los componentes** (PostgreSQL, Redis, Nginx, Gitaly…) en un solo paquete del sistema operativo. Gestiona todo con `gitlab-ctl`.

```bash
# Ubuntu/Debian — ejemplo rápido (siempre consulta docs.gitlab.com para la versión actual)
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="https://gitlab.tudominio.com" apt install gitlab-ce

# Gestión posterior
sudo gitlab-ctl reconfigure    # aplica cambios en /etc/gitlab/gitlab.rb
sudo gitlab-ctl status         # estado de todos los servicios
sudo gitlab-ctl restart        # reinicia todo
sudo gitlab-ctl tail           # logs en vivo
```

**Pros:** instalación de un comando, Let's Encrypt automático, soporte oficial, backups integrados con `gitlab-backup create`.
**Contras:** instala su propio PostgreSQL/Redis/Nginx (puede chocar si ya tienes esos servicios en el host), más difícil de orquestar con otras apps.

**Cuándo usarlo:** VPS o servidor dedicado para GitLab únicamente.

---

### 2. Docker / Docker Compose — recomendado para homelab ⭐

Permite correr GitLab aislado, junto a otras apps, y es fácil de respaldar y mover.

> **Nota de jerga:** el paquete `gitlab-ce` es la edición Community (gratis y open-source). `gitlab-ee` es Enterprise (licencia de pago, con fallback a features gratuitos). Para homelab siempre CE.

#### `docker-compose.yml` básico y comentado

```yaml
version: "3.8"

services:
  gitlab:
    image: gitlab/gitlab-ce:latest          # usa una tag fija en producción: 17.0.1-ce.0
    container_name: gitlab
    restart: unless-stopped

    environment:
      GITLAB_OMNIBUS_CONFIG: |
        # URL externa — GitLab la usa para generar links en emails, webhooks, etc.
        external_url 'https://gitlab.tudominio.com'

        # --- TLS ---
        # Opción A: Nginx interno con Let's Encrypt (necesitas puerto 80/443 abierto al exterior)
        # letsencrypt['enable'] = true
        # letsencrypt['contact_emails'] = ['tu@email.com']

        # Opción B: TLS gestionado externamente (Cloudflare Tunnel, Nginx proxy externo)
        # Dile a GitLab que NO gestione TLS:
        nginx['listen_port'] = 80
        nginx['listen_https'] = false
        nginx['proxy_set_headers'] = {
          "X-Forwarded-Proto" => "https",
          "X-Forwarded-Ssl"   => "on"
        }

        # --- SSH ---
        gitlab_rails['gitlab_shell_ssh_port'] = 2222   # puerto SSH expuesto al usuario

        # --- Performance: ajusta workers según tu RAM ---
        # Con 4 GB RAM: 2 workers Puma, 5 Sidekiq
        puma['worker_processes'] = 2
        sidekiq['concurrency'] = 5

        # --- Email (SMTP) ---
        # gitlab_rails['smtp_enable'] = true
        # gitlab_rails['smtp_address'] = "smtp.gmail.com"
        # gitlab_rails['smtp_port'] = 587
        # gitlab_rails['smtp_user_name'] = "tu@gmail.com"
        # gitlab_rails['smtp_password'] = "app-password"
        # gitlab_rails['smtp_domain'] = "gmail.com"
        # gitlab_rails['smtp_authentication'] = "login"
        # gitlab_rails['smtp_enable_starttls_auto'] = true
        # gitlab_rails['gitlab_email_from'] = 'gitlab@tudominio.com'

    ports:
      - "8929:80"      # HTTP interno (si usas proxy externo en 443, apunta a este)
      - "2222:22"      # SSH para git push/pull vía SSH

    volumes:
      # ⚠️ Estos tres volúmenes son TODO tu GitLab. Respaldar = respaldar estas carpetas.
      - ./gitlab/config:/etc/gitlab          # configuración (gitlab.rb, secrets...)
      - ./gitlab/logs:/var/log/gitlab        # logs de todos los componentes
      - ./gitlab/data:/var/opt/gitlab        # repos, uploads, artifacts, DB, Redis...

    shm_size: '256m'    # necesario para PostgreSQL dentro del contenedor

    # GitLab tarda ~3-5 minutos en arrancar la primera vez. Paciencia.
```

```bash
# Primer arranque
docker compose up -d

# Ver logs en vivo (espera hasta ver "gitlab Reconfigured!")
docker compose logs -f gitlab

# Obtener contraseña inicial de root
docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password

# Consola Rails (equivalente a manage.py shell de Django — para tareas admin)
docker exec -it gitlab gitlab-rails console
```

**Estructura de carpetas resultante:**
```
proyecto/
├── docker-compose.yml
└── gitlab/
    ├── config/          # ← respaldar siempre
    │   ├── gitlab.rb
    │   └── gitlab-secrets.json   # ⚠️ NUNCA pierdes esto (claves de cifrado de BD)
    ├── logs/
    └── data/            # ← el más grande (repos + artifacts)
```

---

### 3. Helm / Kubernetes — para entornos de producción a escala

La [Chart oficial de GitLab](https://docs.gitlab.com/charts/) despliega cada componente como un Deployment separado (Puma, Sidekiq, Gitaly, Registry...), con escalado horizontal independiente.

```bash
helm repo add gitlab https://charts.gitlab.io/
helm install gitlab gitlab/gitlab \
  --set global.hosts.domain=tudominio.com \
  --set certmanager-issuer.email=tu@email.com
```

**Cuándo usarlo:** equipos grandes, necesitas HA (alta disponibilidad), ya tienes un cluster K8s. Para homelab o equipo pequeño es sobreingeniería — usa Docker Compose.

---

## 🔒 HTTPS y exposición segura

### El problema de exponer GitLab a internet

Abrir el puerto 443 directamente al exterior es la opción obvia pero la más peligrosa: expones la interfaz admin a internet, y GitLab tiene superficie de ataque significativa.

**Dos alternativas seguras (sin abrir puertos en el router):**

#### Opción A: Cloudflare Tunnel (antes Argo Tunnel)

```bash
# Instala cloudflared en el host
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared

cloudflared login                         # abre navegador, vincula tu dominio
cloudflared tunnel create gitlab-tunnel
cloudflared tunnel route dns gitlab-tunnel gitlab.tudominio.com

# config.yml del tunnel
cat > ~/.cloudflared/config.yml <<EOF
tunnel: <ID-del-tunnel>
credentials-file: /root/.cloudflared/<ID>.json
ingress:
  - hostname: gitlab.tudominio.com
    service: http://localhost:8929        # puerto del contenedor de GitLab
  - service: http_status:404
EOF

cloudflared service install && systemctl start cloudflared
```

**Resultado:** tráfico va `usuario → Cloudflare (TLS) → cloudflared (en tu casa) → GitLab`. Tu IP nunca es pública.

**Limitación importante:** Cloudflare Tunnel **no soporta bien SSH** (git push por SSH). Tendrás que usar HTTPS para git o abrir solo el puerto 2222 de SSH (que es menos arriesgado que el 443).

#### Opción B: Tailscale (VPN mesh)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Ahora tu servidor tiene una IP privada Tailscale (ej: 100.x.x.x)
# Accedes desde cualquier dispositivo en tu tailnet: http://100.x.x.x:8929
```

**Resultado:** GitLab solo accesible desde dispositivos en tu red Tailscale. Más privado que Cloudflare (Cloudflare ve el tráfico). Ideal para uso personal/equipo pequeño de confianza.

**Pros/Contras rápidos:**

| | Cloudflare Tunnel | Tailscale |
|---|---|---|
| Acceso público (sin VPN) | ✅ Sí | ❌ No (solo tailnet) |
| IP privada | ✅ | ✅ |
| SSH git nativo | ⚠️ Limitado | ✅ Completo |
| Coste | Gratis (Free plan) | Gratis hasta 3 usuarios |
| Confianza | Cloudflare ve tráfico | Solo tus devices |

---

## ⚙️ Requisitos reales de hardware

| Uso | RAM | CPU | Disco |
|---|---|---|---|
| Homelab / pruebas | 4 GB | 2 cores | 20 GB SSD |
| Equipo pequeño (5-10 devs) | 8 GB | 4 cores | 50-100 GB SSD |
| Equipo medio (20-50 devs, CI activo) | 16 GB | 8 cores | 200+ GB SSD |
| Producción seria | 32+ GB | 16+ cores | SSD NVMe RAID |

> **Disco:** GitLab guarda los repos, los artifacts de CI (pueden crecer mucho), el Registry de imágenes Docker, y la base de datos. Define una política de limpieza de artifacts (`expire_in` en `.gitlab-ci.yml`) desde el primer día.

---

## 🛡️ Errores comunes y cómo evitarlos

| Error | Consecuencia | Solución |
|---|---|---|
| Perder `gitlab-secrets.json` | **Pierdes acceso a toda la BD cifrada** | Respaldar junto con `gitlab/config/` en un lugar seguro |
| No configurar SMTP | Los usuarios no reciben emails de confirmación ni alertas | Configurar SMTP en `gitlab.rb` antes del primer usuario |
| Artifacts sin expiración | Disco lleno en semanas con CI activo | Añadir `expire_in: 1 week` por defecto en `.gitlab-ci.yml` |
| Actualizar sin leer release notes | Migraciones de BD que rompen la instancia | Actualizar de versión major en versión major, nunca saltar |
| Abrir puerto 443 directo al router | Superficie de ataque innecesaria | Usar Cloudflare Tunnel o Tailscale |
| Memoria insuficiente | OOM killer mata PostgreSQL o Gitaly, GitLab queda roto | Respetar mínimo de 4 GB, añadir swap como safety net |

**Añadir swap como safety net (Linux):**
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 💾 Backups

```bash
# Con Omnibus (en el host)
sudo gitlab-backup create

# Con Docker
docker exec -t gitlab gitlab-backup create
# El backup queda en: gitlab/data/backups/

# ⚠️ El backup de gitlab-backup NO incluye gitlab.rb ni gitlab-secrets.json
# Debes respaldar esos archivos APARTE (están en gitlab/config/)
```

Estrategia mínima viable: backup diario con cron → rsync a disco externo o rclone a nube.

---

## 🚀 Aplícalo a tus proyectos

**app web y proyecto embebido:** ambos son proyectos que podrías alojar en una instancia GitLab self-hosted si quieres CI/CD propio con runners en tu máquina local (sin límite de minutos CI, sin exponer código a GitLab.com).

**Flujo de trabajo práctico:**
1. Levantar GitLab CE con Docker Compose en un VPS de 4 GB (ej: Hetzner CX21, ~5€/mes) o en tu propio servidor.
2. Exponer con Tailscale para acceso desde tu máquina de desarrollo.
3. Registrar un GitLab Runner en el mismo host (o en tu máquina local) — ver [[06-runners]].
4. Migrar repos: `git remote add gitlab http://...` y `git push gitlab --all`.

**Para proyecto embebido (firmware embebido):** self-hosting tiene ventaja adicional de poder instalar toolchains de compilación (arm-none-eabi, PlatformIO) en runners propios sin consumir minutos de CI externos.

---

## Conexiones

- [[MOC_GitLab]]
- [[01-que-es-gitlab]]
- [[05-gitlab-cicd-fundamentos]]
- [[06-runners]]
- [[07-cicd-avanzado]]
- [[08-registry-paquetes-y-pages]]
- [[11-administracion-backups-upgrades]]
- [[12-gitlab-vs-alternativas]]
- [[MOC_Desarrollo_Software]]
