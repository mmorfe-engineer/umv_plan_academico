#!/usr/bin/env python3
"""Genera el dashboard HTML para el Academic Tracker.

Lee data/obligaciones.json y genera docs/index.html con:
- Diseño Kanban por estados (Pendiente, En Progreso, Entregado)
- Tarjetas con emojis por tipo de actividad
- Badges de urgencia por dias restantes
- Barra de progreso general
- Diseño responsivo
- Paleta: fondo oscuro (#1a1a2e), acento teal (#01696f)
"""

import json
from datetime import datetime
import pytz

# =============================================================================
# Cargar datos
# =============================================================================

def load_data():
    """Carga y valida los datos de obligaciones."""
    try:
        with open("data/obligaciones.json", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validar estructura minima
        if "meta" not in data or "obligaciones" not in data:
            raise ValueError("Estructura JSON invalida: faltan 'meta' o 'obligaciones'")
        
        return data
    except FileNotFoundError:
        raise FileNotFoundError(
            "Archivo data/obligaciones.json no encontrado. "
            "Ejecutar desde el directorio raiz del proyecto."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON: {e}")


data = load_data()
meta = data["meta"]
obligaciones = data["obligaciones"]

# =============================================================================
# Configuracion timezone
# =============================================================================

tz = pytz.timezone(meta["timezone"])
now = datetime.now(tz)
formatted_now = now.strftime("%Y-%m-%d %H:%M:%S %Z")

# =============================================================================
# Constantes
# =============================================================================

# Emojis por tipo
EMOJI_TIPO = {
    "grupo c": "📝",
    "examen": "📝",
    "anteproyecto": "📐",
    "proyecto": "🚀",
    "programar": "💻",
    "trabajo en grupo": "👥",
    "flyer": "🎨",
}

# Estado emojis
ESTADO_EMOJI = {
    "pendiente": "⏳",
    "en_progreso": "🔄",
    "entregado": "✅",
}

# =============================================================================
# Funciones utilitarias
# =============================================================================

def get_fecha_limite(ob):
    """Obtiene la fecha limite como objeto date."""
    if "fecha" in ob:
        return datetime.strptime(ob["fecha"], "%Y-%m-%d").date()
    if "fecha_fin" in ob:
        return datetime.strptime(ob["fecha_fin"], "%Y-%m-%d").date()
    return None


def get_fecha_display(ob):
    """Obtiene el texto de fecha para mostrar."""
    if "fecha" in ob:
        return ob["fecha"]
    inicio = ob.get("fecha_inicio", "?")
    fin = ob.get("fecha_fin", "?")
    return f"{inicio} → {fin}"


def get_dias_restantes(ob):
    """Calcula dias restantes."""
    fecha_limite = get_fecha_limite(ob)
    if fecha_limite:
        hoy = datetime.now(tz).date()
        return (fecha_limite - hoy).days
    return None


def get_urgencia_class(dias, estado):
    """Determina la clase CSS de urgencia."""
    if estado == "entregado":
        return "badge-entregado"
    if dias is not None:
        if dias < 0:
            return "badge-vencido"
        elif dias <= 3:
            return "badge-urgente"
        elif dias <= 7:
            return "badge-proximo"
    return "badge-normal"


def get_urgencia_text(dias, estado):
    """Texto para mostrar en el badge de urgencia."""
    if estado == "entregado":
        return "Entregado"
    if dias is not None:
        if dias < 0:
            return "Vencido"
        elif dias == 0:
            return "Vence hoy"
        elif dias == 1:
            return "Vence manana"
        elif dias <= 7:
            return f"Vence en {dias} dias"
    return ""


# =============================================================================
# Agrupar obligaciones por estado
# =============================================================================

VALID_ESTADOS = ["pendiente", "en_progreso", "entregado"]
obligaciones_por_estado = {estado: [] for estado in VALID_ESTADOS}

for ob in obligaciones:
    estado = ob.get("estado", "pendiente")
    if estado not in VALID_ESTADOS:
        estado = "pendiente"
        print(f"⚠️  Estado invalido '{ob.get('estado')}' en {ob.get('materia')}, usando 'pendiente'")
    obligaciones_por_estado[estado].append(ob)

# =============================================================================
# Calcular progreso
# =============================================================================

total_obligaciones = len(obligaciones)
obligaciones_entregadas = len(obligaciones_por_estado["entregado"])
porcentaje_completado = (obligaciones_entregadas / total_obligaciones * 100) if total_obligaciones > 0 else 0

# =============================================================================
# Funcion para generar tarjeta HTML
# =============================================================================

def generate_card_html(ob):
    """Genera el HTML de una tarjeta de obligacion."""
    dias = get_dias_restantes(ob)
    urgencia_class = get_urgencia_class(dias, ob.get("estado", "pendiente"))
    urgencia_text = get_urgencia_text(dias, ob.get("estado", "pendiente"))
    emoji_tipo = EMOJI_TIPO.get(ob.get("tipo", "").lower(), "📌")
    tiene_lunes = ob.get("revision_semanal_lunes", False)
    estado = ob.get("estado", "pendiente")
    estado_emoji = ESTADO_EMOJI.get(estado, "⏳")
    materia = ob["materia"]
    actividad_id = ob["actividad_id"]
    titulo = ob["titulo"]
    seccion = ob.get("seccion", "")
    tipo = ob.get("tipo", "")
    fecha_display = get_fecha_display(ob)
    nota = ob.get("nota", "")

    lines = []
    lines.append('<div class="card">')
    lines.append('  <div class="card-header">')
    lines.append('    <span class="card-title">')
    
    if tiene_lunes:
        lines.append('      <span class="lunes-icon">🔁</span> ')
    
    lines.append(f'      {materia}')
    lines.append('    </span>')
    lines.append(f'    <span class="card-id">{actividad_id}</span>')
    lines.append('  </div>')
    lines.append('  <div class="card-body">')
    lines.append(f'    <span class="card-type">{emoji_tipo} {titulo}</span>')
    lines.append('  </div>')
    
    if seccion:
        lines.append(f'  <div class="card-section">{seccion}</div>')
    
    lines.append(f'  <div class="card-date">📅 {fecha_display}</div>')
    lines.append(f'  <div class="card-type">Tipo: {tipo}</div>')
    
    if urgencia_text:
        lines.append(f'  <div><span class="badge {urgencia_class}">{urgencia_text}</span></div>')
    
    if nota:
        lines.append(f'  <div class="card-nota">📝 {nota}</div>')
    
    # Badge de estado
    if estado == "entregado":
        lines.append(f'  <span class="badge badge-estado badge-entregado-badge">{estado_emoji} Entregado</span>')
    elif estado == "en_progreso":
        lines.append(f'  <span class="badge badge-estado badge-en_progreso">{estado_emoji} En Progreso</span>')
    else:
        lines.append(f'  <span class="badge badge-estado badge-pendiente">{estado_emoji} Pendiente</span>')
    
    lines.append('</div>')
    return '\n'.join(lines)


# =============================================================================
# CSS Estilos
# =============================================================================

CSS = """
:root {
    --bg-dark: #1a1a2e;
    --bg-darker: #16213e;
    --surface: #f8f9fa;
    --surface-dark: #e9ecef;
    --accent: #01696f;
    --accent-light: #01878c;
    --text-primary: #1a1a2e;
    --text-secondary: #6c757d;
    --border: #dee2e6;
    --shadow: rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-darker) 100%);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 30px;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--surface);
    margin-bottom: 10px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header .subtitle {
    font-size: 1.1rem;
    color: var(--surface-dark);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

.header .subtitle a {
    color: var(--accent-light);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}

.header .subtitle a:hover {
    color: var(--accent);
    text-decoration: underline;
}

.header .meta-info {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 10px;
}

/* Progress Bar */
.progress-container {
    background: var(--surface-dark);
    height: 30px;
    border-radius: 15px;
    overflow: hidden;
    margin: 20px 0 30px;
    box-shadow: 0 4px 6px var(--shadow);
}

.progress-bar {
    height: 100%;
    width: {porcentaje_completado}%;
    background: linear-gradient(90deg, var(--accent), var(--accent-light));
    border-radius: 15px;
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 0 15px;
    color: white;
    font-weight: 600;
    font-size: 0.9rem;
}

.progress-text {
    text-align: center;
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 10px;
}

/* Kanban Columns */
.kanban-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.kanban-column {
    background: var(--surface);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px var(--shadow);
    min-height: 200px;
}

.kanban-column h2 {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--border);
}

.kanban-column .count {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 400;
}

.kanban-column .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-secondary);
}

.kanban-column .empty-state em {
    font-style: italic;
}

/* Cards */
.card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px var(--shadow);
    border-left: 4px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
    gap: 10px;
}

.card-title {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1rem;
    flex: 1;
}

.card-id {
    font-size: 0.75rem;
    color: var(--text-secondary);
    background: var(--surface-dark);
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
}

.card-body {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 10px;
}

.card-type {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.card-date {
    font-size: 0.85rem;
    color: var(--accent);
    font-weight: 500;
    margin: 5px 0;
}

.card-section {
    font-size: 0.75rem;
    color: var(--text-secondary);
    background: var(--surface-dark);
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 8px;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-entregado {
    background: #d4edda;
    color: #155724;
}

.badge-vencido {
    background: #f8d7da;
    color: #721c24;
}

.badge-urgente {
    background: #fff3cd;
    color: #856404;
}

.badge-proximo {
    background: #fff3cd;
    color: #856404;
}

.badge-normal {
    background: #e2e3e5;
    color: #383d41;
}

.badge-estado {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-pendiente {
    background: #fff5f5;
    color: #dc3545;
}

.badge-en_progreso {
    background: #fffcf5;
    color: #fd7e14;
}

.badge-entregado-badge {
    background: #d4edda;
    color: #155724;
}

.card-nota {
    font-size: 0.8rem;
    color: #666;
    font-style: italic;
    margin-top: 8px;
    padding: 8px;
    background: #f8f9fa;
    border-radius: 4px;
    border-left: 2px solid var(--accent);
}

.lunes-icon {
    font-size: 1.2rem;
    margin-right: 5px;
}

/* Footer */
.footer {
    text-align: center;
    padding: 20px;
    color: var(--text-secondary);
    font-size: 0.85rem;
    border-top: 1px solid var(--border);
    margin-top: 30px;
}

.footer a {
    color: var(--accent-light);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .header h1 {
        font-size: 1.8rem;
    }
    .kanban-container {
        grid-template-columns: 1fr;
    }
    .card-header {
        flex-direction: column;
    }
    .card-id {
        align-self: flex-start;
    }
}

@media (max-width: 480px) {
    body {
        padding: 10px;
    }
    .header h1 {
        font-size: 1.5rem;
    }
    .header .subtitle {
        font-size: 0.95rem;
    }
    .kanban-column {
        padding: 15px;
    }
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--accent);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-light);
}
"""

# =============================================================================
# Generar HTML
# =============================================================================

def generate_column_html(title, icono, obligaciones_lista):
    """Genera el HTML de una columna Kanban."""
    lines = []
    count = len(obligaciones_lista)
    
    lines.append(f'<div class="kanban-column">')
    lines.append(f'  <h2>')
    lines.append(f'    <span>{icono}</span>')
    lines.append(f'    <span>{title}</span>')
    lines.append(f'    <span class="count">({count})</span>')
    lines.append(f'  </h2>')
    
    if not obligaciones_lista:
        lines.append(f'  <div class="empty-state"><em>No hay actividades {title.lower()}</em></div>')
    else:
        for ob in obligaciones_lista:
            lines.append(generate_card_html(ob))
    
    lines.append(f'</div>')
    return '\n'.join(lines)


# Construir HTML completo
html_lines = []

# Doctype y head
html_lines.append('<!DOCTYPE html>')
html_lines.append('<html lang="es">')
html_lines.append('<head>')
html_lines.append('  <meta charset="UTF-8">')
html_lines.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
html_lines.append(f'  <title>Plan Academico UVM - {meta["carrera"]} | {meta["periodo"]}</title>')
html_lines.append('  <link rel="preconnect" href="https://fonts.googleapis.com">')
html_lines.append('  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
html_lines.append('  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">')
html_lines.append('  <style>')

# Insertar CSS con indentacion
for css_line in CSS.strip().split('\n'):
    if css_line.strip():
        html_lines.append(f'    {css_line}')

html_lines.append('  </style>')
html_lines.append('</head>')
html_lines.append('<body>')
html_lines.append('  <div class="container">')

# Header
html_lines.append('    <!-- Header -->')
html_lines.append('    <header class="header">')
html_lines.append('      <h1>📚 Plan Academico UVM</h1>')
html_lines.append('      <div class="subtitle">')
html_lines.append(f'        <span><strong>{meta["carrera"]}</strong> | Periodo {meta["periodo"]}</span>')
html_lines.append('        <span>•</span>')
html_lines.append(f'        <span>Propietario: {meta["owner"]}</span>')
html_lines.append('      </div>')
html_lines.append('      <div class="subtitle">')
html_lines.append(f'        <a href="{meta["github_pages_url"]}" target="_blank">')
html_lines.append('          🌐 Ver Tablero Publico')
html_lines.append('        </a>')
html_lines.append('      </div>')
html_lines.append('      <div class="meta-info">')
html_lines.append(f'        Ultima actualizacion: {formatted_now}')
html_lines.append('      </div>')
html_lines.append('    </header>')

# Progress Bar
html_lines.append('    <!-- Progress Bar -->')
html_lines.append('    <div class="progress-text">')
html_lines.append(f'      Progreso general: {obligaciones_entregadas} de {total_obligaciones} actividades completadas')
html_lines.append('    </div>')
html_lines.append('    <div class="progress-container">')
html_lines.append(f'      <div class="progress-bar">{porcentaje_completado:.1f}%</div>')
html_lines.append('    </div>')

# Kanban Columns
html_lines.append('    <!-- Kanban Columns -->')
html_lines.append('    <div class="kanban-container">')

# Pendiente
html_lines.append(generate_column_html("Pendiente", ESTADO_EMOJI.get("pendiente"), obligaciones_por_estado["pendiente"]))

# En Progreso
html_lines.append(generate_column_html("En Progreso", ESTADO_EMOJI.get("en_progreso"), obligaciones_por_estado["en_progreso"]))

# Entregado
html_lines.append(generate_column_html("Entregado", ESTADO_EMOJI.get("entregado"), obligaciones_por_estado["entregado"]))

html_lines.append('    </div>')

# Footer
html_lines.append('    <!-- Footer -->')
html_lines.append('    <footer class="footer">')
html_lines.append('      <p>Generado automaticamente por <strong>Academic Tracker</strong></p>')
html_lines.append(f'      <p>Fecha de generacion: {formatted_now} (Timezone: {meta["timezone"]})</p>')
html_lines.append('    </footer>')
html_lines.append('  </div>')
html_lines.append('</body>')
html_lines.append('</html>')

# =============================================================================
# Escribir archivo
# =============================================================================

html_content = '\n'.join(html_lines)

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Dashboard generado en docs/index.html")
print(f"   Total actividades: {total_obligaciones}")
print(f"   Pendientes: {len(obligaciones_por_estado['pendiente'])}")
print(f"   En progreso: {len(obligaciones_por_estado['en_progreso'])}")
print(f"   Entregadas: {len(obligaciones_por_estado['entregado'])}")
print(f"   Progreso: {porcentaje_completado:.1f}%")
