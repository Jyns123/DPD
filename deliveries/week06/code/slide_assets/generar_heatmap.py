import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Cargar dataset procesado
df = pd.read_csv("listings_eda.csv")

# Selección de variables numéricas de interés
cols = [
    "price_soles",
    "area_m2",
    "price_per_m2",
    "rooms",
    "bathrooms",
    "crime_index_zone",
    "urban_convenience_index",
]
cols_validas = [c for c in cols if c in df.columns]

# Mapeo a nombres ejecutivos para la diapositiva
nombres = {
    "price_soles": "Precio Total (S/)",
    "area_m2": "Área (m²)",
    "price_per_m2": "Precio/m²",
    "rooms": "Dormitorios",
    "bathrooms": "Baños",
    "crime_index_zone": "Índice Crimen",
    "urban_convenience_index": "Conveniencia Urbana",
}

df_subset = df[cols_validas].rename(columns=nombres)
matriz_corr = df_subset.corr()

# Configuración visual
plt.figure(figsize=(8, 6.5), dpi=300)
sns.set_theme(style="white")

sns.heatmap(
    matriz_corr,
    annot=True,
    fmt=".2f",
    cmap="Blues",
    cbar=True,
    square=True,
    linewidths=0.8,
    annot_kws={"size": 9, "weight": "bold"},
)

plt.title(
    "Matriz de Correlación de Variables Clave",
    fontsize=12,
    fontweight="bold",
    pad=12,
)
plt.xticks(rotation=30, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()

plt.savefig("mapa_correlaciones.png", bbox_inches="tight")
print("Imagen generada con éxito: mapa_correlaciones.png")