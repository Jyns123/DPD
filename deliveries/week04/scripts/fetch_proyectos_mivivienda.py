"""descarga proyectos del buscador de fondo mivivienda (nuevo credito y techo propio)."""
import sys
import time

import pandas as pd
import requests

PROXY = "https://fondomivivienda.pe/api/servicios/proxy"
HEADERS = {"User-Agent": "Mozilla/5.0 (inmoscore-dpd, proyecto academico)",
           "Content-Type": "application/json",
           "Origin": "https://fondomivivienda.pe",
           "Referer": "https://fondomivivienda.pe/buscador-proyectos"}
# programa -> (service, opcion)
PROGRAMAS = {"nuevo_credito_mivivienda": ("cmv", "CMV"), "techo_propio": ("tp", "TP")}

COLS = {
    "strproyecto": "proyecto", "strcodproyecto": "codigo_proyecto",
    "strpromotor": "promotor", "strdireccion": "direccion",
    "strdepartamento": "departamento", "strprovincia": "provincia",
    "strdistrito": "distrito", "strperiodopub": "periodo_publicacion",
    "decareatechmin": "area_techada_min", "decareatechmax": "area_techada_max",
    "decarealotemin": "area_lote_min", "decarealotemax": "area_lote_max",
    "decpreciomin": "precio_min", "decpreciomax": "precio_max",
    "decofertadisp": "unidades_disponibles", "intverde": "bono_verde",
    "strlink": "web", "strtelefono": "telefono",
}


def consultar(service, opcion, departamento="", provincia=""):
    cuerpo = {"opcion": opcion, "nombres": "", "departamento": departamento,
              "provincia": provincia, "distrito": "", "areamin": "", "areamax": "",
              "arealotemin": "", "arealotemax": "", "preciomin": "", "preciomax": "",
              "bonoverde": "", "promotor": "", "proyecto": ""}
    payload = {"service": service, "path": "api/ofertainmobiliariajwt",
               "method": "POST", "body": cuerpo}
    r = requests.post(PROXY, headers=HEADERS, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


def main(salida="data/samples/proyectos_mivivienda.csv"):
    filas = []
    for programa, (service, opcion) in PROGRAMAS.items():
        datos = consultar(service, opcion)
        for p in datos:
            fila = {nuevo: p.get(viejo) for viejo, nuevo in COLS.items()}
            fila["programa"] = programa
            filas.append(fila)
        print(f"{programa}: {len(datos)} proyectos", file=sys.stderr)
        time.sleep(3)  # cortesia con el servicio

    d = pd.DataFrame(filas)
    d["periodo_publicacion"] = d.periodo_publicacion.str.split(" ").str[0]
    d = d.sort_values(["programa", "departamento", "distrito", "proyecto"])
    d.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} proyectos, {d.promotor.nunique()} promotores -> {salida}",
          file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
