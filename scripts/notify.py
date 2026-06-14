"""Script de notificaciones para Academic Tracker.

Envia alertas via Slack Webhook y Gmail SMTP segun las obligaciones academicas.
Uso: python scripts/notify.py [modo]
  modo: "normal" (default) - alertas por dias restantes
        "lunes" - revisiones semanales de lunes
"""

import json
import os
import sys
import subprocess
import requests
import smtplib
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# DEBUG: Mostrar commit actual
try:
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=".").decode().strip()
    print(f"🔥 GIT COMMIT: {commit_hash}")
except Exception as e:
    print(f"⚠️  No se pudo obtener commit: {e}")

# =============================================================================
# Configuracion y Validacion
# =============================================================================

def validate_environment():
    """Valida que todas las variables de entorno requeridas esten configuradas."""
    required_vars = {
        "SLACK_WEBHOOK_URL": "URL del Incoming Webhook de Slack",
        "GMAIL_USER": "Cuenta Gmail remitente (ej: tuemail@gmail.com)",
        "GMAIL_APP_PASS": "App Password de Gmail de 16 caracteres",
    }
    
    missing = []
    for var_name, description in required_vars.items():
        if not os.environ.get(var_name):
            missing.append(f"{var_name} ({description})")
    
    if missing:
        raise EnvironmentError(
            "Faltan variables de entorno requeridas:\n" + 
            "\n".join(f"  - {m}" for m in missing) + 
            "\n\nConfiguralas en GitHub Secrets o en tu entorno local."
        )

# Validar antes de continuar
validate_environment()

# Obtener configuracion
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASS = os.environ["GMAIL_APP_PASS"]

# =============================================================================
# Constantes
# =============================================================================

# Emojis por tipo de actividad
EMOJI_TIPO = {
    "grupo c": "📝",
    "examen": "📝",
    "anteproyecto": "📐",
    "proyecto": "🚀",
    "programar": "💻",
    "trabajo en grupo": "👥",
    "flyer": "🎨",
}

# Emojis por nivel de urgencia
EMOJI_URGENCIA = {
    7: "📅",
    3: "⚠️",
    1: "🔴",
    0: "🚨",
}

# =============================================================================
# Funciones de Utilidad
# =============================================================================

def get_fecha_display(ob):
    """Obtiene la representacion de fecha para display."""
    if "fecha" in ob:
        return ob["fecha"]
    return f'{ob.get("fecha_inicio", "?")} → {ob.get("fecha_fin", "?")}'


def get_fecha_limite(ob):
    """Obtiene la fecha limite como objeto date."""
    if "fecha" in ob:
        return datetime.strptime(ob["fecha"], "%Y-%m-%d").date()
    if "fecha_fin" in ob:
        return datetime.strptime(ob["fecha_fin"], "%Y-%m-%d").date()
    return None


def get_fecha_inicio(ob):
    """Obtiene la fecha de inicio como objeto date."""
    if "fecha_inicio" in ob:
        return datetime.strptime(ob["fecha_inicio"], "%Y-%m-%d").date()
    if "fecha" in ob:
        return datetime.strptime(ob["fecha"], "%Y-%m-%d").date()
    return None


def get_rango_semananal():
    """Obtiene el lunes de esta semana y el domingo de la próxima semana (2 semanas de cobertura)."""
    hoy = date.today()
    # Lunes de esta semana
    lunes_esta_semana = hoy - timedelta(days=hoy.weekday())
    # Domingo de la próxima semana
    domingo_proxima_semana = lunes_esta_semana + timedelta(days=13)
    return lunes_esta_semana, domingo_proxima_semana


def actividad_en_periodo_semananal(ob):
    """Verifica si la actividad tiene alguna fecha en las próximas 2 semanas (esta semana + siguiente)."""
    lunes_esta_semana, domingo_proxima_semana = get_rango_semananal()
    
    # Verificar fecha única
    fecha_limite = get_fecha_limite(ob)
    if fecha_limite and lunes_esta_semana <= fecha_limite <= domingo_proxima_semana:
        return True
    
    # Verificar rango de fechas (fecha_inicio a fecha_fin)
    fecha_inicio = get_fecha_inicio(ob)
    if fecha_inicio:
        if "fecha_fin" in ob:
            fecha_fin = datetime.strptime(ob["fecha_fin"], "%Y-%m-%d").date()
            # Verificar si la actividad TERMINA dentro de las 2 semanas
            if lunes_esta_semana <= fecha_fin <= domingo_proxima_semana:
                return True
        elif lunes_esta_semana <= fecha_inicio <= domingo_proxima_semana:
            return True
    
    return False


def load_data():
    """Carga los datos de obligaciones desde el JSON."""
    try:
        with open("data/obligaciones.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            "Archivo data/obligaciones.json no encontrado. "
            "Asegurate de estar en el directorio correcto."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON: {e}")

# =============================================================================
# Funciones de Notificacion
# =============================================================================

def send_slack(ob, dias, canal, pages_url, modo="normal"):
    """Envía notificacion a Slack."""
    emoji_u = EMOJI_URGENCIA.get(dias, "📌") if modo == "normal" else "🔁"
    emoji_t = EMOJI_TIPO.get(ob.get("tipo", "").lower(), "📌")
    materia = ob["materia"]
    titulo = ob["titulo"]
    fecha_d = get_fecha_display(ob)
    nota = ob.get("nota", "")

    if modo == "lunes":
        # Si hay dias restantes, mostrar urgencia
        if dias is not None:
            if dias == 0:
                urgencia_txt = "🚨 *¡VENCE HOY!*"
            elif dias == 1:
                urgencia_txt = "🔴 *¡Vence MAÑANA!*"
            elif dias <= 3:
                urgencia_txt = f"⚠️ *Vence en {dias} días*"
            elif dias <= 7:
                urgencia_txt = f"📅 *Vence en {dias} días*"
            else:
                urgencia_txt = f"📅 *Vence en {dias} días*"
            texto = (
                f"{urgencia_txt}\n"
                f"{emoji_t} *{materia}* · {titulo}\n"
                f"📆 Fecha: `{get_fecha_display(ob)}`\n"
                f"📋 {nota}\n"
                f"🔗 Tablero: {pages_url}"
            )
        else:
            texto = (
                f"🔁 *REVISIÓN SEMANAL — LUNES*\n"
                f"{emoji_t} *{materia}* · {titulo}\n"
                f"📋 {nota}\n"
                f"🔗 Tablero: {pages_url}"
            )
    else:
        if dias == 0:
            urgencia_txt = "🚨 *¡VENCE HOY!*"
        elif dias == 1:
            urgencia_txt = "🔴 *¡Vence MAÑANA!*"
        elif dias == 3:
            urgencia_txt = "⚠️ *Vence en 3 días*"
        else:
            urgencia_txt = f"📅 Vence en {dias} días"

        texto = (
            f"{urgencia_txt}\n"
            f"{emoji_t} *{materia}* · {titulo}\n"
            f"📆 Fecha: `{fecha_d}`\n"
            f"🔗 Ver tablero: {pages_url}"
        )

    payload = {"text": texto, "channel": canal}
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        print(f"✅ Slack [{r.status_code}] → {materia} / {titulo}")
        return True
    except requests.RequestException as e:
        print(f"❌ Error Slack: {e}")
        return False


def send_email(ob, dias, email_list, pages_url, modo="normal"):
    """Envía notificacion por email."""
    materia = ob["materia"]
    titulo = ob["titulo"]
    fecha_d = get_fecha_display(ob)

    if modo == "lunes":
        if dias is not None:
            if dias == 0:
                subject = f"🚨 VENCE HOY — {materia}: {titulo}"
            elif dias == 1:
                subject = f"🔴 Vence MAÑANA — {materia}: {titulo}"
            elif dias <= 3:
                subject = f"⚠️ Vence en {dias} días — {materia}: {titulo}"
            else:
                subject = f"📅 Revisión semanal — {materia}: {titulo}"
            body = (
                f"Recordatorio académico - Revisión de lunes.\n\n"
                f"Materia:    {materia}\n"
                f"Actividad:  {titulo}\n"
                f"Tipo:       {ob.get('tipo', '')}\n"
                f"Fecha:      {get_fecha_display(ob)}\n"
                f"Días rest.: {dias} días\n"
                f"Nota:       {ob.get('nota', '')}\n\n"
                f"Ver tablero completo: {pages_url}"
            )
        else:
            subject = f"🔁 Revisión semanal — {materia}"
            body = (
                f"Revisión programada de lunes.\n\n"
                f"Materia: {materia}\n"
                f"Actividad: {titulo}\n"
                f"Nota: {ob.get('nota', '')}\n\n"
                f"Ver tablero completo: {pages_url}"
            )
    else:
        if dias == 0:
            subject = f"🚨 VENCE HOY — {materia}: {titulo}"
        elif dias == 1:
            subject = f"🔴 Vence MAÑANA — {materia}: {titulo}"
        elif dias == 3:
            subject = f"⚠️ 3 días — {materia}: {titulo}"
        else:
            subject = f"📅 {dias} días — {materia}: {titulo}"

        body = (
            f"Recordatorio académico.\n\n"
            f"Materia:    {materia}\n"
            f"Actividad:  {titulo}\n"
            f"Tipo:       {ob.get('tipo', '')}\n"
            f"Fecha:      {fecha_d}\n\n"
            f"Ver tablero completo: {pages_url}"
        )

    # Enviar email individual a cada destinatario
    emails_sent = 0
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            
            for dest in email_list:
                msg = MIMEMultipart()
                msg["From"] = GMAIL_USER
                msg["To"] = dest
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))
                
                server.sendmail(GMAIL_USER, dest, msg.as_string())
                print(f"✅ Email → {dest} [{materia}]")
                emails_sent += 1
    except smtplib.SMTPException as e:
        print(f"❌ Error Gmail: {e}")
    
    return emails_sent > 0


# =============================================================================
# Logica Principal
# =============================================================================

def run(modo="normal"):
    """Ejecuta el proceso de notificaciones."""
    data = load_data()
    meta = data["meta"]
    canal = meta["canal_slack"]
    emails = meta["email_to"]
    pages_url = meta["github_pages_url"]
    hoy = date.today()
    
    # DEBUG: Mostrar fecha del servidor y rango
    if modo == "lunes":
        lunes, domingo = get_rango_semananal()
        print(f"🔍 DEBUG - Fecha servidor: {hoy}")
        print(f"🔍 DEBUG - Rango semanal: {lunes} → {domingo}")

    if not emails:
        print("⚠️  No hay destinatarios de email configurados")
    if not canal:
        print("⚠️  No hay canal de Slack configurado")

    for ob in data["obligaciones"]:
        # Revision semanal lunes - Enviar actividades de las proximas 2 semanas
        if modo == "lunes":
            # Verificar si tiene fechas definidas
            tiene_fecha = "fecha" in ob or "fecha_inicio" in ob or "fecha_fin" in ob
            
            if actividad_en_periodo_semananal(ob):
                # Calcular dias restantes si tiene fecha limite
                dias_restantes = None
                fecha_limite = get_fecha_limite(ob)
                if fecha_limite:
                    dias_restantes = (fecha_limite - hoy).days
                
                send_slack(ob, dias_restantes, canal, pages_url, modo="lunes")
                send_email(ob, dias_restantes, emails, pages_url, modo="lunes")
            # Solo enviar actividades SIN fechas pero con revision_semanal_lunes
            elif not tiene_fecha and ob.get("revision_semanal_lunes"):
                send_slack(ob, None, canal, pages_url, modo="lunes")
                send_email(ob, None, emails, pages_url, modo="lunes")
            continue

        # Alerta por dias restantes
        if modo == "normal" and ob.get("alerta") and ob.get("recordatorios_dias"):
            fecha_limite = get_fecha_limite(ob)
            if fecha_limite:
                dias = (fecha_limite - hoy).days
                if dias in ob["recordatorios_dias"]:
                    send_slack(ob, dias, canal, pages_url)
                    send_email(ob, dias, emails, pages_url)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "normal"
    print(f"Iniciando notificaciones en modo: {modo}")
    try:
        run(modo)
        print("Notificaciones enviadas correctamente")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
