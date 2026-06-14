import json
import os
import requests
import smtplib
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -- Secrets desde variables de entorno (GitHub Actions secrets) --
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
GMAIL_USER        = os.environ["GMAIL_USER"]        # cuenta @gmail.com remitente
GMAIL_APP_PASS    = os.environ["GMAIL_APP_PASS"]    # App Password de Gmail
PAGES_URL         = "https://mmorfe-engineer.github.io/umv_plan_academico"

# -- Emojis por tipo --
EMOJI_TIPO = {
    "grupo c":        "📝",
    "examen":         "📝",
    "anteproyecto":   "📐",
    "proyecto":       "🚀",
    "programar":      "💻",
    "trabajo en grupo": "👥",
    "flyer":          "🎨",
}

EMOJI_URGENCIA = {
    7: "📅",
    3: "⚠️",
    1: "🔴",
    0: "🚨",
}

def get_fecha_display(ob):
    if "fecha" in ob:
        return ob["fecha"]
    return f'{ob.get("fecha_inicio","?")} → {ob.get("fecha_fin","?")}'

def get_fecha_limite(ob):
    if "fecha" in ob:
        return datetime.strptime(ob["fecha"], "%Y-%m-%d").date()
    if "fecha_fin" in ob:
        return datetime.strptime(ob["fecha_fin"], "%Y-%m-%d").date()
    return None

def send_slack(ob, dias, canal, pages_url, modo="normal"):
    emoji_u  = EMOJI_URGENCIA.get(dias, "📌") if modo == "normal" else "🔁"
    emoji_t  = EMOJI_TIPO.get(ob.get("tipo","").lower(), "📌")
    materia  = ob["materia"]
    titulo   = ob["titulo"]
    fecha_d  = get_fecha_display(ob)
    nota     = ob.get("nota","")

    if modo == "lunes":
        texto = (
            f"{emoji_u} *REVISION SEMANAL — LUNES*\n"
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
    r = requests.post(SLACK_WEBHOOK_URL, json=payload)
    print(f"Slack [{r.status_code}] → {materia} / {titulo}")

def send_email(ob, dias, email_list, pages_url, modo="normal"):
    materia = ob["materia"]
    titulo  = ob["titulo"]
    fecha_d = get_fecha_display(ob)

    if modo == "lunes":
        subject = f"🔁 Revisión semanal — {materia}"
        body    = (
            f"Revisión programada de lunes.\n\n"
            f"Materia: {materia}\n"
            f"Actividad: {titulo}\n"
            f"Nota: {ob.get('nota','')}\n\n"
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
            f"Tipo:       {ob.get('tipo','')}\n"
            f"Fecha:      {fecha_d}\n\n"
            f"Ver tablero completo: {pages_url}"
        )

    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        for dest in email_list:
            msg["To"] = dest
            server.sendmail(GMAIL_USER, dest, msg.as_string())
            print(f"Email → {dest} [{materia}]")

def run(modo="normal"):
    with open("data/obligaciones.json", encoding="utf-8") as f:
        data = json.load(f)

    meta       = data["meta"]
    canal      = meta["canal_slack"]
    emails     = meta["email_to"]
    pages_url  = meta["github_pages_url"]
    hoy        = date.today()

    for ob in data["obligaciones"]:

        # -- Revisión semanal lunes --
        if modo == "lunes" and ob.get("revision_semanal_lunes"):
            send_slack(ob, None, canal, pages_url, modo="lunes")
            send_email(ob, None, emails, pages_url, modo="lunes")
            continue

        # -- Alerta por días restantes --
        if modo == "normal" and ob.get("alerta") and ob.get("recordatorios_dias"):
            fecha_limite = get_fecha_limite(ob)
            if fecha_limite:
                dias = (fecha_limite - hoy).days
                if dias in ob["recordatorios_dias"]:
                    send_slack(ob, dias, canal, pages_url)
                    send_email(ob, dias, emails, pages_url)

if __name__ == "__main__":
    import sys
    modo = sys.argv[1] if len(sys.argv) > 1 else "normal"
    run(modo)
