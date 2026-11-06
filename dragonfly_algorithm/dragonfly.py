"""Dragonfly Algorithm (Mirjalili, 2016) adaptado a un problema entero con restricciones.

Cada libélula se mueve según cinco fuerzas calculadas sobre su vecindario:
  separación (S), alineación (A), cohesión (C), atracción al alimento (F) y repulsión al enemigo (E).
    ΔX(t+1) = s·S + a·A + c·C + f·F + e·E + w·ΔX(t)
    X(t+1) = X(t) + ΔX(t+1)
Si una libélula no tiene vecinos se mueve con un vuelo de Lévy (exploración).
"""
import random as rnd
import numpy as np
import csv
import math
import os
import sys

import AC3

def levy(beta=1.5):
    # Salto de Lévy
    sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
             (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    u = rnd.gauss(0, sigma)
    v = rnd.gauss(0, 1)
    return u / max(abs(v), 1e-12) ** (1 / beta)

def stoch_round(valores):
    # Redondeo estocástico
    result = []
    for v in valores:
        base = math.floor(v)
        if rnd.random() < v - base:
            base += 1
        result.append(int(base))
    return np.array(result)

class Problem:
    def __init__(self):
        # Dimensión del problema
        self.dimension = 5

        # Límites encontrados con AC-3
        AC3.ac3(AC3.arcs)
        names = ['x1', 'x2', 'x3', 'x4', 'x5']
        self.lb = np.array([min(AC3.domains[n]) for n in names])
        self.ub = np.array([max(AC3.domains[n]) for n in names])

        # Restricciones de presupuesto
        self.A = [[180, 310, 0, 0, 0],
                  [0, 0, 60, 100, 0],
                  [0, 0, 60, 0, 15]]
        self.b = [3800, 2800, 3500]
        # Normalizar los objetivos en el modo Pareto (valores máximos posibles)
        self.max_f1 = 75 * self.ub[0] + 91 * self.ub[1] + 50 * self.ub[2] + 60 * self.ub[3] + 25 * self.ub[4]
        self.max_f2 = 180 * self.ub[0] + 310 * self.ub[1] + 60 * self.ub[2] + 100 * self.ub[3] + 15 * self.ub[4]

    def eval(self, x):
        # Funcion objetivo 1 Maximizar calidad
        f1 = 75 * x[0] + 91 * x[1] + 50 * x[2] + 60 * x[3] + 25 * x[4]
        # Funcion objetivo 2 Minimizar costo
        f2 = 180 * x[0] + 310 * x[1] + 60 * x[2] + 100 * x[3] + 15 * x[4]
        return [f1, f2]

    # Chequear restricciones
    def check(self, x):
        if np.any(x < self.lb) or np.any(x > self.ub):
            return False
        for row, limit in zip(self.A, self.b):
            if sum(c * v for c, v in zip(row, x)) > limit:
                return False
        return True

    # Arreglar una solución que viola restricciones
    def repair(self, x):
        x = np.array(x)
        while not self.check(x):
            for row, limit in zip(self.A, self.b):
                excess = sum(c * v for c, v in zip(row, x)) - limit
                if excess > 0:
                    candidates = [j for j in range(self.dimension) if row[j] > 0 and x[j] > self.lb[j]]
                    x[rnd.choice(candidates)] -= 1
                    break
        return x

class Agent:
    def __init__(self, problem, x=None):
        self.p = problem
        if x is None:
            self.x = np.array([rnd.randint(int(lo), int(hi)) for lo, hi in zip(problem.lb, problem.ub)])
        else:
            self.x = np.array(x)
        self.fit = self.p.eval(self.x)
        self.step = np.zeros(self.p.dimension)

    def isFeasible(self):
        return self.p.check(self.x)

    def isBetterThan(self, other):
        # Es mejor si no es peor en ninguno de los dos objetivos y es estrictamente mejor en al menos uno (maximizar o minimizar).
        no_better = self.fit[0] >= other.fit[0] and self.fit[1] <= other.fit[1]
        better = self.fit[0] > other.fit[0] or self.fit[1] < other.fit[1]
        return no_better and better

    def update_position(self, new_x):
        self.x = new_x
        self.fit = self.p.eval(self.x)

    def move(self, best, enemy, neighbours, weights):
        # s: separación, a: alineación, c: cohesión, f: atracción al alimento, e: repulsión al enemigo, w: inercia
        s, a, c, f, e, w = weights
        span = self.p.ub - self.p.lb

        if len(neighbours) > 0:
            alignment = np.mean([n.step for n in neighbours], axis=0)
            cohesion = np.mean([n.x for n in neighbours], axis=0) - self.x
            separation = np.sum([self.x - n.x for n in neighbours], axis=0)
            food_attraction = best.x - self.x
            enemy_repulsion = self.x - enemy.x

            self.step = (s * separation + a * alignment + c * cohesion + f * food_attraction + e * enemy_repulsion + w * self.step)
            self.step = np.clip(self.step, -span / 5, span / 5)   # paso máximo
            new_x = self.x + self.step
            
        else:
            self.step = np.zeros(self.p.dimension)
            salto = np.array([levy() for _ in range(self.p.dimension)])
            new_x = self.x + salto * span * 0.05

        new_x = np.clip(new_x, self.p.lb, self.p.ub)
        new_x = stoch_round(new_x)
        new_x = self.p.repair(new_x)
        self.update_position(new_x)

    def __str__(self):
        x_int = [int(val) for val in self.x]
        return f"fit:{self.fit} x:{x_int}"

    def copy(self, other):
        self.x = other.x.copy()
        self.fit = list(other.fit)
        self.step = other.step.copy()


class Swarm:
    def __init__(self, modo="single", seed=None, nAgents=15, maxIter=500):
        # modo single maximiza la calidad (f1)
        # modo pareto aproxima el frente calidad vs costo
        self.modo = modo
        self.maxIter = maxIter
        self.nAgents = nAgents
        self.problem = Problem()
        self.swarm = []
        self.g_best = None                 # mejor solución de toda la corrida
        self.file = []                  # soluciones no dominadas encontradas
        self.lam = 1.0                     # peso entre calidad y costo
        self.historial = []                # mejor calidad por iteración
        self.results_file = "results.csv"
        self.pareto_file = "pareto.csv"
        if seed is not None:
            rnd.seed(seed)

    def better_quality(self, agent):
        return agent.fit[0] - 1e-6 * agent.fit[1]

    def pareto_score(self, agent):
        # Combinación de los dos objetivos (normalizados) según el peso lam de esta iteración
        return self.lam * agent.fit[0] / self.problem.max_f1 - (1 - self.lam) * agent.fit[1] / self.problem.max_f2

    def get_best(self):
        best = max(self.swarm, key=self.better_quality)
        if self.g_best is None:
            self.g_best = Agent(self.problem)
            self.g_best.copy(best)
        elif self.better_quality(best) > self.better_quality(self.g_best):
            self.g_best.copy(best)
        return self.g_best

    def add_to_file(self, agent):
        for m in self.file:
            if m.isBetterThan(agent) or (m.fit[0] == agent.fit[0] and m.fit[1] == agent.fit[1]):
                return   # ya hay una solución igual o mejor
        self.file = [m for m in self.file if not agent.isBetterThan(m)]
        new = Agent(self.problem)
        new.copy(agent)
        self.file.append(new)

    def solve(self):
        self.initRand()
        for t in range(self.maxIter):
            weights = self.update_weights(t)

            if self.modo == "pareto":
                # En cada iteración se prioriza una mezcla distinta de calidad y costo
                self.lam = rnd.random()
                food = max(self.file, key=self.pareto_score)
                enemy = min(self.swarm, key=self.pareto_score)
            else:
                food = self.g_best
                enemy = min(self.swarm, key=self.better_quality)

            # El vecindario crece con las iteraciones
            span = self.problem.ub - self.problem.lb
            radius = span / 4 + span * (2 * t / self.maxIter)

            for agent in self.swarm:
                neighbours = [o for o in self.swarm
                              if o is not agent and np.all(np.abs(o.x - agent.x) <= radius)]
                agent.move(food, enemy, neighbours, weights)
                if self.modo == "pareto":
                    self.add_to_file(agent)

            self.get_best()
            self.historial.append(self.g_best.fit[0])

        self.toFile()

    def initRand(self):
        for i in range(self.nAgents):
            while True:
                a = Agent(self.problem)
                if a.isFeasible():
                    self.swarm.append(a)
                    if self.modo == "pareto":
                        self.add_to_file(a)
                    break
        self.get_best()

    def update_weights(self, t):
        # al inicio se explora, al final solo se va hacia el alimento
        w = 0.9 - 0.5 * t / self.maxIter
        mi_c = max(0.0, 0.1 - 0.2 * t / self.maxIter)
        s = 2 * rnd.random() * mi_c
        a = 2 * rnd.random() * mi_c
        c = 2 * rnd.random() * mi_c
        f = 2 * rnd.random()
        e = mi_c
        return s, a, c, f, e, w

    def toFile(self):
        if self.modo == "pareto":
            self.file.sort(key=lambda ag: ag.fit[1])
            with open(self.pareto_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Calidad", "Costo", "X Values"])
                for ag in self.file:
                    writer.writerow([int(ag.fit[0]), int(ag.fit[1]), [int(v) for v in ag.x]])
            print(f"Frente de Pareto: {len(self.file)} soluciones guardadas en {self.pareto_file}")
            return

        nuevo = not os.path.isfile(self.results_file) or os.path.getsize(self.results_file) == 0
        with open(self.results_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if nuevo:
                writer.writerow(["Best Fit", "X Values"])
            best_fit_str = [int(val) for val in self.g_best.fit]
            best_x_str = [int(val) for val in self.g_best.x]
            writer.writerow([best_fit_str, best_x_str])
            print(f"Best fit: {best_fit_str} with x: {best_x_str}")

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    Swarm(modo).solve()
