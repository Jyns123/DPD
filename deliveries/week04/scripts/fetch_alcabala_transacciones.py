"""descarga transferencias de predios del impuesto de alcabala (sat de lima).

es la unica fuente de transacciones cerradas que encontramos: el alcabala se paga
sobre el valor real de transferencia, no sobre el precio pedido.
"""
import sys

import pandas as pd
import requests

BASE = "https://www.datosabiertos.gob.pe/sites/default/files"
HEADERS = {"User-Agent": "Mozilla/5.0 (inmoscore-dpd, proyecto academico)",
           "Referer": "https://www.datosabiertos.gob.pe/"}
PERIODOS = {
    "2026-S1": f"{BASE}/Alcabala_Medio_de_Determinacion_Ene_Junio_2026_II_TRIM_SAT.csv",
}
# cocheras y depositos se registran como predios aparte y hunden la mediana
UMBRAL_COCHERA = 80000


def descargar(url, destino):
    r = requests.get(url, headers=HEADERS, timeout=600)
    r.raise_for_status()
    open(destino, "wb").write(r.content)
    return destino


def compraventas(ruta):
    d = pd.read_csv(ruta, encoding="utf-8-sig")
    return d[(d["Tipo Transferencia"] == "Compra/Venta")
             & (d["Porcentaje de Propiedad"] == 100.0)
             & (d["Valor Transferencia Soles"] > 0)].copy()


def resumen_distrito(cv, periodo):
    v = "Valor Transferencia Soles"
    g = cv.groupby("Distrito")[v]
    d = pd.DataFrame({
        "n_transacciones": g.size(),
        "valor_p25": g.quantile(0.25).round(0),
        "valor_mediana": g.median().round(0),
        "valor_p75": g.quantile(0.75).round(0),
        "valor_p90": g.quantile(0.90).round(0),
        # proporcion de operaciones chicas: proxy de cochera/deposito
        "pct_bajo_umbral": (g.apply(lambda s: (s < UMBRAL_COCHERA).mean() * 100)).round(1),
    }).reset_index().rename(columns={"Distrito": "distrito"})

    nuevas = (cv[cv["Primera Venta?"] == "SI"].groupby("Distrito")[v]
                .agg(n_primera_venta="size", mediana_primera_venta="median")
                .round(0).reset_index().rename(columns={"Distrito": "distrito"}))
    d = d.merge(nuevas, on="distrito", how="left")
    d[["n_primera_venta"]] = d[["n_primera_venta"]].fillna(0).astype(int)
    d.insert(1, "periodo", periodo)
    return d.sort_values("n_transacciones", ascending=False)


def main(salida="data/samples/alcabala_transacciones_distrito.csv"):
    partes = []
    for periodo, url in PERIODOS.items():
        ruta = descargar(url, f"data/raw/alcabala_{periodo}.csv")
        cv = compraventas(ruta)
        print(f"{periodo}: {len(cv)} compraventas al 100%", file=sys.stderr)
        partes.append(resumen_distrito(cv, periodo))

    d = pd.concat(partes, ignore_index=True)
    d.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} distritos -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
