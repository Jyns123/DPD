import numpy as np
import pandas as pd


df = pd.read_csv("listings_eda.csv")


y_true = df["price_soles"]
y_base = df["baseline_price_soles"]


error_porcentual = (np.abs(y_true - y_base) / y_true) * 100


mdape_calculado = error_porcentual.median()
mape_calculado = error_porcentual.mean()

print("--- VERIFICACIÓN DE MÉTRICAS BASELINE ---")
print(f"MdAPE (Mediana del error porcentual): {mdape_calculado:.2f}%")
print(f"MAPE  (Promedio del error porcentual): {mape_calculado:.2f}%")