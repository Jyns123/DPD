"""Convierte Delivery1Report.md (fuente editable) en Delivery1Report.pdf.

Markdown -> HTML con estilos de impresion -> PDF con Edge o Chrome headless. El
HTML intermedio se escribe junto al .md para que las rutas de las figuras
resuelvan, y se borra al terminar.

    python code/docs/build_report.py
"""
import subprocess
import tempfile
from pathlib import Path

import markdown

from render_design import WEEK07, browser

SOURCE = WEEK07 / "Delivery1Report.md"
OUTPUT = WEEK07 / "Delivery1Report.pdf"

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm;
        @bottom-right { content: "InmoScore · Delivery 1 · " counter(page); font: 8.5pt 'Segoe UI', sans-serif; color: #8a8983; } }
@page :first { @bottom-right { content: none; } }
* { box-sizing: border-box; }
body { font: 10.3pt/1.5 'Segoe UI', Calibri, sans-serif; color: #1b1b1a; margin: 0; }
h1, h2, h3 { line-height: 1.2; break-after: avoid; }
h2 { font-size: 16pt; margin: 20pt 0 8pt; color: #1f3f6e; }
h3 { font-size: 12pt; margin: 14pt 0 5pt; }
p { margin: 0 0 7pt; }
ul, ol { margin: 0 0 8pt; padding-left: 18pt; }
li { margin: 2pt 0; }
a { color: #1f5fae; text-decoration: none; }
code { font: 8.8pt Consolas, monospace; background: #f1f1ee; padding: 0 2pt; border-radius: 2pt; }
pre { background: #f5f5f2; border: 1px solid #e1e0d9; border-radius: 4pt; padding: 7pt 9pt; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.5pt; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt; font-size: 8.6pt; line-height: 1.35; break-inside: auto; }
tr { break-inside: avoid; }
th { text-align: left; background: #eef2f7; color: #1b1b1a; font-weight: 600; }
th, td { border-bottom: 1px solid #dcdbd4; padding: 3.5pt 5pt; vertical-align: top; }
img { max-width: 100%; display: block; margin: 6pt auto 2pt; break-inside: avoid; }
p:has(> img) { break-inside: avoid; break-after: avoid; margin: 0; }
p:has(> strong:only-child) { break-after: avoid; }
p:has(> em:only-child) { font-size: 8.8pt; color: #55544f; margin-bottom: 11pt; }
.page-break { break-after: page; }
.formula { text-align: center; font-size: 11pt; margin: 8pt 0 10pt; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; break-after: page; }
.cover h1 { font-size: 40pt; color: #1f3f6e; margin: 0 0 6pt; letter-spacing: -.5pt; }
.cover h2 { font-size: 18pt; color: #1b1b1a; margin: 0 0 28pt; font-weight: 500; }
.cover p { font-size: 11pt; color: #3d3c38; margin-bottom: 10pt; }
"""


def main():
    text = SOURCE.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["extra", "sane_lists"], output_format="html5")
    html = (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>InmoScore · Delivery 1</title>'
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    page = WEEK07 / "_Delivery1Report.html"
    page.write_text(html, encoding="utf-8")
    try:
        with tempfile.TemporaryDirectory() as profile:
            subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
                            "--no-pdf-header-footer", "--virtual-time-budget=5000", f"--print-to-pdf={OUTPUT}",
                            page.as_uri()], check=True, capture_output=True, timeout=180)
    finally:
        page.unlink(missing_ok=True)
    print(f"pdf -> {OUTPUT.relative_to(WEEK07)}")


if __name__ == "__main__":
    main()
