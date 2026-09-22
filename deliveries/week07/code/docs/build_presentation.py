"""Genera PresentationWeek07.pptx (y el PDF si PowerPoint esta disponible).

Mantiene la linea visual de Week 5: indigo dominante, serif en titulos, etiqueta
en versalitas sobre cada titulo. Las cifras salen de data/processed/.

    python code/docs/build_presentation.py
"""
import re
import sys
from pathlib import Path

import pandas as pd
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

WEEK07 = Path(__file__).resolve().parents[2]
PROCESSED = WEEK07 / "data" / "processed"
OUTPUT = WEEK07 / "PresentationWeek07.pptx"

INDIGO = RGBColor(0x2A, 0x3D, 0x9B)
INDIGO_DARK = RGBColor(0x1C, 0x29, 0x6B)
LAVENDER = RGBColor(0x9D, 0xAC, 0xF8)
LAVENDER_SOFT = RGBColor(0xEC, 0xEF, 0xFD)
ORANGE = RGBColor(0xEB, 0x68, 0x34)
INK = RGBColor(0x1B, 0x1B, 0x1A)
INK_2 = RGBColor(0x55, 0x54, 0x4F)
MUTED = RGBColor(0x8A, 0x89, 0x83)
BG = RGBColor(0xF9, 0xFA, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xDC, 0xDB, 0xD4)
TITLE_FONT, BODY_FONT = "Cambria", "Calibri"
W, H = 13.333, 7.5


def fmt(value, decimals=0):
    text = f"{value:,.{decimals}f}".replace(",", " ")
    return text.replace(".", ",") if decimals else text


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(W), Inches(H)
        self.blank = self.prs.slide_layouts[6]
        self.count = 0

    def slide(self, kicker=None, title=None, dark=False, notes=""):
        slide = self.prs.slides.add_slide(self.blank)
        self.count += 1
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = INDIGO if dark else BG
        if kicker:
            self.text(slide, kicker.upper(), 0.6, 0.42, 9, 0.35, size=12, bold=True,
                      color=LAVENDER if dark else MUTED, spacing=250)
        if title:
            self.text(slide, title, 0.6, 0.72, 12.1, 0.9, size=30, bold=True, font=TITLE_FONT,
                      color=WHITE if dark else INK)
        if not dark:
            self.text(slide, "InmoScore · Delivery 1", 0.6, 7.05, 4, 0.3, size=10, color=INDIGO)
            self.text(slide, str(self.count), 12.2, 7.05, 0.5, 0.3, size=10, color=INDIGO, align=PP_ALIGN.RIGHT)
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
        return slide

    @staticmethod
    def text(slide, content, x, y, w, h, size=16, bold=False, color=INK, font=BODY_FONT, align=PP_ALIGN.LEFT,
             italic=False, spacing=0, anchor=MSO_ANCHOR.TOP):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        frame = box.text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        frame.vertical_anchor = anchor
        lines = content if isinstance(content, list) else [content]
        for index, line in enumerate(lines):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.alignment = align
            runs = line if isinstance(line, list) else [(line, bold)]
            for piece, piece_bold in runs:
                run = paragraph.add_run()
                run.text = piece
                run.font.size, run.font.bold, run.font.italic = Pt(size), piece_bold, italic
                run.font.name, run.font.color.rgb = font, color
                if spacing:
                    run.font._element.set("spc", str(spacing))
        return box

    @staticmethod
    def bullets(slide, items, x, y, w, h, size=16, color=INK, gap=6):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        frame = box.text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        for index, item in enumerate(items):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.space_after = Pt(gap)
            runs = item if isinstance(item, list) else [(item, False)]
            first = paragraph.add_run()
            first.text = "•  "
            first.font.size, first.font.color.rgb, first.font.name = Pt(size), INDIGO, BODY_FONT
            for piece, bold in runs:
                run = paragraph.add_run()
                run.text = piece
                run.font.size, run.font.bold, run.font.name, run.font.color.rgb = Pt(size), bold, BODY_FONT, color
        return box

    @staticmethod
    def card(slide, x, y, w, h, fill=WHITE, line=LINE):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        shape.adjustments[0] = 0.06
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
        if line is None:
            shape.line.fill.background()
        else:
            shape.line.color.rgb = line
            shape.line.width = Pt(1)
        shape.shadow.inherit = False
        return shape

    def stat(self, slide, value, label, x, y, w, color=INDIGO, size=40):
        self.text(slide, value, x, y, w, 0.8, size=size, bold=True, color=color, font=TITLE_FONT)
        self.text(slide, label, x, y + 0.85, w, 0.9, size=13, color=INK_2)

    @staticmethod
    def image(slide, path, x, y, max_w, max_h, align="center"):
        width, height = Image.open(path).size
        scale = min(max_w / width, max_h / height)
        w, h = width * scale, height * scale
        left = x + (max_w - w) / 2 if align == "center" else x
        top = y + (max_h - h) / 2
        return slide.shapes.add_picture(str(path), Inches(left), Inches(top), Inches(w), Inches(h))

    def table(self, slide, rows, x, y, widths, row_h=0.36, size=12, highlight=None):
        shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                                       Inches(sum(widths)), Inches(row_h * len(rows)))
        table = shape.table
        for index, width in enumerate(widths):
            table.columns[index].width = Inches(width)
        for r, row in enumerate(rows):
            table.rows[r].height = Inches(row_h)
            for c, value in enumerate(row):
                cell = table.cell(r, c)
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.margin_top = cell.margin_bottom = Inches(0.03)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.fill.solid()
                header, marked = r == 0, highlight is not None and r == highlight
                cell.fill.fore_color.rgb = INDIGO if header else (LAVENDER_SOFT if marked else WHITE)
                paragraph = cell.text_frame.paragraphs[0]
                paragraph.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.RIGHT if str(value)[:1].isdigit() or str(value)[:1] in "−+-" else PP_ALIGN.LEFT
                run = paragraph.add_run()
                run.text = str(value)
                run.font.size, run.font.name = Pt(size), BODY_FONT
                run.font.bold = header or marked
                run.font.color.rgb = WHITE if header else INK
        return table


def requirement_status():
    """Cuenta los estados de RF y RNF directamente de Requirements.md."""
    counts = {"RF": {}, "RNF": {}}
    for line in (WEEK07 / "Requirements.md").read_text(encoding="utf-8").splitlines():
        for kind in counts:
            if re.match(rf"^\| {kind}-\d{{2}} \|", line):
                status = next((mark for mark in ["✅", "🟡", "⬜", "❌"] if mark in line), None)
                counts[kind][status] = counts[kind].get(status, 0) + 1
    return counts


def load():
    models = pd.read_csv(PROCESSED / "model_comparison.csv").set_index("model")
    checks = pd.read_csv(PROCESSED / "recommendation_checks.csv")
    geo = pd.read_csv(PROCESSED / "geocoding_summary.csv").set_index("district")
    calibration = pd.read_csv(PROCESSED / "alcabala_calibration.csv").set_index("district")
    return models, checks, geo, calibration


def build():
    models, checks, geo, calibration = load()
    base, best = models.loc["A_mediana_distrital"], models.loc[models.seleccionado].iloc[0]
    geo_total = geo.loc["TOTAL"]
    deck = Deck()
    figures, design = WEEK07 / "figures", WEEK07 / "design"

    # 1 portada
    s = deck.slide(dark=True, notes="Presentamos Delivery 1 de InmoScore: la definición integrada del producto al cierre de la primera fase.")
    deck.text(s, "DELIVERY 1 · DS3022 DESARROLLO DE PRODUCTO DE DATOS", 0.8, 1.5, 11, 0.4, size=13, bold=True, color=LAVENDER, spacing=250)
    deck.text(s, "InmoScore", 0.8, 2.0, 11, 1.4, size=72, bold=True, color=WHITE, font=TITLE_FONT)
    deck.text(s, "Cuánto vale de verdad cada aviso, y cuáles convienen a tu perfil, con la razón a la vista.",
              0.8, 3.45, 10.5, 1.0, size=22, italic=True, color=LAVENDER_SOFT)
    deck.text(s, [[("Denzel ", True), ("Cloud & DevOps   ·   ", False), ("Jyns ", True), ("Machine Learning   ·   ", False),
                   ("Lisseth ", True), ("Data Analyst   ·   ", False), ("Mafer ", True), ("Full-Stack & UX/UI", False)]],
              0.8, 5.3, 11.5, 0.4, size=15, color=WHITE)
    deck.text(s, "UTEC · Prof. Germain Garcia-Zanabria · 23 de setiembre de 2026 · github.com/Jyns123/DPD",
              0.8, 5.8, 11.5, 0.4, size=13, color=LAVENDER)

    # 2 problema
    s = deck.slide("Problema revisado", "Comprar vivienda con información incompleta",
                   notes="Las tres preguntas siguen siendo las de Week 5, pero ahora cuantificadas con nuestros datos.")
    deck.bullets(s, [[("¿El precio es razonable? ", True), ("Los portales muestran precio y fotos, no un valor de referencia.", False)],
                     [("¿Cómo es el entorno? ", True), ("Seguridad, colegios y transporte no están en el aviso.", False)],
                     [("¿Quién construye? ", True), ("En planos, se paga por adelantado sin historial del promotor.", False)]],
                 0.6, 1.75, 6.2, 2.6, size=17, gap=12)
    deck.card(s, 7.3, 1.75, 5.4, 4.8, fill=WHITE)
    deck.stat(s, "3,4×", "variación del precio por m² entre distritos (S/ 2 773 a S/ 9 299)", 7.6, 1.95, 4.9)
    deck.stat(s, "15 %", "error mediano de usar la mediana del distrito como precio de referencia", 7.6, 3.45, 4.9)
    deck.stat(s, "+9–14 %", "precio pedido sobre el de cierre (Alcabala) en los distritos comparables", 7.6, 4.95, 4.9, color=ORANGE)
    deck.text(s, "Enunciado: el comprador no tiene una forma accesible de saber si el precio de un aviso es razonable para "
                 "sus características y su zona, ni de comparar avisos según sus propias prioridades.",
              0.6, 4.75, 6.3, 1.6, size=15, italic=True, color=INK_2)

    # 3 usuarios
    s = deck.slide("Usuarios", "Dos compradores, dos rankings",
                   notes="María y Carlos son los perfiles de los storyboards de Week 5. En ambos casos lo que limita el precio es la cuota del crédito, no el presupuesto declarado.")
    for index, (name, who, finance, weights, cap) in enumerate([
        ("María", "Familia con una hija en edad escolar · ≥ 3 dormitorios", "Ingreso S/ 15 000 · ahorro S/ 150 000 · presupuesto S/ 700 000",
         "Precio 20 · Seguridad 40 · Colegios 30 · Constructora 10", "S/ 662 959"),
        ("Carlos", "Primer comprador, prioriza el precio · ≥ 2 dormitorios", "Ingreso S/ 9 000 · ahorro S/ 60 000 · presupuesto S/ 400 000",
         "Precio 60 · Seguridad 15 · Colegios 20 · Constructora 5", "S/ 367 775")]):
        x = 0.6 + index * 6.2
        deck.card(s, x, 1.75, 5.9, 3.9)
        deck.text(s, name, x + 0.35, 1.95, 5, 0.6, size=26, bold=True, font=TITLE_FONT, color=INDIGO)
        deck.text(s, who, x + 0.35, 2.6, 5.3, 0.4, size=14, color=INK_2)
        deck.text(s, finance, x + 0.35, 3.15, 5.3, 0.4, size=14)
        deck.text(s, weights, x + 0.35, 3.6, 5.3, 0.4, size=14, bold=True)
        deck.text(s, "Precio máximo alcanzable", x + 0.35, 4.3, 5, 0.3, size=12, color=MUTED)
        deck.text(s, cap, x + 0.35, 4.6, 5, 0.7, size=30, bold=True, font=TITLE_FONT, color=ORANGE)
    deck.text(s, "Precio máximo = mínimo entre el presupuesto, el ahorro / 10 % de inicial y el crédito con cuota ≤ 30 % del ingreso "
                 "(TEA 9 %, 20 años) más el ahorro. En ambos perfiles manda la cuota.",
              0.6, 5.95, 12.1, 0.8, size=14, color=INK_2)

    # 4 canvas
    s = deck.slide("Data Product Canvas", "Canvas final de la primera fase",
                   notes="Cambiaron cuatro cajas respecto a Week 5: la data nueva que creamos, el estado de la solución, las métricas ya medidas y las acciones hacia Week 15.")
    deck.image(s, WEEK07 / "DataProductCanvas.png", 0.6, 1.6, 12.1, 5.3)

    # 5 datos
    s = deck.slide("Datos", "Ocho fuentes públicas en un solo feature store",
                   notes="Todas las fuentes son públicas. El manifiesto registra hash y fecha de cada archivo. Corregimos un error de Week 6 en el join del BCRP.")
    sources = [("Urbania", "3 987 avisos"), ("SAT · Alcabala", "24 148 compraventas"), ("BCRP", "957 observaciones"),
               ("SIDPOL", "29 833 registros"), ("OpenStreetMap", "16 987 POIs"), ("INEI", "51 distritos"),
               ("Fondo MIVIVIENDA", "747 proyectos"), ("Nominatim", "200 avisos geocodificados")]
    for index, (name, volume) in enumerate(sources):
        x, y = 0.6 + (index % 4) * 3.05, 1.75 + (index // 4) * 1.3
        deck.card(s, x, y, 2.85, 1.1, fill=LAVENDER_SOFT, line=None)
        deck.text(s, name, x + 0.2, y + 0.15, 2.5, 0.4, size=16, bold=True, color=INDIGO)
        deck.text(s, volume, x + 0.2, y + 0.58, 2.5, 0.4, size=14, color=INK_2)
    deck.bullets(s, [[("Filtro IQR por distrito: ", True), ("3 987 → 3 896 avisos en 20 distritos.", False)],
                     [("Sin imputación: ", True), ("data_partial marca 984 avisos (25,3 %) fuera de la cobertura del BCRP.", False)],
                     [("Corrección de Week 6: ", True), ("el ratio precio/alquiler quedaba vacío por un join sin normalizar; data_partial salía en 100 %.", False)],
                     [("Trazabilidad: ", True), ("manifiesto SHA-256 por archivo y diccionario de 315 columnas generado desde los datos.", False)]],
                 0.6, 4.55, 12.1, 2.3, size=15)

    # 6 EDA
    s = deck.slide("Análisis exploratorio", "El área explica el precio; el distrito, el precio por m²",
                   notes="Precio y área tienen cola larga, por eso modelamos en logaritmos. Dentro de un distrito la dispersión sigue siendo grande: la mediana distrital no basta.")
    deck.image(s, figures / "fig_eda_distribuciones.png", 0.5, 1.65, 7.6, 2.8)
    deck.image(s, figures / "fig_eda_precio_m2_distrito.png", 8.3, 1.55, 4.5, 5.35)
    deck.bullets(s, [[("ρ(precio, área) = 0,74; ", True), ("ρ(precio/m², área) = −0,21: el m² de los inmuebles grandes cuesta menos.", False)],
                     [("Asimetría: ", True), ("precio 4,8, área 2,9, precio por m² 0,4 → modelar en logaritmos.", False)],
                     [("Dispersión dentro del distrito: ", True), ("en Chorrillos la mitad central va de −21 % a +29 % de la mediana.", False)]],
                 0.6, 4.7, 7.4, 2.2, size=15)

    # 7 paradoja de seguridad
    s = deck.slide("Hallazgo", "Los distritos más caros tienen más denuncias por residente",
                   notes="No es que la inseguridad suba el precio: las denuncias ocurren donde hay comercio y población flotante, y se dividen entre residentes. Es un sesgo de medición que el producto debe declarar.")
    deck.image(s, figures / "fig_eda_entorno_vs_precio.png", 0.5, 1.6, 8.2, 3.9)
    deck.card(s, 9.0, 1.75, 3.7, 4.6, fill=WHITE)
    deck.stat(s, "ρ = −0,41", "seguridad vs precio por m² en 20 distritos", 9.3, 1.95, 3.2)
    deck.stat(s, "ρ = +0,50", "conveniencia urbana vs precio por m²", 9.3, 3.5, 3.2)
    deck.text(s, "Acción: probar normalización por superficie y por modalidad de denuncia en Week 11.", 9.3, 5.05, 3.2, 1.2, size=13, color=INK_2)
    deck.text(s, "Miraflores, Barranco y San Isidro concentran comercio y turismo: las denuncias se dividen entre pocos residentes.",
              0.6, 5.8, 8.2, 0.8, size=14, italic=True, color=INK_2)

    # 8 Alcabala
    homogeneous = calibration.loc[["SAN MARTIN DE PORRES", "SAN JUAN DE LURIGANCHO", "LA MOLINA", "LOS OLIVOS", "COMAS"],
                                  "brecha_oferta_vs_vivienda"]
    s = deck.slide("Precios de cierre", "Alcabala: cuánto se paga de verdad",
                   notes="El dataset del SAT no trae área ni tipo de predio, y las cocheras se venden como predios aparte. La fórmula (1 + f) / 2 es un criterio que no depende de Urbania, así que sirve para contrastarla.")
    deck.image(s, figures / "fig_alcabala_oferta_vs_cierre.png", 0.5, 1.55, 6.6, 5.35)
    deck.bullets(s, [[("24 148 compraventas ", True), ("al 100 % en 44 distritos (ene–jun 2026).", False)],
                     [("Problema: ", True), ("64 % de las operaciones de San Isidro son cocheras o depósitos (< S/ 80 000).", False)],
                     [("Criterio: ", True), ("la mediana de vivienda está en el percentil (1 + f) / 2 = mediana de las operaciones ≥ S/ 80 000.", False)],
                     [("Resultado: ", True), (f"la oferta supera al cierre en +{homogeneous.min():.0%} a +{homogeneous.max():.0%} donde la composición es comparable.".replace("%", " %"), False)],
                     [("En distritos caros ", True), ("la brecha (+50–72 %) mide composición, no negociación.", False)]],
                 7.4, 1.75, 5.3, 5.0, size=15, gap=10)

    # 9 motor de valoracion
    s = deck.slide("Motor de valoración", "Gradient boosting: −17 % de error frente a la línea base",
                   notes="Validación rotada de 5 pliegues estratificada por distrito y precio. La regla de aceptación es la de Week 6: bajar el MAE sin empeorar los distritos chicos.")
    names = {"A_mediana_distrital": "A · Mediana distrital × área", "B_loglineal_distrito": "B · Log-lineal área + distrito",
             "C1_ridge_week06": "C1 · Ridge de Week 6", "C2_ridge_v2": "C2 · Ridge v2 (log-área)",
             "D_gradient_boosting": "D · Gradient boosting"}
    rows = [["Modelo", "MAE (S/)", "MdAPE", "Error ≤ 10 %", "ΔMAE vs A"]]
    order = list(names)
    for name in order:
        row = models.loc[name]
        rows.append([names[name], fmt(row.mae_soles), f"{row.mdape:.1%}".replace(".", ",").replace("%", " %"),
                     f"{row.pct_within_10:.1%}".replace(".", ",").replace("%", " %"),
                     "—" if name == "A_mediana_distrital" else f"{row.delta_mae_vs_A:+.1%}".replace(".", ",").replace("-", "−").replace("%", " %")])
    deck.table(s, rows, 0.6, 1.8, [3.6, 1.6, 1.3, 1.5, 1.5], row_h=0.5, size=14, highlight=order.index(best.name) + 1)
    deck.card(s, 10.4, 1.8, 2.3, 3.0, fill=WHITE)
    deck.stat(s, fmt(best.mdape * 100, 1) + " %", "MdAPE del modelo (línea base 15,2 %)", 10.6, 1.95, 2.0, color=ORANGE, size=34)
    deck.stat(s, "80,1 %", "cobertura del intervalo del 80 %", 10.6, 3.35, 2.0, size=34)
    deck.bullets(s, [[("Reproducible: ", True), ("el pliegue 0 da las cifras exactas de Week 6 (S/ 155 372,04 y S/ 155 396,37).", False)],
                     [("Error de especificación: ", True), ("el Ridge de Week 6 usaba el área lineal para predecir log(precio): +8,5 % de error.", False)],
                     [("Selección automática ", True), ("con la regla de Week 6; D mejora el MdAPE en los 20 distritos.", False)]],
                 0.6, 5.1, 12.1, 1.8, size=15)

    # 10 error por distrito
    s = deck.slide("Motor de valoración", "Mejora en todos los distritos, con incertidumbre honesta",
                   notes="El intervalo usa residuos fuera de pliegue. Con residuos de entrenamiento cubría solo el 72 %. Los avisos por debajo del intervalo no se presentan como gangas.")
    deck.image(s, figures / "fig_modelos_error_distrito.png", 0.5, 1.55, 6.4, 5.35)
    deck.bullets(s, [[("Intervalo del 80 % cross-conformal: ", True), ("cuantiles de los residuos fuera de pliegue; cobertura 80,1 % (antes 72 % con residuos de entrenamiento).", False)],
                     [("388 avisos (10 %) ", True), ("quedan bajo el intervalo: pasan a una lista \"por verificar\".", False)],
                     [("Ate (29 avisos): ", True), ("mejora marginal del MdAPE y +3 % de MAE; la regla de distritos chicos lo acepta (cociente 0,87).", False)],
                     [("Alternativa interpretable: ", True), ("Ridge v2, a 7 % de D, si las explicaciones SHAP no resultan legibles.", False)]],
                 7.2, 1.75, 5.5, 5.0, size=15, gap=10)

    # 11 geocodificacion
    s = deck.slide("Enriquecimiento geoespacial", f"Geocodificación: de 10 avisos a {int(geo_total.avisos)}, con {geo_total.tasa_exito:.0%} validados".replace("%", " %"),
                   notes="La primera corrida validó 57 %. La auditoría mostró que 31 rechazos eran falsos: OSM los ubicaba en el distrito correcto pero caían fuera del polígono simplificado.")
    rows = [["Distrito", "Avisos", "Validados", "Tasa"]]
    for district in ["JESUS MARIA", "SURQUILLO", "BARRANCO", "SAN BORJA", "PUEBLO LIBRE"]:
        row = geo.loc[district]
        rows.append([district.title(), int(row.avisos), int(row.exitosos), f"{row.tasa_exito:.0%}".replace("%", " %")])
    rows.append(["Total", int(geo_total.avisos), int(geo_total.exitosos), f"{geo_total.tasa_exito:.0%}".replace("%", " %")])
    deck.table(s, rows, 0.6, 1.8, [2.6, 1.1, 1.3, 1.1], row_h=0.48, size=14, highlight=len(rows) - 1)
    deck.bullets(s, [[("Limpieza: ", True), ("departamento, \"al 500\", \"cerca a…\", abreviaturas Jr./Av./Psj.", False)],
                     [("Tres intentos: ", True), ("dirección, calle sin número, urbanización (precisión \"zona\").", False)],
                     [("Validación sin imputar: ", True), ("polígono ±300 m o distrito según OSM; 1,1 s por consulta con caché.", False)],
                     [("57 % → 83 %: ", True), ("31 falsos rechazos por el GeoJSON simplificado.", False)],
                     [("Distancia mediana: ", True), ("colegio 158 m, parque 102 m, paradero 221 m.", False)]],
                 7.0, 1.8, 5.7, 5.0, size=15, gap=10)

    # 12 recomendacion
    s = deck.slide("Capa de recomendación", "Un ranking por perfil, explicado y sin imputar",
                   notes="La primera versión no cumplía REQ-01: con el mismo presupuesto, María y Carlos recibían el mismo top 10. Las reglas de 'por verificar' y diversidad salieron de esa verificación.")
    deck.text(s, "score = Σ peso × componente / Σ pesos de los componentes disponibles", 0.6, 1.65, 12.1, 0.5, size=18,
              bold=True, color=INDIGO, font=TITLE_FONT)
    deck.bullets(s, [[("Componentes: ", True), ("precio (logística del opportunity score), seguridad, colegios y servicios, constructora.", False)],
                     [("Faltante ≠ cero: ", True), ("sale del cálculo y la explicación lo declara.", False)],
                     [("Precio atípico ", True), ("→ lista \"por verificar\", no ranking.", False)],
                     [("Diversidad: ", True), ("máximo 3 avisos por distrito en el top 10.", False)],
                     [("Iteración: ", True), ("la v1 daba el mismo top 10 a ambos perfiles (Jaccard 1,0).", False)]],
                 0.6, 2.35, 5.6, 4.5, size=15, gap=9)
    rows = [["Criterio", "Resultado"]]
    labels = ["REQ-01 perfiles distintos (Jaccard top 10)", "REQ-01 mismo presupuesto (Jaccard)", "REQ-01 ρ de Spearman entre scores",
              "REQ-02 avisos con explicación", "Atípicos en el ranking", "Parciales que lo declaran", "RNF-01 tiempo del ranking"]
    for label, (_, row) in zip(labels, checks.iterrows()):
        value = row.valor
        shown = (f"{value:.0%}".replace("%", " %") if "%" in row.metrica else
                 f"{value:.2f} s".replace(".", ",") if row.metrica == "segundos" else f"{value:.2f}".replace(".", ","))
        rows.append([label, f"{shown}  ✓" if row.cumple else shown])
    deck.table(s, rows, 6.6, 2.35, [4.4, 1.7], row_h=0.5, size=13)

    # 13 arquitectura
    s = deck.slide("Arquitectura", "Por lotes: el pipeline precalcula, el servicio solo pondera",
                   notes="Sólido: implementado hoy. Punteado: planificado para Week 10 a 15. El ranking de 3 896 avisos toma milisegundos.")
    deck.image(s, design / "architecture.png", 0.5, 1.5, 12.3, 5.45)

    # 14 prototipo
    s = deck.slide("Interfaz", "Prototipo de baja fidelidad con datos reales",
                   notes="El prototipo se abre con doble clic y recalcula en el navegador. Verificamos que su top 10 es idéntico al del pipeline para ambos perfiles.")
    deck.image(s, design / "user_flow.png", 0.5, 1.5, 12.3, 5.45)

    # 15 requerimientos
    s = deck.slide("Requerimientos", "Estado al cierre de la primera fase",
                   notes="Los criterios de aceptación de Week 5 se cumplen salvo el modelo de visión, bloqueado por datos, y el despliegue, que es el hito de Week 10.")
    status = requirement_status()
    rf, rnf = status["RF"], status["RNF"]
    for index, (value, label, color) in enumerate([
            (str(rf.get("✅", 0)), f"de {sum(rf.values())} funcionales implementados y verificados", INDIGO),
            (str(rf.get("🟡", 0)), "funcionales parciales, con plan y semana", INDIGO),
            (str(rnf.get("✅", 0)), f"de {sum(rnf.values())} no funcionales cumplidos", INDIGO),
            (str(rf.get("❌", 0)), "bloqueado por datos: modelo de visión", ORANGE)]):
        deck.stat(s, value, label, 0.6 + index * 3.1, 1.75, 2.8, color=color, size=44)
    rows = [["Criterio de aceptación (Week 5)", "Estado"],
            ["≥ 500 avisos con < 10 % de faltantes críticos", "✓ 3 896 avisos, 0 faltantes"],
            ["MAE comparado contra la línea base", "✓ −17,1 %"],
            ["Dos perfiles, dos rankings", "✓ Jaccard 0,43"],
            ["Explicación en cada recomendación", "✓ 100 %"],
            ["Modelo de visión ≥ 70 %", "Sin datos: decisión en Week 10"],
            ["Prototipo desplegado", "Local hoy; URL en Week 10"]]
    deck.table(s, rows, 0.6, 3.6, [7.4, 4.7], row_h=0.44, size=14)

    # 16 plan
    s = deck.slide("Plan hasta Week 15", "Prioridades y responsables",
                   notes="Week 8 es el parcial: la usamos para incorporar la retroalimentación y cerrar decisiones de stack.")
    timeline = [("W8", "Parcial", "retroalimentación y stack"), ("W9", "Construir", "geocodificación completa, API, web app"),
                ("W10", "Prototipo funcional", "flujo desplegado, mapa, decisión de visión"),
                ("W11", "Evaluar", "SHAP, umbral Alcabala, seguridad, usuarios"),
                ("W12", "Evaluación", "casos de estudio, guardar y comparar"),
                ("W13–14", "Cerrar", "refresco, accesibilidad, reporte y video"), ("W15", "Delivery 2", "presentación final")]
    for index, (week, name, detail) in enumerate(timeline):
        x = 0.6 + index * 1.75
        milestone = name in {"Prototipo funcional", "Evaluación", "Delivery 2"}
        deck.card(s, x, 1.75, 1.6, 2.0, fill=INDIGO if milestone else LAVENDER_SOFT, line=None)
        deck.text(s, week, x + 0.15, 1.85, 1.3, 0.4, size=16, bold=True, color=WHITE if milestone else INDIGO)
        deck.text(s, name, x + 0.15, 2.25, 1.35, 0.5, size=13, bold=True, color=WHITE if milestone else INK)
        deck.text(s, detail, x + 0.15, 2.75, 1.35, 1.0, size=11, color=LAVENDER_SOFT if milestone else INK_2)
    rows = [["Integrante", "Responsabilidad principal hasta Week 15"],
            ["Denzel · Cloud & DevOps", "Contenedor y despliegue, GitHub Actions, geocodificación completa, URL pública"],
            ["Jyns · Machine Learning", "Valoración y evaluación, recomendación, explicaciones SHAP, decisión de visión"],
            ["Lisseth · Data Analyst", "Calidad del pipeline, POIs, diccionario, umbral Alcabala, índice de seguridad"],
            ["Mafer · Full-Stack & UX/UI", "Web app y mapa, alta fidelidad, prueba con usuarios, página y video"]]
    deck.table(s, rows, 0.6, 4.1, [3.4, 8.7], row_h=0.5, size=13)

    # 17 cierre
    s = deck.slide(dark=True, notes="Cerramos con los riesgos que definen la segunda fase y abrimos preguntas.")
    deck.text(s, "PRÓXIMOS PASOS Y RIESGOS", 0.8, 0.9, 11, 0.4, size=13, bold=True, color=LAVENDER, spacing=250)
    deck.text(s, "Lo que falta decidir antes de Week 10", 0.8, 1.35, 11.5, 0.9, size=34, bold=True, color=WHITE, font=TITLE_FONT)
    for index, (head, body) in enumerate([
        ("Imágenes de entorno", "Mapillary más un set propio, o sacar el modelo de visión del alcance y declararlo."),
        ("Sesgo en seguridad", "Normalizar por superficie o por modalidad; declararlo en la interfaz."),
        ("Cierre vs oferta", "Umbral de cochera por distrito con la relación valor/autovalúo de Alcabala."),
        ("Inventario vigente", "Complementar el dataset sin fecha con el scraper por sitemap de Week 6.")]):
        x = 0.8 + (index % 2) * 6.0
        y = 2.7 + (index // 2) * 1.9
        deck.text(s, head, x, y, 5.6, 0.5, size=20, bold=True, color=LAVENDER)
        deck.text(s, body, x, y + 0.5, 5.4, 1.1, size=16, color=WHITE)
    deck.text(s, "Gracias · preguntas", 0.8, 6.55, 11, 0.5, size=18, bold=True, color=WHITE)

    deck.prs.save(OUTPUT)
    print(f"{deck.count} diapositivas -> {OUTPUT.name}")


def export_pdf():
    """Exporta a PDF con PowerPoint (solo Windows con Office)."""
    try:
        import win32com.client
    except ImportError:
        print("PowerPoint no disponible: exporta el PDF manualmente")
        return
    app = win32com.client.Dispatch("PowerPoint.Application")
    try:
        deck = app.Presentations.Open(str(OUTPUT), True, False, False)
        deck.SaveAs(str(OUTPUT.with_suffix(".pdf")), 32)
        deck.Close()
        print(f"pdf -> {OUTPUT.with_suffix('.pdf').name}")
    finally:
        app.Quit()


if __name__ == "__main__":
    build()
    if "--no-pdf" not in sys.argv:
        export_pdf()
