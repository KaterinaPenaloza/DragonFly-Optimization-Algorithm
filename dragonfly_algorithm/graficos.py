# Genera los gráficos a partir de results.csv, results_random.csv y pareto.csv
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from verificar import leer_resultados, solucion_exacta

os.makedirs("../docs/img", exist_ok=True)
(opt_q, opt_c, opt_x), n_fact, frente_real = solucion_exacta()

# 1) Distribución de resultados finales
da = leer_resultados("results.csv")
azar = leer_resultados("results_random.csv")
bins = range(min(azar + da) - 10, opt_q + 30, 20)
plt.figure(figsize=(7, 4))
plt.hist(azar, bins=bins, color="#ff7f0e", alpha=0.7, label="Búsqueda aleatoria")
plt.hist(da, bins=bins, color="#1f77b4", alpha=0.8, label="Dragonfly")
plt.axvline(opt_q, color="#2ca02c", ls="--", label="óptimo exacto")
plt.xlabel("calidad final de la ejecucion")
plt.ylabel("número de ejecuciones")
plt.title(f"Resultados de {len(da)} ejecuciones (mismo número de evaluaciones)")
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("../docs/img/distribucion_resultados.png", dpi=150)
plt.close()

# 2) Frente de Pareto
with open("pareto.csv") as f:
    filas = list(csv.reader(f))[1:]
plt.figure(figsize=(7, 4.5))
plt.step([c for q, c in frente_real], [q for q, c in frente_real], where="post",
         color="#2ca02c", lw=1.5, label="frente real (enumeración)")
plt.scatter([int(fila[1]) for fila in filas], [int(fila[0]) for fila in filas],
            s=12, color="#1f77b4", label="Dragonfly")
plt.xlabel("costo (minimizar)")
plt.ylabel("calidad (maximizar)")
plt.title("Frente de Pareto Dragonfly")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("../docs/img/frente_pareto.png", dpi=150)
plt.close()
print("Gráficos guardados en ../docs/img/")
