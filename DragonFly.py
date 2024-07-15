import random as rnd
import numpy as np
import csv
import os

class Problem:
    def __init__(self):
        # Dimensión del problema
        self.dimension = 5
        # Límites encontrados con AC-3
        self.lb = np.array([0, 0, 0, 0, 0])
        self.ub = np.array([15, 10, 25, 4, 30])

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
        if 180 * x[0] + 310 * x[1] > 3800:
            return False
        if 60 * x[2] + 100 * x[3] > 2800:
            return False
        if 60 * x[2] + 15 * x[4] > 3500:
            return False
        return True

class Agent:
    def __init__(self, problem):
        self.p = problem
        self.x = np.array([rnd.randint(0, domain) for domain in [15, 10, 25, 4, 30]])
        self.fit = self.p.eval(self.x)
        self.step = np.zeros(self.p.dimension)

    def isFeasible(self):
        return self.p.check(self.x)

    def isBetterThan(self, other):
        return self.fit[0] > other.fit[0] and self.fit[1] < other.fit[1]

    def update_position(self, new_x):
        self.x = new_x
        self.fit = self.p.eval(self.x)

    def move(self, best, neighbours, weights):
        s, a, c, f, e = weights
        if len(neighbours) > 0:
            alignment = np.mean([n.step for n in neighbours], axis=0)
            cohesion = (np.mean([n.x for n in neighbours], axis=0) - self.x)
            separation = np.sum([self.x - n.x for n in neighbours], axis=0)
        else:
            alignment = np.zeros(self.p.dimension)
            cohesion = np.zeros(self.p.dimension)
            separation = np.zeros(self.p.dimension)

        food_attraction = best.x - self.x
        enemy_repulsion = np.zeros(self.p.dimension)

        self.step = s * self.step + a * alignment + c * cohesion + e * separation + f * food_attraction - e * enemy_repulsion
        new_x = self.x + self.step
        new_x = np.clip(new_x, self.p.lb, self.p.ub).astype(int)
        self.update_position(new_x)

    def __str__(self):
        x_int = [int(val) for val in self.x]
        return f"fit:{self.fit} x:{x_int}"

    def copy(self, other):
        self.x = other.x[:]

class Swarm:
    def __init__(self):
        self.maxIter = 500
        self.nAgents = 15
        self.problem = Problem()
        self.swarm = []
        self.g_best = None
        self.experiment_count = 1
        self.results_file = "results.csv"
        self.header_written = False

    def get_best(self):
        feasible_agents = [agent for agent in self.swarm if agent.isFeasible()]
        if feasible_agents:
            self.g_best = max(feasible_agents, key=lambda agent: agent.fit[0])
            return self.g_best
        return None

    def solve(self):
        self.initRand()
        with open(self.results_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not os.path.isfile(self.results_file) or os.path.getsize(self.results_file) == 0:
                writer.writerow(["Best Fit", "X Values"])
                self.header_written = True
            for t in range(self.maxIter):
                weights = self.update_weights(t)
                for agent in self.swarm:
                    neighbours = [a for a in self.swarm if a != agent]
                    agent.move(self.g_best, neighbours, weights)
                self.g_best = self.get_best()
                if t == self.maxIter - 1:
                    self.toFile(writer)

    def initRand(self):
        for i in range(self.nAgents):
            while True:
                a = Agent(self.problem)
                if a.isFeasible():
                    self.swarm.append(a)
                    break
        self.g_best = self.get_best()

    def update_weights(self, t):
        w_max = 0.9
        w_min = 0.2
        s = w_max - ((w_max - w_min) * t / self.maxIter)
        a = 0.001
        c = 0.001
        f = 0.001
        e = 0.001
        return s, a, c, f, e

    def toFile(self, csv_writer):
        if self.g_best:
            best_fit_str = [int(val) for val in self.g_best.fit]
            best_x_str = [int(val) for val in self.g_best.x]
            csv_writer.writerow([best_fit_str, best_x_str])
            print(f"Best fit: {best_fit_str} with x: {best_x_str}")
            self.experiment_count += 1
        else:
            csv_writer.writerow([f"No feasible solution found", "N/A"])
            print(f"Experiment {self.experiment_count}: No feasible solution found")

# Ejecutar la solución
try:
    Swarm().solve()
except Exception as e:
    print(f"{e} \nCaused by {e.__cause__}")
