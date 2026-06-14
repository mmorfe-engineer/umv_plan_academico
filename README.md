# Academic Tracker - UVM Plan Academico

Sistema completo de seguimiento y automatizacion de obligaciones academicas universitarias.

## Caracteristicas

- **Notificaciones automaticas** via Slack y Gmail
- **Dashboard visual** publicado en GitHub Pages
- **Gestion de actividades** con alertas programadas
- **Sincronizacion automatica** con cron jobs diarios y semanales

## Estructura del Proyecto

```
umv_plan_academico/
├── data/
│   └── obligaciones.json          # Fuente unica de verdad
├── scripts/
│   ├── notify.py                  # Logica de alertas Slack + Gmail
│   └── generate_dashboard.py      # Genera docs/index.html
├── .github/
│   └── workflows/
│       ├── daily_check.yml        # Check diario a las 9:00 AM Caracas
│       ├── weekly_monday.yml      # Revision semanal los lunes
│       └── deploy_dashboard.yml   # Deploy automatico a GitHub Pages
├── docs/
│   └── index.html                 # Tablero visual
├── requirements.txt
└── README.md
```

## Configuracion

### 1. Crear el repositorio en GitHub

1. Crear repositorio: `mmorfe-engineer/umv_plan_academico`
2. Activar GitHub Pages:
   - Settings → Pages
   - Source: `Deploy from a branch`
   - Branch: `main` | Folder: `/docs`

### 2. Configurar Secrets en GitHub

Ir a: **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Descripcion |
|---|---|
| `SLACK_WEBHOOK_URL` | URL del Incoming Webhook de Slack |
| `GMAIL_USER` | Cuenta Gmail remitente |
| `GMAIL_APP_PASS` | App Password de Gmail (16 caracteres) |

#### Como obtener SLACK_WEBHOOK_URL:
1. Ir a https://api.slack.com/apps → "Create New App" → "From scratch"
2. Nombre: `AcademicTracker` | Workspace: el personal
3. En "Add features": activar **Incoming Webhooks**
4. Click en "Add New Webhook to Workspace"
5. Seleccionar el canal `#plan-academico`
6. Copiar la URL generada → pegarla en el secret

#### Como obtener GMAIL_APP_PASS:
1. Ir a https://myaccount.google.com/security
2. Activar **Verificacion en 2 pasos** si no esta activa
3. Buscar **"Contraseñas de aplicaciones"**
4. App: "Otra (nombre personalizado)" → escribir `AcademicTracker`
5. Copiar los 16 caracteres generados → pegarlos en secret `GMAIL_APP_PASS`
6. En `GMAIL_USER` poner la cuenta `@gmail.com` que genero el App Password

### 3. Clonar el repositorio y subir los archivos

```bash
git clone https://github.com/mmorfe-engineer/umv_plan_academico.git
cd umv_plan_academico
# Copiar todos los archivos creados
 git add .
git commit -m "Initial commit - Academic Tracker setup"
git push origin main
```

## Uso

### Modificar actividades

Editar el archivo `data/obligaciones.json` y hacer commit/push:
- Cambiar `estado` entre: `pendiente`, `en_progreso`, `entregado`
- Configurar `alerta: true` para recibir notificaciones
- Configurar `recordatorios_dias: [7, 3, 1, 0]` para dias de alerta
- Configurar `revision_semanal_lunes: true` para revision semanal

### Workflows disponibles

- **Daily Academic Check**: Ejecuta todos los dias a las 9:00 AM Caracas (13:00 UTC)
  - Envia notificaciones por Slack y Gmail segun los recordatorios configurados
  
- **Weekly Monday Review**: Ejecuta todos los lunes a las 9:00 AM Caracas
  - Envia recordatorios para actividades con `revision_semanal_lunes: true`
  
- **Deploy Dashboard**: Se ejecuta automaticamente al hacer push a `main`
  - Regenera el dashboard HTML y lo despliega en GitHub Pages

### Ejecutar manualmente

Para ejecutar los workflows manualmente:
1. Ir a GitHub → Actions
2. Seleccionar el workflow deseado
3. Click en "Run workflow" → "Run workflow"

## Dashboard Publico

El dashboard estara disponible en: https://mmorfe-engineer.github.io/umv_plan_academico

## Requerimientos

- Python 3.11+
- Librerias: `requests`, `pytz` (instaladas via `requirements.txt`)

## Licencia

Proyecto academico personal - Martin Morfe Flores
