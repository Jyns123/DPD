"""descarga licencias y conformidades de obra de la municipalidad de lima."""
import sys

import pandas as pd
import requests

BASE = "https://www.datosabiertos.gob.pe/sites/default/files"
HEADERS = {"User-Agent": "Mozilla/5.0 (inmoscore-dpd, proyecto academico)",
           "Referer": "https://www.datosabiertos.gob.pe/"}
FUENTES = {
    "licencia": f"{BASE}/DATASET%20RESOLUCION%20DE%20LICENCIAS%20DE%20EDIFICACION%20MOD%20A%2CB%2CC%2CD.csv",
    "conformidad": f"{BASE}/DATASET%20CONFORMIDAD%20Y%20DECLARATORIA%20DE%20FABRICA%20EMITIDOS%20050125.csv",
}
# columnas comunes tras normalizar nombres
COMUNES = ["etapa", "distrito", "expediente", "fecha_inicio", "fecha_emision",
           "modalidad", "zonificacion", "altura", "codigo_catastral",
           "uso", "valorizacion", "solicitante"]

RENOMBRES = {
    "N EXPEDIENTE": "expediente", "N DE EXPEDIENTE": "expediente",
    "FECHA DE INICIO DE TRAMITE": "fecha_inicio",
    "FECHA_DE_INICIO_DE_TRAMITE": "fecha_inicio",
    "FECHA DE EMISION DE LICENCIA": "fecha_emision",
    "FECHA_DE_EMISION": "fecha_emision",
    "MODALIDAD DE APROBACION": "modalidad",
    "MODALIDAD_DE_APROBACION": "modalidad",
    "TIPO DE USO": "uso", "USO": "uso",
    "VALORIZACION DE LA OBRA": "valorizacion",
    "VALORIZACION_DE_LA_OBRA": "valorizacion",
    "CODIGO CATASTRAL": "codigo_catastral",
    "CODIGO_CATASTRAL": "codigo_catastral",
    "SOLICITANTE": "solicitante", "DISTRITO": "distrito",
    "ZONIFICACION": "zonificacion", "ALTURA": "altura",
}


def descargar(url, destino):
    r = requests.get(url, headers=HEADERS, timeout=300)
    r.raise_for_status()
    open(destino, "wb").write(r.content)
    return destino


def normalizar(ruta, etapa):
    d = pd.read_csv(ruta, sep=";", encoding="latin-1")
    # los encabezados traen saltos de linea y caracteres mal codificados
    d.columns = [c.replace("\n", "").replace("°", "").replace("\xb0", "")
                  .replace("�", "").strip() for c in d.columns]
    d = d.rename(columns=RENOMBRES)
    d["etapa"] = etapa
    for c in COMUNES:
        if c not in d:
            d[c] = pd.NA
    return d[COMUNES]


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/samples/obras_cercado_lima_sample.csv"
    partes = []
    for etapa, url in FUENTES.items():
        ruta = descargar(url, f"data/raw/obras_{etapa}.csv")
        partes.append(normalizar(ruta, etapa))
        print(f"{etapa}: {len(partes[-1])} filas", file=sys.stderr)
    d = pd.concat(partes, ignore_index=True).sort_values(["etapa", "fecha_emision"])
    d.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} filas -> {salida}", file=sys.stderr)
