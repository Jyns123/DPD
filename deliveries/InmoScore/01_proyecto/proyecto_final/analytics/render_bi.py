"""Dibuja las series del tablero como SVG, sin librerías adicionales.

Lee un objeto JSON de stdin y devuelve {trend, heatmap} en stdout.
La API prepara los agregados; este archivo solo valida y dibuja esos valores.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import date, timedelta
from html import escape


INK = "#173d31"
MUTED = "#53675e"
GRID = "#e3eae5"
BAR = "#8eb99f"
LINE = "#087b83"
FONT = "Arial, Helvetica, sans-serif"
MAX_DAYS = 92
MAX_COUNT = 20000


def count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Los conteos deben ser números enteros no negativos.")
    if value < 0 or value > MAX_COUNT or not math.isfinite(value) or int(value) != value:
        raise ValueError(f"Los conteos deben ser enteros entre 0 y {MAX_COUNT}.")
    return int(value)


def text(x: float, y: float, label: object, *, size: int = 12,
         anchor: str = "start", color: str = MUTED, weight: int = 400) -> str:
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}" font-weight="{weight}">'
            f'{escape(str(label))}</text>')


def start_svg(kind: str, title: str, description: str, height: int, width: int = 960) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-labelledby="{kind}-title {kind}-description" '
        f'style="width:100%;height:auto;display:block;font-family:{FONT}">',
        f'<title id="{kind}-title">{escape(title)}</title>',
        f'<desc id="{kind}-description">{escape(description)}</desc>',
        f'<rect width="{width}" height="{height}" rx="12" fill="#ffffff"/>',
    ]


def daily_rows(raw: object) -> list[tuple[date, int, int]]:
    if not isinstance(raw, list):
        raise ValueError("daily debe ser una lista.")
    values: dict[date, tuple[int, int]] = {}
    for row in raw:
        if not isinstance(row, dict) or not isinstance(row.get("date"), str):
            raise ValueError("Cada día necesita fecha, búsquedas y sesiones con salida.")
        day = date.fromisoformat(row["date"])
        if day.isoformat() != row["date"]:
            raise ValueError("La fecha debe usar YYYY-MM-DD.")
        if day in values:
            raise ValueError("Las fechas diarias no deben repetirse.")
        values[day] = (count(row.get("searches")), count(row.get("referrals")))
    if not values:
        return []
    first, last = min(values), max(values)
    length = (last - first).days + 1
    if length > MAX_DAYS:
        raise ValueError(f"El gráfico admite hasta {MAX_DAYS} días por consulta.")
    return [(day, *values.get(day, (0, 0)))
            for day in (first + timedelta(days=index) for index in range(length))]


def scale(maximum: int) -> tuple[int, int]:
    """Límites cómodos de leer, sin fracciones para un conteo de eventos."""
    raw_step = max(1, maximum / 4)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    step = next(multiplier * magnitude for multiplier in (1, 2, 5, 10)
                if multiplier * magnitude >= raw_step)
    return max(step, math.ceil(maximum / step) * step), step


def trend_svg(raw: object, mode: str) -> str:
    rows = daily_rows(raw)
    origin = "Escenario simulado" if mode == "sim" else "Interacciones registradas"
    description = (f"{origin}. Barras de búsquedas y línea de sesiones con salida al anuncio, con una misma "
                   "escala de conteos. Los días sin eventos dentro del periodo observado "
                   "aparecen en cero. No representa ventas confirmadas.")
    parts = start_svg("trend", "Búsquedas y sesiones con salida por día", description, 390)
    parts += [text(66, 27, origin, size=12, weight=700),
              '<rect x="625" y="16" width="14" height="12" rx="3" fill="' + BAR + '"/>',
              text(648, 27, "Búsquedas"),
              f'<path d="M768 22H793" fill="none" stroke="{LINE}" stroke-width="3"/>',
              f'<circle cx="780" cy="22" r="4" fill="#fff" stroke="{LINE}" stroke-width="2"/>',
              text(802, 27, "Sesiones con salida")]
    if not rows:
        parts += [text(480, 182, "Todavía no hay actividad en este periodo.", size=18, anchor="middle", color=INK),
                  text(480, 210, "Los gráficos aparecerán cuando existan registros.", size=13, anchor="middle"), "</svg>"]
        return "".join(parts)

    left, top, width, height = 66, 57, 866, 258
    maximum, step = scale(max(max(searches, referrals) for _, searches, referrals in rows))
    slot = width / len(rows)
    bar_width = max(0.15, min(56, slot * 0.58))
    y = lambda value: top + height - (value / maximum) * height
    for tick in range(0, maximum + 1, step):
        yy = y(tick)
        parts += [f'<path d="M{left} {yy:.2f}H{left + width}" stroke="{GRID}" stroke-width="1"/>',
                  text(left - 12, yy + 4, f"{tick:,}".replace(",", " "), anchor="end")]
    parts.append(text(left, top - 12, "Conteo", size=10))
    points = []
    for index, (day, searches, referrals) in enumerate(rows):
        xx = left + slot * (index + 0.5)
        label = f"{day.isoformat()}: {searches} búsquedas · {referrals} sesiones con salida"
        parts.append(f'<rect x="{xx - bar_width / 2:.2f}" y="{y(searches):.2f}" '
                     f'width="{bar_width:.2f}" height="{height * searches / maximum:.2f}" '
                     f'rx="{min(3, bar_width / 3):.2f}" fill="{BAR}"><title>{escape(label)}</title></rect>')
        points.append((xx, y(referrals), label))
    if len(points) > 1:
        path = "M" + " L".join(f"{xx:.2f} {yy:.2f}" for xx, yy, _ in points)
        parts.append(f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    # También dibuja el punto si hay un solo día; no desaparece la segunda serie.
    marker_indexes = set(range(len(points))) if len(points) <= 60 else {0, len(points) - 1}
    for index in sorted(marker_indexes):
        xx, yy, label = points[index]
        parts.append(f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="4" fill="#fff" stroke="{LINE}" stroke-width="2.5"><title>{escape(label)}</title></circle>')
    label_indexes = sorted({round(index * (len(rows) - 1) / min(7, len(rows) - 1))
                            for index in range(min(8, len(rows)))}) if len(rows) > 1 else [0]
    for index in label_indexes:
        day = rows[index][0]
        parts.append(text(left + slot * (index + 0.5), 340, day.strftime("%d/%m"), anchor="middle"))
    period = rows[0][0].isoformat() if len(rows) == 1 else f"{rows[0][0].isoformat()} — {rows[-1][0].isoformat()}"
    parts += [text(left, 371, period, size=11), text(932, 371, "Misma escala · conteos diarios", size=11, anchor="end"), "</svg>"]
    return "".join(parts)


def heat_color(value: int, maximum: int) -> str:
    if value == 0:
        return "#f0f4f1"
    light, dark = (220, 237, 226), (23, 86, 68)
    ratio = value / maximum
    return "#" + "".join(f"{round(start + (end - start) * ratio):02x}" for start, end in zip(light, dark))


def cell_text_color(background: str) -> str:
    """Mantiene legibles los conteos tanto sobre tonos claros como oscuros."""
    channels = [int(background[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
              for channel in channels]
    luminance = sum(channel * weight for channel, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    return "#ffffff" if luminance < 0.179 else "#000000"


def heatmap_svg(raw: object, mode: str) -> str:
    if raw == []:
        matrix = [[0] * 6 for _ in range(7)]
    elif isinstance(raw, list) and len(raw) == 7 and all(isinstance(row, list) and len(row) == 6 for row in raw):
        matrix = [[count(value) for value in row] for row in raw]
    else:
        raise ValueError("heatmap debe tener 7 días por 6 bloques horarios.")
    weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    hours = ["00–03 h", "04–07 h", "08–11 h", "12–15 h", "16–19 h", "20–23 h"]
    maximum = max(value for row in matrix for value in row)
    total = sum(sum(row) for row in matrix)
    origin = "Escenario simulado" if mode == "sim" else "Interacciones registradas"
    parts = start_svg("heatmap", "Actividad por día y franja horaria",
                      f"{origin}. {total} eventos repartidos en siete días de la semana y seis bloques de cuatro horas. "
                      "Cada celda muestra su conteo. Un color más oscuro indica más actividad.", 390, 560)
    parts.append(text(66, 27, origin, size=15, weight=700))
    left, top, cell_width, cell_height, gap = 66, 65, 76, 34, 4
    for column, label in enumerate(hours):
        parts.append(text(left + column * (cell_width + gap) + cell_width / 2, 51, label, anchor="middle", size=14))
    for row, day in enumerate(weekdays):
        yy = top + row * (cell_height + gap)
        parts.append(text(left - 10, yy + 23, day_labels[row], anchor="end", size=15))
        for column, value in enumerate(matrix[row]):
            xx = left + column * (cell_width + gap)
            fill = heat_color(value, maximum or 1)
            foreground = cell_text_color(fill)
            tooltip = f"{day}, {hours[column]}: {value} eventos"
            parts += [f'<rect x="{xx}" y="{yy}" width="{cell_width}" height="{cell_height}" rx="5" fill="{fill}"><title>{escape(tooltip)}</title></rect>',
                      text(xx + cell_width / 2, yy + 23, f"{value:,}".replace(",", " "), anchor="middle", size=16, color=foreground, weight=700)]
    parts.append(text(left, 365, "Sin actividad registrada" if total == 0 else f"{total:,} eventos".replace(",", " "), size=14))
    parts.append(text(344, 365, "0", size=13, anchor="end"))
    for index in range(6):
        shade = heat_color(round(maximum * index / 5), maximum or 1)
        parts.append(f'<rect x="{353 + index * 26}" y="351" width="24" height="16" rx="3" fill="{shade}"/>')
    parts += [text(515, 365, str(maximum), size=13), "</svg>"]
    return "".join(parts)


def indicator_svg(chart: dict) -> str:
    values = chart["values"]
    points = [value for value in values if value is not None]
    kind = chart["kind"]
    description = "Valores de la selección del tablero."
    if points:
        description += f" Último valor representado: {points[-1]:.6g}."
    parts = start_svg("indicator", "Gráfico del indicador", description, 96, 320)
    if not points:
        return "".join(parts + [text(160, 53, "Sin datos", anchor="middle"), "</svg>"])
    maximum = max(1, chart.get("max") or 0, max(abs(value) for value in points))
    if kind in {"level", "signed"}:
        value = points[0]
        parts.append('<rect x="14" y="36" width="292" height="24" rx="7" fill="#edf2ed"/>')
        if kind == "signed":
            width = 146 * abs(value) / maximum
            left = 160 - width if value < 0 else 160
            fill = "#ad5541" if value < 0 else BAR
            parts.append('<path d="M160 28V68" stroke="#53675e" stroke-width="1"/>')
        else:
            width = 292 * max(0, value) / maximum
            left, fill = 14, BAR
        parts.append(f'<rect x="{left:.2f}" y="36" width="{width:.2f}" height="24" rx="6" fill="{fill}"/>')
    else:
        top, bottom, left, right = 10, 84, 14, 306
        minimum = min(0, min(points))
        for line in (10, 47, 84):
            parts.append(f'<path d="M{left} {line}H{right}" stroke="{GRID}" stroke-width="1"/>')
        segments: list[list[tuple[float, float]]] = [[]]
        for index, value in enumerate(values):
            if value is None:
                if segments[-1]:
                    segments.append([])
                continue
            x = (left + right) / 2 if len(values) == 1 else left + (right-left)*index/(len(values)-1)
            y = bottom - (bottom-top)*(value-minimum)/(maximum-minimum)
            segments[-1].append((x, y))
        for segment in segments:
            if len(segment) > 1:
                path = " L".join(f"{x:.2f} {y:.2f}" for x, y in segment)
                area = f"M{segment[0][0]:.2f} {bottom} L{path} L{segment[-1][0]:.2f} {bottom} Z"
                parts.append(f'<path d="{area}" fill="{BAR}" opacity="0.26"/>')
                parts.append(f'<path d="M{path}" fill="none" stroke="{LINE}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')
            if segment:
                x, y = segment[-1]
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{LINE}"/>')
    return "".join(parts + ["</svg>"])


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    def reject_constant(value: str) -> None:
        raise ValueError(f"Número inválido: {value}")
    payload = json.load(sys.stdin, parse_constant=reject_constant)
    if not isinstance(payload, dict) or payload.get("mode") not in {"sim", "live"}:
        raise ValueError("mode debe ser sim o live.")
    if "charts" in payload:
        result = {"charts": {chart["id"]: indicator_svg(chart) for chart in payload["charts"]}}
    else:
        result = {"trend": trend_svg(payload.get("daily", []), payload["mode"]),
                  "heatmap": heatmap_svg(payload.get("heatmap", []), payload["mode"])}
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OverflowError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
