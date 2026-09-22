"""Renderiza el canvas, los diagramas (design/*.html) y los wireframes del prototipo.

Usa Edge o Chrome en modo headless, con un perfil temporal para no tocar el del
usuario. El tamano de cada diagrama se lee de <meta name="render-size">.

    python code/docs/render_design.py
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WEEK07 = Path(__file__).resolve().parents[2]
DESIGN = WEEK07 / "design"
PROTOTYPE = WEEK07 / "prototype" / "index.html"
CANVAS = WEEK07 / "DataProductCanvas.html"
BROWSERS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path("/usr/bin/google-chrome"), Path("/usr/bin/chromium"),
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
]
# estados del prototipo que se exportan como wireframes: (archivo, parametros, ancho, alto)
WIREFRAMES = [
    ("wf-01-perfil-maria.png", "perfil=maria", 1400, 900),
    ("wf-02-ranking-maria.png", "perfil=maria&vista=ranking", 1400, 1500),
    ("wf-03-ranking-carlos.png", "perfil=carlos&vista=ranking", 1400, 1500),
    ("wf-04-detalle-maria.png", "perfil=maria&vista=detalle", 1400, 900),
    ("wf-05-movil-carlos.png", "perfil=carlos&vista=ranking", 420, 1500),
]


def browser():
    for path in BROWSERS:
        if path.exists():
            return str(path)
    found = shutil.which("msedge") or shutil.which("chrome") or shutil.which("chromium")
    if not found:
        sys.exit("No se encontro Edge ni Chrome para renderizar")
    return found


def run(args, profile):
    command = [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               f"--user-data-dir={profile}", "--virtual-time-budget=4000", *args]
    subprocess.run(command, check=True, capture_output=True, timeout=180)


def render(url, png, size, profile, pdf=None, scale=2):
    width, height = size
    run([f"--window-size={width},{height}", f"--force-device-scale-factor={scale}", f"--screenshot={png}", url], profile)
    print(f"png -> {png.relative_to(WEEK07)}")
    if pdf:
        run(["--no-pdf-header-footer", f"--print-to-pdf={pdf}", url], profile)
        print(f"pdf -> {pdf.relative_to(WEEK07)}")


def main():
    with tempfile.TemporaryDirectory() as profile:
        # primero los wireframes: user_flow.html los usa como imagenes
        wireframes = DESIGN / "wireframes"
        wireframes.mkdir(exist_ok=True)
        for name, query, width, height in WIREFRAMES:
            render(f"{PROTOTYPE.as_uri()}?{query}", wireframes / name, (width, height), profile, scale=1)
        render(CANVAS.as_uri(), CANVAS.with_suffix(".png"), (1588, 1123), profile, pdf=CANVAS.with_suffix(".pdf"))
        for source in sorted(DESIGN.glob("*.html")):
            meta = re.search(r'name="render-size" content="(\d+)x(\d+)"', source.read_text(encoding="utf-8"))
            size = (int(meta.group(1)), int(meta.group(2))) if meta else (1600, 1000)
            render(source.as_uri(), source.with_suffix(".png"), size, profile, pdf=source.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
