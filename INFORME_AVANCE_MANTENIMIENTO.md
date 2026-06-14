# 📊 INFORME DE AVANCE Y MANTENIMIENTO - ACADEMIC TRACKER UVM

---

## 📅 FECHA: 14 de Junio de 2026
## 👤 RESPONSABLE: Mistral Vibe (Senior DevOps Engineer)
## 🎯 PROYECTO: Academic Tracker UVM

---

## ✅ AVANCE DEL PROYECTO

### Estado Inicial
- **Estado del proyecto:** 95% completado
- **Problema identificado:** Workflow Weekly Monday Review no mostraba actividades con fechas específicas (Humanitas Flyer, Backend Programar, Estadística Trabajo en Grupo) que vencen el 19 de junio de 2026
- **Solo mostraba:** Actividades con nota de revisión (Humanitas y Álgebra)

### Problemas Resueltos

#### 1️⃣ **Problema de Versión en GitHub Actions**
- **Síntoma:** GitHub Actions ejecutaba código antiguo (commit `1a86304`) en lugar del nuevo (commit `1bd70e0`)
- **Causa:** Cache de GitHub Actions y uso de "Re-run all jobs" en lugar de "Run workflow"
- **Solución aplicada:**
  - Modificación de `weekly_monday.yml` para usar `fetch-depth: 0` y `clean: true`
  - adición de debug en `notify.py` para mostrar commit hash
  - Commit final: `53af8a6`
- **Resultado:** ✅ GitHub Actions ahora usa el código actualizado

#### 2️⃣ **Problema de Filtrado de Fechas**
- **Síntoma:** Se enviaban TODAS las actividades, incluyendo las de julio
- **Causa:** La función `actividad_en_periodo_semananal()` aceptaba superposiciones parciales de rangos de fechas
- **Solución aplicada:**
  - Modificación de la lógica en `notify.py` línea 135
  - Cambio de: `if fecha_fin >= lunes_esta_semana and fecha_inicio <= domingo_proxima_semana:`
  - A: `if lunes_esta_semana <= fecha_fin <= domingo_proxima_semana:`
  - Eliminación del envío de actividades sin fechas con `revision_semanal_lunes`
- **Resultado:** ✅ Solo se envían actividades que terminan dentro de las 2 semanas

#### 3️⃣ **Problema de Notificaciones Redundantes**
- **Síntoma:** Mensajes redundantes en Slack (notas de Humanitas y Álgebra sin sentido)
- **Causa:** Campos `nota` y `revision_semanal_lunes` en actividades que ya no los necesitaban
- **Solución aplicada:**
  - Eliminación del campo `nota` de Humanitas
  - Eliminación de campos `revision_semanal_lunes` y `nota` de Álgebra de Estructura
  - Eliminación de la lógica de envío para actividades sin fechas
- **Resultado:** ✅ Solo se envían actividades con fechas válidas en el rango

#### 4️⃣ **Problema de Email Bloqueado**
- **Síntoma:** Email a morfecarballom@uvm.edu.ve se devuelven por cuenta bloqueada
- **Solución aplicada:**
  - Eliminación de morfecarballom@uvm.edu.ve de la lista `email_to` en `obligaciones.json`
- **Resultado:** ✅ Solo se envía a morfefloresm@uvm.edu.ve

---

## 📈 RESULTADO FINAL

### Workflow Weekly Monday Review - Funcionando Correctamente

**Para fecha: 14 de Junio de 2026 (Rango: 2026-06-09 → 2026-06-23)**

| Materia | Actividad | Fecha | Días restantes | Estado |
|---------|-----------|-------|----------------|--------|
| Humanitas | Flyer | 2026-05-22 → 2026-06-19 | 5 días | ✅ Enviado |
| Backend (Ingeniería de la Programación) | Programar | 2026-06-12 → 2026-06-19 | 5 días | ✅ Enviado |
| Estadística Descriptiva | Trabajo en Grupo | 2026-05-04 → 2026-06-19 | 5 días | ✅ Enviado |

**Actividades NO enviadas (correctamente filtradas):**
- ❌ Álgebra de Estructura · Examen (ya terminó: 2026-05-30)
- ❌ Estadística · Trabajo en Grupo (2026-05-31 → 2026-07-24)
- ❌ Estadística · Trabajo en Grupo (2026-05-31 → 2026-07-26)
- ❌ Todas las de Principio de Electricidad (fechas en julio)
- ❌ Todas las de Física I (fechas en julio)
- ❌ Backend (Avance del Proyecto, Proyecto Final - fechas en julio)

---

## 🔧 CAMBIOS REALIZADOS

### Archivos Modificados

1. **`.github/workflows/weekly_monday.yml`**
   - Añadido `fetch-depth: 0` y `clean: true` al paso de checkout
   - Esto fuerza a GitHub Actions a descargar el código fresco

2. **`scripts/notify.py`**
   - Añadido debug de commit hash para diagnóstico
   - Modificado `actividad_en_periodo_semananal()` para filtrar por fecha_fin
   - Eliminado el envío de actividades sin fechas
   - Comits: `1bd70e0`, `4edaf16`, `7644b1a`, `b3ce3aa`, `4dba197`, `53af8a6`

3. **`data/obligaciones.json`**
   - Eliminado campo `nota` de Humanitas
   - Eliminado campos `revision_semanal_lunes` y `nota` de Álgebra de Estructura
   - Eliminado email morfecarballom@uvm.edu.ve
   - Commit: `53af8a6`

---

## 🛠️ FUTURO MANTENIMIENTO

### Recomendaciones

#### 1. **Mantenimiento de Fechas**
- **Frecuencia:** Revisar semanalmente el archivo `data/obligaciones.json`
- **Acción:** Actualizar fechas de actividades según el calendario académico
- **Herramienta:** Usar el workflow Weekly Monday Review para validar que las actividades aparecen correctamente

#### 2. **Monitoreo de GitHub Actions**
- **Frecuencia:** Diaria
- **Acción:** Verificar que los workflows se ejecuten con el commit correcto
- **Indicador:** Buscar la línea `[command]/usr/bin/git log -1 --format=%H` en los logs
- **Alarma:** Si el commit no es el último de main, forzar re-ejecución con "Run workflow"

#### 3. **Limpieza de Datos**
- **Frecuencia:** Cada inicio de período académico
- **Acción:** 
  - Eliminar actividades ya finalizadas
  - Verificar que todas las actividades tengan fechas válidas
  - Eliminar campos `revision_semanal_lunes` de actividades con fechas específicas

#### 4. **Actualización de Dependencias**
- **Frecuencia:** Mensual
- **Acción:** Actualizar `requirements.txt` con las últimas versiones de:
  - requests
  - pytz
- **Comando:** `pip install -r requirements.txt --upgrade`

#### 5. **Backup**
- **Frecuencia:** Semanal
- **Acción:** Hacer backup del repositorio
- **Comando:** `git archive --format=zip --output=backup_$(date +%Y%m%d).zip main`

---

## 📝 REGISTRO DE COMMITS

| Commit | Mensaje | Cambios |
|--------|---------|---------|
| `1bd70e0` | debug: agregar impresion de fecha del servidor para diagnostico | Añadido debug en notify.py |
| `48e2ed1` | feat: Weekly Monday ahora incluye actividades de las proximas 2 semanas | Modificación inicial de rango |
| `4edaf16` | chore: forzar actualizacion de GitHub Actions | Archivo temporal para forzar update |
| `7644b1a` | fix: forzar checkout completo en workflow | Añadido fetch-depth: 0 |
| `b3ce3aa` | fix: forzar commit hash en debug + cleanup checkout | Añadido clean: true y git commit hash |
| `4dba197` | fix: filtrar actividades por fecha_fin dentro de 2 semanas | Corrección de lógica de filtrado |
| `53af8a6` | fix: solo reportar actividades con fechas en rango de 2 semanas | Eliminación de notas y envío solo por fechas |

---

## ✅ ESTADO FINAL DEL PROYECTO

- **Estado:** ✅ **100% COMPLETADO**
- **Workflow Weekly Monday Review:** ✅ Funcionando correctamente
- **Filtrado de fechas:** ✅ Solo envía actividades en rango de 2 semanas
- **Notificaciones:** ✅ Solo a morfefloresm@uvm.edu.ve (Slack + Email)
- **Mensajes:** ✅ Sin redundancias, solo información relevante

---

## 🎓 CONCLUSIONES

El proyecto Academic Tracker UVM ha sido completado exitosamente. Se resolvieron todos los problemas identificados:

1. ✅ GitHub Actions ahora usa el código actualizado
2. ✅ El filtrado de fechas funciona correctamente (solo 2 semanas)
3. ✅ Se eliminaron notificaciones redundantes
4. ✅ Se eliminó el email bloqueado

**El sistema está listo para producción.**

---

*Generado por Mistral Vibe - Senior DevOps Engineer*
*Fecha: 14 de Junio de 2026*
