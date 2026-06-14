# 🎓 Academic Tracker UVM

[![GitHub stars](https://img.shields.io/github/stars/mmorfe-engineer/umv_plan_academico?style=social)](https://github.com/mmorfe-engineer/umv_plan_academico/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mmorfe-engineer/umv_plan_academico?style=social)](https://github.com/mmorfe-engineer/umv_plan_academico/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/weekly_monday.yml/badge.svg)](https://github.com/mmorfe-engineer/umv_plan_academico/actions)
[![Last Commit](https://img.shields.io/github/last-commit/mmorfe-engineer/umv_plan_academico)](https://github.com/mmorfe-engineer/umv_plan_academico/commits/main)

**Sistema de seguimiento académico para gestionar actividades, fechas de entrega y recordatorios automáticos para estudiantes de la Universidad Valle del Momboy (UVM).**

---

## 📋 Tabla de Contenidos
- [✨ Características](#-características)
- [🚀 Instalación](#-instalación)
- [🎯 Uso](#-uso)
- [📊 Workflows Automatizados](#-workflows-automatizados)
- [🗂️ Estructura del Proyecto](#-estructura-del-proyecto)
- [🛠️ Tecnologías](#-tecnologías)
- [📝 Contribuir](#-contribuir)
- [🤝 Código de Conducta](#-código-de-conducta)
- [📄 Licencia](#-licencia)
- [🙏 Créditos](#-créditos)

---

## ✨ Características

- ✅ **Notificaciones automáticas** por Slack y Email
- ✅ **Recordatorios semanales** de actividades académicas (todos los lunes)
- ✅ **Filtrado inteligente** por fechas (2 semanas de anticipación)
- ✅ **Dashboard HTML** con visualización de todas las obligaciones
- ✅ **Integración con GitHub Actions** para automatización completa
- ✅ **Soporte para múltiples materias** y tipos de actividades
- ✅ **Configuración flexible** de fechas y recordatorios

---

## 🚀 Instalación

### 📋 Requisitos Previos

- **Python** 3.11 o superior
- **pip** (gestor de paquetes de Python)
- Cuenta de **GitHub** (para clonar el repositorio)
- **Webhook de Slack** (opcional, para notificaciones en Slack)
- Cuenta **Gmail** con App Password (opcional, para notificaciones por email)

### 💻 Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/mmorfe-engineer/umv_plan_academico.git
   cd umv_plan_academico
   ```

2. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   Crea un archivo `.env` en el directorio raíz o configura las siguientes variables en tu entorno:
   ```bash
   # Para notificaciones por Slack
   export SLACK_WEBHOOK_URL="tu_webhook_url"
   
   # Para notificaciones por email
   export GMAIL_USER="tu_email@gmail.com"
   export GMAIL_APP_PASS="tu_app_password"
   ```

4. **Personalizar tus actividades:**
   Edita el archivo `data/obligaciones.json` para añadir tus materias, actividades y fechas:
   ```json
   {
     "materia": "Nombre de la materia",
     "titulo": "Nombre de la actividad",
     "tipo": "examen|trabajo en grupo|programar|etc",
     "fecha": "2026-06-19",  // o fecha_inicio y fecha_fin
     "estado": "pendiente|en_progreso|completado"
   }
   ```

---

## 🎯 Uso

### 📱 Ejecución Local

Para probar el sistema localmente:

```bash
# Notificaciones diarias (modo normal)
python scripts/notify.py normal

# Revisión semanal de lunes
python scripts/notify.py lunes
```

### 🔄 GitHub Actions (Automatización)

El repositorio incluye **3 workflows automatizados** que se ejecutan en GitHub Actions:

| Workflow | Descripción | Frecuencia | Estado |
|----------|-------------|------------|--------|
| `daily_check.yml` | Revisión diaria de actividades que vencen pronto | Diario a las 9:00 AM (UTC-4) | [![Daily Check](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/daily_check.yml/badge.svg)](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/daily_check.yml) |
| `weekly_monday.yml` | Revisión semanal de todas las actividades | Todos los lunes a las 9:00 AM | [![Weekly Monday](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/weekly_monday.yml/badge.svg)](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/weekly_monday.yml) |
| `deploy_dashboard.yml` | Despliegue del dashboard HTML | Manual | [![Deploy Dashboard](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/deploy_dashboard.yml/badge.svg)](https://github.com/mmorfe-engineer/umv_plan_academico/actions/workflows/deploy_dashboard.yml) |

---

## 🗂️ Estructura del Proyecto

```
umv_plan_academico/
├── .github/
│   └── workflows/
│       ├── daily_check.yml          # Notificaciones diarias
│       ├── weekly_monday.yml         # Revisión semanal
│       └── deploy_dashboard.yml     # Despliegue del dashboard
├── data/
│   └── obligaciones.json           # Datos de actividades académicas
├── scripts/
│   └── notify.py                   # Script principal de notificaciones
├── docs/                          # Documentación adicional
├── README.md                      # Este archivo
├── LICENSE                       # Licencia MIT
├── CONTRIBUTING.md               # Guía de contribución
├── CODE_OF_CONDUCT.md            # Código de conducta
├── requirements.txt               # Dependencias de Python
└── INFORME_AVANCE_MANTENIMIENTO.txt  # Informe de desarrollo
```

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.11+ | Lenguaje principal |
| **GitHub Actions** | - | Automatización de workflows |
| **Slack API** | - | Notificaciones por Slack |
| **SMTP (Gmail)** | - | Notificaciones por email |
| **JSON** | - | Formato de datos |
| **GitHub Pages** | - | Hosting del dashboard |

---

## 📝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee nuestro [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles sobre cómo contribuir al proyecto.

### 🚀 Pasos Básicos

1. **Haz un fork** del proyecto
2. **Crea una branch** para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. **Haz commit** de tus cambios (`git commit -m 'feat: añade nueva característica'`)
4. **Empuja** a tu branch (`git push origin feature/nueva-caracteristica`)
5. **Abre un Pull Request**

---

## 🤝 Código de Conducta

Todos los contribuyentes deben seguir nuestro [Código de Conducta](CODE_OF_CONDUCT.md). Esperamos que todos los participantes mantengan un ambiente respetuoso y colaborativo.

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT** - mira el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Créditos

**Desarrollado por:**
- [Martin Morfe Flores](https://github.com/mmorfe-engineer) - Autor principal
- Martin Alejandro Morfe Carballo - Contribuidor

**Universidad:** Universidad Valle del Momboy (UVM)

**Año:** 2026

---

*© 2026 Martin Morfe Flores & Martin Alejandro Morfe Carballo*
