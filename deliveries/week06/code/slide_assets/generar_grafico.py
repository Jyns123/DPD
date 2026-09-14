import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


df = pd.read_csv("listings_eda.csv")


sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)


precios_miles = df["price_soles"] / 1000
mediana_precio = precios_miles.median()

sns.histplot(
    precios_miles,
    kde=True,
    ax=axes[0],
    color="#1d4ed8",
    bins=40,
    alpha=0.6,
    edgecolor="white",
)
axes[0].axvline(
    mediana_precio,
    color="#b91c1c",
    linestyle="--",
    linewidth=2,
    label=f"Mediana: S/ {mediana_precio:.1f}k",
)
axes[0].set_title(
    "Distribución de Precios (Sesgo a la Derecha)",
    fontsize=12,
    fontweight="bold",
    pad=10,
)
axes[0].set_xlabel("Precio de Oferta (Miles de Soles - PEN)", fontsize=10)
axes[0].set_ylabel("Cantidad de Anuncios", fontsize=10)
axes[0].set_xlim(0, 3000)
axes[0].legend(loc="upper right")

# Gráfico 2: Distribución del Área Construida (m²)
area_data = df["area_m2"]
mediana_area = area_data.median()

sns.histplot(
    area_data,
    kde=True,
    ax=axes[1],
    color="#0284c7",
    bins=40,
    alpha=0.6,
    edgecolor="white",
)
axes[1].axvline(
    mediana_area,
    color="#b91c1c",
    linestyle="--",
    linewidth=2,
    label=f"Mediana: {mediana_area:.1f} m²",
)
axes[1].set_title(
    "Distribución del Área (Sesgo a la Derecha)",
    fontsize=12,
    fontweight="bold",
    pad=10,
)
axes[1].set_xlabel("Área del Inmueble (m²)", fontsize=10)
axes[1].set_ylabel("Cantidad de Anuncios", fontsize=10)
axes[1].set_xlim(0, 350)
axes[1].legend(loc="upper right")

plt.tight_layout()
output_img = "eda_distribucion_precio_area.png"
plt.savefig(output_img, bbox_inches="tight")
print(f"Imagen generada con éxito como: {output_img}")
plt.show()