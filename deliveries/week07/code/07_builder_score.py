"""Paso 7: score parcial de confiabilidad de constructoras (REQ-06).

Mientras no haya acceso al CIPIEC (plazos) ni un cruce con sanciones de
INDECOPI, REQ-06 pide construir el score sobre volumen y antiguedad y
declararlo parcial. Con los datos disponibles:
- volumen: proyectos y unidades registrados en el Fondo MIVIVIENDA;
- antiguedad: no disponible, los 747 proyectos traen el mismo periodo de
  publicacion (1/07/2026);
- el ranking de entidades tecnicas (10 empresas, por RUC) no coincide por nombre
  con ningun promotor, porque MIVIVIENDA no publica el RUC del promotor.

El score solo puede usarse para proyectos en planos del Fondo MIVIVIENDA; los
avisos de Urbania no identifican al promotor, asi que alli queda como faltante.
"""
import numpy as np
import pandas as pd

from config import PROCESSED, RAW


def main():
    projects = pd.read_csv(RAW / "proyectos_mivivienda.csv")
    projects["promotor"] = projects.promotor.str.strip().str.upper()
    projects["en_lima"] = projects.departamento.eq("LIMA") & projects.provincia.isin(["LIMA", "CALLAO"])
    builders = projects.groupby("promotor").agg(
        proyectos=("proyecto", "nunique"),
        proyectos_lima=("en_lima", "sum"),
        unidades_disponibles=("unidades_disponibles", "sum"),
        departamentos=("departamento", "nunique"),
        programas=("programa", lambda s: "|".join(sorted(s.unique()))),
        precio_min=("precio_min", "min"),
        precio_max=("precio_max", "max"),
    ).reset_index()
    volume = np.log1p(builders.proyectos)
    units = np.log1p(builders.unidades_disponibles)
    builders["builder_score_partial"] = (0.6 * volume.rank(pct=True) + 0.4 * units.rank(pct=True)).round(3)
    builders["componentes_disponibles"] = "volumen MIVIVIENDA"
    builders["componentes_faltantes"] = "plazos (CIPIEC)|sanciones (INDECOPI)|antiguedad"
    builders["data_partial"] = True
    builders = builders.sort_values(["builder_score_partial", "proyectos"], ascending=False)
    builders.to_csv(PROCESSED / "builder_score_partial.csv", index=False)

    single = (builders.proyectos == 1).mean()
    print(f"{len(builders)} promotores ({int((builders.proyectos_lima > 0).sum())} con proyectos en Lima)")
    print(f"promotores con un solo proyecto: {single:.0%}; valores distintos del score: "
          f"{builders.builder_score_partial.nunique()}")
    print(builders.head(8)[["promotor", "proyectos", "proyectos_lima", "unidades_disponibles",
                            "builder_score_partial"]].to_string(index=False))


if __name__ == "__main__":
    main()
