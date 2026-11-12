#!/usr/bin/env python3
"""Genera el manual de uso de Epanimeitor en PDF (español, ReportLab)."""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable

# ──────────────────────────── Paths ────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/z/my-project"
LOGO_MAIN = f"{ROOT}/download/_logo_epanimeitor.png"
LOGO_INTRO = f"{ROOT}/download/_logo_intro.png"
OUTPUT = f"{ROOT}/download/Epanimeitor-Manual-de-Uso.pdf"

# ──────────────────────────── Palette (cascade, minimal) ────────────────────────────
PAGE_BG       = colors.HexColor('#f0f0ef')
SECTION_BG    = colors.HexColor('#f1f1f0')
CARD_BG       = colors.HexColor('#eeedea')
TABLE_STRIPE  = colors.HexColor('#f4f4f3')
HEADER_FILL   = colors.HexColor('#62583b')
COVER_BLOCK   = colors.HexColor('#897d5b')
BORDER        = colors.HexColor('#d1cec3')
ICON          = colors.HexColor('#7a6d48')
ACCENT        = colors.HexColor('#a5862a')
ACCENT_2      = colors.HexColor('#3ea6c9')
TEXT_PRIMARY  = colors.HexColor('#1a1a18')
TEXT_MUTED    = colors.HexColor('#7d7b73')

# ──────────────────────────── Fonts ────────────────────────────
# Use Noto Sans for body, Noto Serif for headings — clean Latin coverage for Spanish
FONT_BODY = "Helvetica"
FONT_BODY_BOLD = "Helvetica-Bold"
FONT_BODY_ITALIC = "Helvetica-Oblique"
FONT_HEAD = "Helvetica-Bold"
FONT_MONO = "Courier"

# Try to register Noto Sans if available (better looking than Helvetica)
NOTO_SANS_REG = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
NOTO_SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
NOTO_SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
if os.path.exists(NOTO_SANS_REG):
    pdfmetrics.registerFont(TTFont("NotoSans", NOTO_SANS_REG))
    if os.path.exists(NOTO_SANS_BOLD):
        pdfmetrics.registerFont(TTFont("NotoSans-Bold", NOTO_SANS_BOLD))
    FONT_BODY = "NotoSans"
    FONT_BODY_BOLD = "NotoSans-Bold" if os.path.exists(NOTO_SANS_BOLD) else "NotoSans"
    FONT_BODY_ITALIC = "NotoSans"
    FONT_HEAD = "NotoSans-Bold" if os.path.exists(NOTO_SANS_BOLD) else "NotoSans"
if os.path.exists(NOTO_SERIF_BOLD):
    pdfmetrics.registerFont(TTFont("NotoSerif-Bold", NOTO_SERIF_BOLD))
    FONT_HEAD = "NotoSerif-Bold"

# ──────────────────────────── Styles ────────────────────────────
styles = getSampleStyleSheet()

def s(name, **kw):
    base = dict(name=name, fontName=FONT_BODY, fontSize=10.5, leading=15,
                textColor=TEXT_PRIMARY, spaceBefore=0, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(**base)

style_title_cover = s("title_cover", fontName=FONT_HEAD, fontSize=32, leading=36,
                     textColor=colors.white, alignment=TA_CENTER, spaceAfter=12)
style_subtitle_cover = s("subtitle_cover", fontName=FONT_BODY, fontSize=14, leading=20,
                        textColor=colors.HexColor('#e6e2d3'), alignment=TA_CENTER, spaceAfter=0)
style_cover_meta = s("cover_meta", fontName=FONT_BODY, fontSize=10, leading=14,
                    textColor=colors.HexColor('#cfc9b3'), alignment=TA_CENTER)

style_h1 = s("h1", fontName=FONT_HEAD, fontSize=20, leading=26,
             textColor=HEADER_FILL, spaceBefore=20, spaceAfter=10)
style_h2 = s("h2", fontName=FONT_HEAD, fontSize=14, leading=20,
             textColor=HEADER_FILL, spaceBefore=14, spaceAfter=6)
style_h3 = s("h3", fontName=FONT_HEAD, fontSize=11.5, leading=16,
             textColor=ACCENT, spaceBefore=8, spaceAfter=4)
style_body = s("body", alignment=TA_JUSTIFY, spaceAfter=8)
style_bullet = s("bullet", leftIndent=14, spaceAfter=4)
style_intro = s("intro", fontSize=11, leading=17, textColor=TEXT_MUTED,
                alignment=TA_LEFT, spaceAfter=10, fontName=FONT_BODY_ITALIC)
style_caption = s("caption", fontSize=9, leading=12, textColor=TEXT_MUTED,
                 alignment=TA_CENTER, spaceAfter=6)
style_code = s("code", fontName=FONT_MONO, fontSize=9.5, leading=13,
              textColor=TEXT_PRIMARY, backColor=CARD_BG, borderPadding=6,
              leftIndent=4, rightIndent=4, spaceAfter=8)
style_table_header = s("th", fontName=FONT_BODY_BOLD, fontSize=10, leading=13,
                      textColor=colors.white, alignment=TA_LEFT)
style_table_cell = s("td", fontSize=9.5, leading=13, textColor=TEXT_PRIMARY,
                    alignment=TA_LEFT)
style_table_cell_mono = s("td_mono", fontName=FONT_MONO, fontSize=9, leading=12,
                         textColor=ACCENT, alignment=TA_LEFT)
style_callout = s("callout", fontSize=10.5, leading=15, textColor=TEXT_PRIMARY,
                 backColor=colors.HexColor('#fbf6e7'), borderColor=ACCENT,
                 borderWidth=0, borderPadding=8, leftIndent=0, rightIndent=0,
                 spaceAfter=10, fontName=FONT_BODY)

# ──────────────────────────── Helpers ────────────────────────────
def hr(color=BORDER, thickness=0.5, space_before=4, space_after=10):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                     spaceBefore=space_before, spaceAfter=space_after)

def section_heading(text):
    return Paragraph(text, style_h1)

def subheading(text):
    return Paragraph(text, style_h2)

def mini_heading(text):
    return Paragraph(text, style_h3)

def body(text):
    return Paragraph(text, style_body)

def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(it, style_bullet), leftIndent=14, value="•") for it in items],
        bulletType='bullet', bulletColor=ACCENT, leftIndent=14, spaceAfter=8,
    )

def callout(text):
    """Highlighted tip/info box."""
    return Paragraph(text, style_callout)

def kv_table(rows, col_widths=None):
    """Two-column key/value table."""
    if col_widths is None:
        col_widths = [4.5*cm, 11*cm]
    data = [[Paragraph(f"<b>{k}</b>", style_table_cell), Paragraph(v, style_table_cell)]
            for k, v in rows]
    t = Table(data, colWidths=col_widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_BG),
        ('TEXTCOLOR', (0,0), (0,-1), HEADER_FILL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-2), 0.25, BORDER),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def shortcuts_table(rows):
    """Three-column shortcuts table: combo, action, note."""
    col_widths = [4.5*cm, 5.5*cm, 5.5*cm]
    header = [
        Paragraph("Atajo", style_table_header),
        Paragraph("Acción", style_table_header),
        Paragraph("Notas", style_table_header),
    ]
    data = [header]
    for combo, action, note in rows:
        data.append([
            Paragraph(combo, style_table_cell_mono),
            Paragraph(action, style_table_cell),
            Paragraph(note, style_table_cell),
        ])
    t = Table(data, colWidths=col_widths, hAlign='LEFT', repeatRows=1)
    style = [
        ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,0), 0.5, HEADER_FILL),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(('BACKGROUND', (0,i), (-1,i), TABLE_STRIPE))
    t.setStyle(TableStyle(style))
    return t

def tools_table(rows):
    """Tool reference table: name, description, key."""
    col_widths = [3.5*cm, 8.5*cm, 3*cm]
    header = [
        Paragraph("Herramienta", style_table_header),
        Paragraph("Para qué sirve", style_table_header),
        Paragraph("Tecla", style_table_header),
    ]
    data = [header]
    for name, desc, key in rows:
        data.append([
            Paragraph(f"<b>{name}</b>", style_table_cell),
            Paragraph(desc, style_table_cell),
            Paragraph(key, style_table_cell_mono),
        ])
    t = Table(data, colWidths=col_widths, hAlign='LEFT', repeatRows=1)
    style = [
        ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(('BACKGROUND', (0,i), (-1,i), TABLE_STRIPE))
    t.setStyle(TableStyle(style))
    return t

# ──────────────────────────── Cover drawing on canvas ────────────────────────────
def draw_cover_background(canvas, page_w, page_h):
    """Draws full-bleed dark cover background with film-strip sprocket holes."""
    # Background block
    canvas.setFillColor(HEADER_FILL)
    canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    # Darker overlay strip top/bottom (film perforation vibe, evoking Epanimator logo)
    canvas.setFillColor(colors.HexColor('#3a3320'))
    strip_h = 18
    canvas.rect(0, page_h - strip_h, page_w, strip_h, fill=1, stroke=0)
    canvas.rect(0, 0, page_w, strip_h, fill=1, stroke=0)
    # White squares along top and bottom strips (sprocket holes)
    canvas.setFillColor(colors.HexColor('#e6e2d3'))
    sq = 8
    gap = 18
    x = gap
    y_top = page_h - strip_h + (strip_h - sq) / 2
    while x + sq <= page_w:
        canvas.rect(x, y_top, sq, sq, fill=1, stroke=0)
        x += gap + sq
    x = gap
    y_bot = (strip_h - sq) / 2
    while x + sq <= page_w:
        canvas.rect(x, y_bot, sq, sq, fill=1, stroke=0)
        x += gap + sq


def cover_page(story):
    """Build the cover content as flowables (background drawn in onFirstPage)."""
    page_w, page_h = A4
    # Spacer to push content down (cover bg is drawn by canvas)
    story.append(Spacer(1, 3.5 * cm))
    # Logo
    logo_w = 14 * cm
    logo = Image(LOGO_MAIN, width=logo_w, height=logo_w * 523 / 1600)
    story.append(Table([[logo]], colWidths=[page_w - 4*cm], style=[
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(Spacer(1, 1.2 * cm))
    # Title
    story.append(Paragraph("MANUAL DE USO", style_title_cover))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Animador de GIFs frame a frame · simple, colorido y gratuito",
        style_subtitle_cover
    ))
    story.append(Spacer(1, 2.5 * cm))
    # Intro logo (school badge)
    intro_w = 2.5 * cm
    intro_img = Image(LOGO_INTRO, width=intro_w, height=intro_w * 538 / 500)
    story.append(Table([[intro_img]], colWidths=[page_w - 4*cm], style=[
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Escuela para Animadores · Rosario",
        style_cover_meta
    ))

# ──────────────────────────── Page templates ────────────────────────────
def header_footer(canvas, doc):
    """Header + footer for body pages; cover background for page 1."""
    canvas.saveState()
    page_w, page_h = A4
    if doc.page == 1:
        # Draw cover background full-bleed
        draw_cover_background(canvas, page_w, page_h)
        canvas.restoreState()
        return
    # Top thin rule
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(2*cm, page_h - 1.5*cm, page_w - 2*cm, page_h - 1.5*cm)
    # Header text (left): small logo wordmark
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont(FONT_BODY, 8.5)
    canvas.drawString(2*cm, page_h - 1.25*cm, "Epanimeitor · Manual de uso")
    # Header right: section info (we just put app version)
    canvas.drawRightString(page_w - 2*cm, page_h - 1.25*cm, "v1.0")
    # Footer thin rule
    canvas.setStrokeColor(BORDER)
    canvas.line(2*cm, 1.3*cm, page_w - 2*cm, 1.3*cm)
    # Footer left: school
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont(FONT_BODY, 8.5)
    canvas.drawString(2*cm, 0.95*cm, "Escuela para Animadores · Rosario")
    # Footer right: page number
    canvas.drawRightString(page_w - 2*cm, 0.95*cm, f"Página {doc.page}")
    canvas.restoreState()

# ──────────────────────────── Build ────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Epanimeitor — Manual de Uso",
        author="Escuela para Animadores Rosario",
        subject="Manual de uso del animador de GIFs Epanimeitor",
        creator="Epanimeitor",
    )
    story = []
    # COVER
    cover_page(story)
    story.append(PageBreak())

    # ──────────── INTRO ────────────
    story.append(section_heading("1. Bienvenida"))
    story.append(Paragraph(
        "Epanimeitor es un animador de GIFs <b>frame a frame</b> que funciona "
        "directamente en el navegador. Está pensado para que cualquiera —desde "
        "niños en un aula hasta adultos creativos— pueda dibujar fotograma por "
        "fotograma, ver la animación al instante y descargarla como GIF sin "
        "instalar nada.",
        style_intro
    ))
    story.append(body(
        "Este manual te lleva por todas las funciones de la aplicación en menos "
        "de diez minutos de lectura. Si prefieres aprender tocando botones, "
        "avanza a la sección <b>Arranque rápido</b>; si quieres entender bien "
        "cada herramienta antes de empezar, sigue el orden del índice."
    ))
    story.append(callout(
        "<b>Idea clave:</b> una animación es una secuencia de imágenes estáticas "
        "que se muestran muy rápido. Epanimeitor hace sencillo lo difícil: dibujar "
        "cada imagen, organizarlas en orden y reproducirlas a la velocidad que elijas."
    ))
    story.append(hr())

    # ──────────── QUICK START ────────────
    story.append(section_heading("2. Arranque rápido"))
    story.append(body(
        "Estos cuatro pasos te llevan de cero a tu primer GIF en menos de dos minutos."
    ))
    story.append(mini_heading("Paso 1 — Elegí color y herramienta"))
    story.append(body(
        "En la barra de herramientas izquierda elegí <b>Lápiz</b> (o presioná la "
        "tecla <b>1</b>). En el panel de la derecha tocá un color de la paleta. "
        "El tamaño del pincel se ajusta con el deslizador."
    ))
    story.append(mini_heading("Paso 2 — Dibujá el primer fotograma"))
    story.append(body(
        "Hacé clic en el lienzo central y arrastrá el mouse para dibujar. Lo que "
        "veas ahora es el <b>fotograma 1</b> de tu animación."
    ))
    story.append(mini_heading("Paso 3 — Añadí más fotogramas"))
    story.append(body(
        "Pulsá el botón <b>Fotograma</b> (tecla <b>N</b>) para crear un nuevo "
        "fotograma vacío. Para no empezar de cero, usá <b>Duplicar</b> (tecla <b>D</b>): "
        "copia el fotograma actual para que solo tengas que mover un poco el dibujo y "
        "crear la ilusión de movimiento."
    ))
    story.append(mini_heading("Paso 4 — Reproducí y exportá"))
    story.append(body(
        "Pulsá <b>Reproducir</b> (o la barra espaciadora) para ver la animación en "
        "bucle. Cuando te guste, pulsá <b>GIF</b> y se descargará un archivo "
        "<i>epanimeitor-&lt;fecha&gt;.gif</i> listo para compartir."
    ))
    story.append(callout(
        "<b>Truco de animador:</b> activá <b>Onion skin</b> (tecla <b>O</b>) para "
        "ver el fotograma anterior dibujado en transparente debajo del actual. Así "
        "es mucho más fácil mantener la continuidad del movimiento."
    ))
    story.append(PageBreak())

    # ──────────── TOOLS ────────────
    story.append(section_heading("3. Herramientas de dibujo"))
    story.append(body(
        "La barra lateral izquierda contiene siete herramientas, cada una con su "
        "atajo de teclado (1 a 7). El botón activo se destaca con un degradado de "
        "color. Debajo de las herramientas están los botones de <b>Deshacer</b> y "
        "<b>Rehacer</b>, que conservan hasta treinta pasos de historial."
    ))
    story.append(tools_table([
        ("Lápiz", "Trazo fino para detalles y bocetos. Pulsá y arrastrá para dibujar líneas continuas.", "1"),
        ("Pincel", "Trazo más grueso y suave, ideal para rellenar áreas grandes.", "2"),
        ("Borrador", "Borra con el tamaño actual del pincel. No borra el fondo, solo el dibujo.", "3"),
        ("Línea", "Dibuja una línea recta entre el punto inicial y el final. Útil para bordes definidos.", "4"),
        ("Rectángulo", "Dibuja el contorno de un rectángulo arrastrando el mouse.", "5"),
        ("Círculo", "Dibuja el contorno de una elipse arrastrando el mouse.", "6"),
        ("Relleno", "Flood fill: rellena un área cerrada con el color actual. Hacé clic dentro del área.", "7"),
    ]))
    story.append(Spacer(1, 6))
    story.append(mini_heading("Tamaño de pincel"))
    story.append(body(
        "El deslizador del panel derecho ajusta el grosor del trazo entre 1 y 50 "
        "píxeles. El círculo de vista previa muestra el tamaño real. El lápiz usa "
        "automáticamente un trazo más fino (60 % del tamaño seleccionado) para "
        "mantener el detalle."
    ))
    story.append(mini_heading("Colores"))
    story.append(body(
        "La paleta principal tiene 16 colores vibrantes elegidos para que las "
        "animaciones se vean alegres. Si necesitás un tono exacto, pulsá "
        "<b>Color personalizado</b> para abrir el selector con ruleta y campo "
        "hexadecimal. El color actual se muestra con su código HEX debajo."
    ))
    story.append(mini_heading("Fondo"))
    story.append(body(
        "El color de fondo se aplica a todos los fotogramas a la vez y se puede "
        "cambiar en cualquier momento sin perder el dibujo. Hay nueve fondos "
        "predefinidos (blanco, crema, celeste, rosa, verde, etc.) y un selector "
        "para elegir cualquier color."
    ))
    story.append(PageBreak())

    # ──────────── FRAMES & TIMELINE ────────────
    story.append(section_heading("4. Fotogramas y línea de tiempo"))
    story.append(body(
        "La línea de tiempo aparece debajo del lienzo y muestra todos los "
        "fotogramas como miniaturas en orden. El fotograma activo se marca con un "
        "borde rosa y un número en la esquina. Hacé clic en cualquier miniatura "
        "para editar ese fotograma."
    ))
    story.append(mini_heading("Operaciones con fotogramas"))
    story.append(kv_table([
        ("Fotograma nuevo", "Crea un fotograma vacío después del actual y pasa a editarlo."),
        ("Duplicar", "Copia el fotograma actual. Es la forma más rápida de animar: duplicás y movés un poco."),
        ("Borrar", "Elimina el fotograma actual. Se necesita al menos uno, por eso se desactiva cuando solo queda uno."),
        ("Limpiar", "Borra todo el dibujo del fotograma actual pero conserva el fotograma."),
        ("Reordenar", "Las flechas arriba/abajo mueven el fotograma una posición a la izquierda o derecha."),
        ("Marcar como 1º", "Mueve el fotograma actual al inicio de la animación."),
    ]))
    story.append(Spacer(1, 6))
    story.append(mini_heading("Onion skin"))
    story.append(body(
        "Cuando activás onion skin (interruptor en el panel derecho o tecla <b>O</b>), "
        "el fotograma anterior aparece dibujado en el lienzo al 30 % de opacidad. "
        "Es una técnica clásica de animación tradicional: permite ver el dibujo "
        "previo como referencia y dibujar el siguiente con precisión."
    ))
    story.append(callout(
        "<b>Flujo recomendado:</b> 1) Dibujá el primer fotograma. 2) Activá onion "
        "skin. 3) Duplicá el fotograma con <b>D</b>. 4) Ajustá el dibujo moviendo "
        "lo que quieras animar. 5) Repetí desde el paso 3."
    ))
    story.append(PageBreak())

    # ──────────── PLAYBACK ────────────
    story.append(section_heading("5. Reproducción"))
    story.append(body(
        "La barra de reproducción está entre el lienzo y la línea de tiempo. "
        "Desde allí podés navegar fotograma por fotograma o ver la animación "
        "completa en bucle."
    ))
    story.append(kv_table([
        ("Reproducir / Pausar", "Inicia o detiene la animación en bucle. Botón central o barra espaciadora."),
        ("Fotograma anterior", "Salta al fotograma anterior sin reproducir. Tecla J."),
        ("Fotograma siguiente", "Salta al fotograma siguiente sin reproducir. Tecla K."),
        ("FPS", "Fotogramas por segundo. Va de 1 (muy lento) a 24 (cine). 8–12 fps es un buen punto de partida."),
        ("Indicador", "Muestra \"Fotograma X de N\" para saber siempre dónde estás parado."),
    ]))
    story.append(Spacer(1, 6))
    story.append(body(
        "La velocidad de reproducción se ajusta con el deslizador de FPS. Cada "
        "fotograma se muestra durante 1000 ÷ FPS milisegundos. A 8 fps, cada "
        "fotograma dura 125 ms; a 12 fps, unos 83 ms."
    ))
    story.append(mini_heading("Cuántos fotogramas usar"))
    story.append(bullet_list([
        "Bucle corto de logo o icono: 4–8 fotogramas a 8 fps.",
        "Animación de personaje caminando: 6–10 fotogramas a 12 fps.",
        "Transición suave de objeto: 10–20 fotogramas a 15 fps.",
        "Animación narrativa con varios segundos: 20–60 fotogramas a 12–15 fps.",
    ]))

    # ──────────── EXPORT & SAVE ────────────
    story.append(section_heading("6. Guardar, cargar y exportar"))
    story.append(body(
        "La barra superior tiene cuatro botones para gestionar tus archivos."
    ))
    story.append(kv_table([
        ("Nuevo", "Empieza una animación desde cero. Pide confirmación si hay cambios sin guardar."),
        ("Guardar", "Descarga un archivo <b>epanimeitor.json</b> con todos los fotogramas, el color de fondo, los FPS y el estado de onion skin. Usalo para seguir trabajando después."),
        ("Cargar", "Abre un archivo .json previamente guardado y restaura toda la animación."),
        ("GIF", "Genera y descarga un GIF animado con la paleta optimizada para cada fotograma. El archivo se llama <b>epanimeitor-&lt;timestamp&gt;.gif</b>."),
    ]))
    story.append(Spacer(1, 6))
    story.append(callout(
        "<b>Diferencia entre Guardar y GIF:</b> <i>Guardar</i> crea un proyecto "
        "editable (se puede volver a abrir y seguir dibujando). <i>GIF</i> crea "
        "la versión final para compartir en redes, mensajería o web. No se puede "
        "editar."
    ))
    story.append(PageBreak())

    # ──────────── SHORTCUTS ────────────
    story.append(section_heading("7. Atajos de teclado"))
    story.append(body(
        "Epanimeitor está pensado para usarse casi sin tocar el mouse. Memorizá "
        "estos atajos y vas a animar mucho más rápido."
    ))
    story.append(subheading("Reproducción y fotogramas"))
    story.append(shortcuts_table([
        ("Espacio", "Reproducir / pausar", "Solo funciona con 2 o más fotogramas"),
        ("N", "Fotograma nuevo", "Vacío, después del actual"),
        ("D", "Duplicar fotograma", "Copia el actual con su dibujo"),
        ("J", "Fotograma anterior", "Salta sin reproducir"),
        ("K", "Fotograma siguiente", "Salta sin reproducir"),
        ("O", "Activar / desactivar onion skin", "Ver fotograma previo en transparente"),
        ("Shift + Supr", "Borrar fotograma actual", "Solo si hay más de uno"),
    ]))
    story.append(Spacer(1, 10))
    story.append(subheading("Herramientas"))
    story.append(shortcuts_table([
        ("1", "Lápiz", "Trazo fino"),
        ("2", "Pincel", "Trazo grueso"),
        ("3", "Borrador", "Borra dibujo"),
        ("4", "Línea", "Recta entre dos puntos"),
        ("5", "Rectángulo", "Contorno rectangular"),
        ("6", "Círculo", "Elipse"),
        ("7", "Relleno", "Flood fill"),
    ]))
    story.append(Spacer(1, 10))
    story.append(subheading("Archivo y edición"))
    story.append(shortcuts_table([
        ("Ctrl / Cmd + Z", "Deshacer", "Hasta 30 pasos"),
        ("Ctrl / Cmd + Shift + Z", "Rehacer", "También Ctrl / Cmd + Y"),
        ("Ctrl / Cmd + S", "Guardar proyecto", "Descarga .json"),
        ("Ctrl / Cmd + E", "Exportar GIF", "Descarga .gif"),
        ("Ctrl / Cmd + O", "Cargar proyecto", "Abre .json"),
    ]))

    # ──────────── TIPS & FAQ (flow, no forced page break) ────────────
    story.append(section_heading("8. Consejos y problemas frecuentes"))
    story.append(subheading("Mi GIF se ve pixelado"))
    story.append(body(
        "El formato GIF solo permite 256 colores por fotograma. Epanimeitor "
        "optimiza la paleta en cada uno, pero si tu animación tiene muchos "
        "colores muy distintos, algunos se aproximan al más cercano. Para mejores "
        "resultados, trabajá con una paleta limitada (4–8 colores principales)."
    ))
    story.append(subheading("La animación se ve a tirones"))
    story.append(body(
        "Subí los FPS en la barra de reproducción. Si tenés pocos fotogramas, "
        "agregá más con <b>Duplicar</b> y ajustá pequeños movimientos. Una buena "
        "regla: cada fotograma debería cambiar solo un poco respecto al anterior."
    ))
    story.append(subheading("Borré algo por accidente"))
    story.append(body(
        "Pulsá <b>Ctrl / Cmd + Z</b> para deshacer. Epanimeitor guarda hasta 30 "
        "pasos de historial por sesión. Si ya guardaste el proyecto después del "
        "error, vas a tener que dibujar de nuevo esa parte."
    ))
    story.append(subheading("Quiero seguir trabajando mañana"))
    story.append(body(
        "Pulsá <b>Guardar</b> y se descarga un archivo .json. Guardalo en una "
        "carpeta que recuerdes. Para reabrirlo, pulsá <b>Cargar</b> y seleccioná "
        "el archivo. La animación vuelve exactamente como la dejaste, incluidos "
        "fondo y FPS."
    ))
    story.append(subheading("Trucos para que tus animaciones se vean profesionales"))
    story.append(bullet_list([
        "Usá onion skin siempre. Es la diferencia entre movimiento fluido y entrecortado.",
        "Dibujá primero los puntos clave (extremos del movimiento) y luego los intermedios.",
        "Mantené una paleta de colores coherente en todos los fotogramas.",
        "Aprovechá <b>Duplicar</b>: copia el fotograma anterior y solo cambia lo que se mueve.",
        "Probá con fondos de color para que el dibujo destaque más.",
        "Si tu animación va a ser un bucle, aseguráte de que el último fotograma conecte con el primero.",
    ]))
    story.append(Spacer(1, 14))
    story.append(hr(color=ACCENT, thickness=1, space_before=6, space_after=10))
    story.append(Paragraph(
        "Epanimeitor es una herramienta gratuita de la <b>Escuela para Animadores "
        "Rosario</b>. Hecho con cariño para que cualquiera pueda contar historias "
        "en movimiento.",
        s("closing", alignment=TA_CENTER, fontSize=10, leading=14,
         textColor=TEXT_MUTED, fontName=FONT_BODY_ITALIC)
    ))

    # Build
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"PDF generated: {OUTPUT}")
    print(f"Size: {os.path.getsize(OUTPUT)/1024:.1f} KB")


if __name__ == "__main__":
    build()
