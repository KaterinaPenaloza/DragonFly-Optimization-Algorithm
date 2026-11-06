import os
from dragonfly import Swarm

# Definir la cantidad de veces a ejecutar
num_executions = 500

# Se borra el results.csv anterior para no mezclar corridas de distintos experimentos
if os.path.isfile("results.csv"):
    os.remove("results.csv")

# Ejecuciones
for i in range(num_executions):
    print(f"Ejecución {i + 1}")
    Swarm(seed=i).solve()

# Una corrida en modo Pareto (guarda el frente en pareto.csv)
print("Corrida en modo Pareto")
Swarm("pareto", seed=0).solve()
