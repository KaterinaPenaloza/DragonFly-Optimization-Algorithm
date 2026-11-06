# Compara los resultados del algoritmo con la solución exacta (enumerando todas las combinaciones)
# y con una búsqueda aleatoria que usa el mismo número de evaluaciones.
import ast
import csv
import os
import random as rnd

import numpy as np

from dragonfly import Problem, Swarm

REF_COSTO = 8150   # costo máximo posible (referencia para el hipervolumen)


def frente_de_pareto(puntos):
    """puntos: lista de (calidad, costo). Devuelve los no dominados (max calidad, min costo)."""
    frente = []
    mejor_calidad = -1
    for calidad, costo in sorted(set(puntos), key=lambda p: (p[1], -p[0])):
        if calidad > mejor_calidad:
            frente.append((calidad, costo))
            mejor_calidad = calidad
    return frente


def hipervolumen(frente):
    frente = sorted(frente, key=lambda p: p[1])
    total = 0
    for i, (calidad, costo) in enumerate(frente):
        siguiente = frente[i + 1][1] if i + 1 < len(frente) else REF_COSTO
        total += (siguiente - costo) * calidad
    return total


def solucion_exacta():
    """Recorre todas las combinaciones factibles. Devuelve óptimo de calidad y frente de Pareto real."""
    mejor = (-1, 0, None)
    n_factibles = 0
    puntos = {}
    for x1 in range(16):
        for x2 in range(11):
            if 180 * x1 + 310 * x2 > 3800:
                continue
            for x3 in range(26):
                for x4 in range(5):
                    if 60 * x3 + 100 * x4 > 2800:
                        continue
                    for x5 in range(31):
                        if 60 * x3 + 15 * x5 > 3500:
                            continue
                        n_factibles += 1
                        f1 = 75 * x1 + 91 * x2 + 50 * x3 + 60 * x4 + 25 * x5
                        f2 = 180 * x1 + 310 * x2 + 60 * x3 + 100 * x4 + 15 * x5
                        if f1 > mejor[0] or (f1 == mejor[0] and f2 < mejor[1]):
                            mejor = (f1, f2, [x1, x2, x3, x4, x5])
                        if f1 > puntos.get(f2, -1):
                            puntos[f2] = f1
    frente = frente_de_pareto([(q, c) for c, q in puntos.items()])
    return mejor, n_factibles, frente


def busqueda_aleatoria(problem, n_evals):
    """Soluciones al azar (reparadas). Devuelve la mejor calidad y los puntos (calidad, costo)."""
    mejor = -1
    puntos = []
    for _ in range(n_evals):
        x = np.array([rnd.randint(int(lo), int(hi)) for lo, hi in zip(problem.lb, problem.ub)])
        x = problem.repair(x)
        f1, f2 = problem.eval(x)
        mejor = max(mejor, f1)
        puntos.append((int(f1), int(f2)))
    return mejor, puntos


def leer_resultados(archivo):
    with open(archivo) as f:
        filas = list(csv.reader(f))[1:]
    return [ast.literal_eval(fila[0])[0] for fila in filas]


if __name__ == "__main__":
    (opt_q, opt_c, opt_x), n_fact, frente_real = solucion_exacta()
    print(f"Solución exacta: calidad={opt_q} costo={opt_c} x={opt_x}")
    print(f"({n_fact:,} soluciones factibles; el frente de Pareto real tiene {len(frente_real)} puntos)\n")

    if os.path.isfile("results.csv"):
        calidades = leer_resultados("results.csv")
        n = len(calidades)
        problem = Problem()
        n_evals = 15 * 501
        rnd.seed(12345)
        azar = []
        for _ in range(n):
            azar.append(busqueda_aleatoria(problem, n_evals)[0])
        with open("results_random.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Best Fit"])
            for q in azar:
                w.writerow([[int(q)]])

        print(f"== Mono-objetivo: {n} corridas de cada uno ==")
        print(f"{'algoritmo':<20}{'media':>9}{'mínimo':>9}{'% óptimo':>10}")
        for nombre, datos in (("Dragonfly", calidades), ("Búsqueda aleatoria", azar)):
            print(f"{nombre:<20}{sum(datos) / n:>9.1f}{min(datos):>9}{100 * sum(d == opt_q for d in datos) / n:>10.1f}")
    else:
        print("No hay results.csv: ejecuta primero ejecutar.py")

    if os.path.isfile("pareto.csv"):
        with open("pareto.csv") as f:
            filas = list(csv.reader(f))[1:]
        encontrados = [(int(fila[0]), int(fila[1])) for fila in filas]
        real = set(frente_real)
        _, puntos_azar = busqueda_aleatoria(Problem(), 15 * 501)
        frente_azar = frente_de_pareto(puntos_azar)
        print("\n== Biobjetivo: frente de Pareto ==")
        print(f"{'algoritmo':<20}{'hipervol.':>10}{'precisión':>11}{'cobertura':>11}{'puntos':>8}")
        for nombre, pts in (("Dragonfly", encontrados), ("Búsqueda aleatoria", frente_azar)):
            en_frente = sum(p in real for p in pts)
            print(f"{nombre:<20}{hipervolumen(pts) / hipervolumen(frente_real):>10.4f}"
                  f"{en_frente / len(pts):>11.3f}{en_frente / len(real):>11.3f}{len(pts):>8}")
        print("(hipervolumen relativo al frente real; precisión = % de puntos que están en el frente real; cobertura = % del frente real encontrado)")
