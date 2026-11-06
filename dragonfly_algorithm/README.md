# Implementación de Algoritmo Dragonfly aplicado a un problema con restricciones.

Implementación en Python del **Dragonfly Algorithm (DA)**, un algoritmo bioinspirado basado en el 
comportamiento de enjambre de las libélulas (Mirjalili, 2016), aplicado a un problema de 
asignación de avisos publicitarios con restricciones de presupuesto. 

Este trabajo corresponde a una revisión y optimización del proyecto desarrollado en el curso de *Optimización Computacional*.

---

## Formulación del Problema

La empresa debe decidir la cantidad óptima de avisos a contratar en cinco medios de comunicación: 
televisión tarde ($x_1$), televisión nocturna ($x_2$), diario ($x_3$), revista ($x_4$) y radio ($x_5$), 
sujetos a límites superiores de 15, 10, 25, 4 y 30 unidades respectivamente.

* **Maximizar calidad de exposición ($f_1$):**  
  $$f_1 = 75x_1 + 91x_2 + 50x_3 + 60x_4 + 25x_5$$
* **Minimizar costo total ($f_2$):**  
  $$f_2 = 180x_1 + 310x_2 + 60x_3 + 100x_4 + 15x_5$$
* **Restricciones presupuestarias:**  
  $$180x_1 + 310x_2 \le 3800$$  
  $$60x_3 + 100x_4 \le 2800$$  
  $$60x_3 + 15x_5 \le 3500$$

El problema se aborda bajo dos modalidades: **mono-objetivo** (maximización exclusiva de la calidad) 
y **biobjetivo** (aproximación del frente de Pareto entre calidad y costo). 
Los dominios iniciales de las variables se acotan previamente mediante el algoritmo de consistencia de arcos **AC-3**.

---

## Resultados Experimentales

Dado que el espacio de búsqueda cuenta con un total exacto de **527.930 soluciones factibles**, es posible realizar una enumeración completa para conocer el óptimo global real, el cual corresponde a una **calidad de 3654**, un **costo de 6110** y un vector de asignación $x = [14, 4, 25, 4, 30]$.

### Evaluación Mono-objetivo
Evaluación sobre 500 corridas independientes utilizando 15 agentes y 500 iteraciones, comparadas frente a una búsqueda aleatoria con idéntico presupuesto computacional de evaluaciones:

| Algoritmo | Calidad Media | Mínimo Obtenido | % Óptimo Alcanzado |
| :--- | :---: | :---: | :---: |
| **Dragonfly** | **3638,9** | 3150 | **94,4 %** |
| Búsqueda Aleatoria | 3564,3 | 3477 | 3,6 % |

### Evaluación Biobjetivo (Frente de Pareto)
Evaluación para la aproximación del frente de Pareto frente a los 211 puntos óptimos exactos:

| Algoritmo | Hipervolumen Relativo | Precisión | Cobertura | Puntos |
| :--- | :---: | :---: | :---: | :---: |
| **Dragonfly** | **0,9965** | **73,8 %** | **50,7 %** | 145 |
| Búsqueda Aleatoria | 0,9585 | 0,0 % | 0,0 % | 55 |

La métrica de **precisión** indica el porcentaje de puntos encontrados que pertenecen al frente real de Pareto, mientras que la **cobertura** refleja que el algoritmo es capaz de recuperar más de la mitad de los puntos óptimos exactos en una única ejecución.

---

## Instrucciones de Ejecución

Para replicar los experimentos y la verificación de resultados, ejecute los siguientes comandos en la terminal:

```bash
pip install -r requirements.txt

python dragonfly.py           # Ejecuta una corrida mono-objetivo
python dragonfly.py pareto    # Ejecuta una corrida en modo biobjetivo Pareto
python ejecutar.py            # Ejecuta las 500 corridas y la generación de registros
python verificar.py           # Compara los resultados con la solución exacta y aleatoria
python graficos.py            # Genera las salidas gráficas del análisis
```

---

## Estructura de Archivos

| Archivo | Descripción |
| :--- | :--- |
| `AC3.py` | Módulo encargado de la consistencia de arcos para la reducción de dominios. |
| `dragonfly.py` | Núcleo del algoritmo que define las clases `Problem`, `Agent` y `Swarm`. |
| `ejecutar.py` | Script para la ejecución masiva de múltiples experimentos con semillas controladas. |
| `verificar.py` | Módulo de validación analítica mediante fuerza bruta exacta y búsqueda aleatoria. |
| `graficos.py` | Generador de visualizaciones de rendimiento y distribuciones. |

---

## Referencia Bibliográfica

* Mirjalili, S. (2016). *Dragonfly algorithm: a new meta-heuristic optimization technique for solving single-objective, discrete, and multi-objective problems*. Neural Computing and Applications, 27(4), 1053–1073.