import subprocess

# Definir la cantidad de veces a ejecutar
num_executions = 1000

# Ruta al archivo
algoritmo_script = "DragonFly.py"

for i in range(num_executions):
    print(f"Ejecución {i + 1}")
    subprocess.run(["python", algoritmo_script])
