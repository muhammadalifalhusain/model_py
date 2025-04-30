# Tambahkan ini dalam file baru `pso/model.py`

import random

class Item:
    def __init__(self, category, name, price, weight):
        self.category = category
        self.name = name
        self.price = price
        self.weight = weight
        self.value = price

class Knapsack:
    def __init__(self, capacity, budget):
        self.capacity = capacity
        self.budget = budget
        self.items = []

    def add_item(self, item):
        if self.can_add_item(item):
            self.items.append(item)

    def can_add_item(self, item):
        return self.total_weight() + item.weight <= self.capacity and self.total_price() + item.price <= self.budget

    def total_weight(self):
        return sum(item.weight for item in self.items)

    def total_price(self):
        return sum(item.price for item in self.items)

    def total_value(self):
        return sum(item.value for item in self.items)

    def is_valid(self):
        return self.total_weight() <= self.capacity and self.total_price() <= self.budget


class Particle:
    def __init__(self, items, knapsacks):
        self.position = [random.choice(range(len(knapsacks) + 1)) for _ in items]
        self.velocity = [random.uniform(-1, 1) for _ in items]
        self.best_position = self.position[:]
        self.best_value = self.evaluate(items, knapsacks)

    def evaluate(self, items, knapsacks):
        solution = [Knapsack(k.capacity, k.budget) for k in knapsacks]
        for i, knapsack_index in enumerate(self.position):
            if knapsack_index < len(knapsacks):
                solution[knapsack_index].add_item(items[i])
        return sum(k.total_value() for k in solution) if all(k.is_valid() for k in solution) else 0

    def update_velocity(self, global_best_position, w, c1, c2):
        for i in range(len(self.velocity)):
            r1, r2 = random.random(), random.random()
            cognitive = c1 * r1 * (self.best_position[i] - self.position[i])
            social = c2 * r2 * (global_best_position[i] - self.position[i])
            self.velocity[i] = 0.7 * self.velocity[i] + cognitive + social

    def update_position(self, num_knapsacks):
        for i in range(len(self.position)):
            self.position[i] = max(0, min(num_knapsacks, round(self.position[i] + self.velocity[i])))

def particle_swarm_optimization(items, knapsacks, num_particles=50, num_iterations=500, top_n=3):
    particles = [Particle(items, knapsacks) for _ in range(num_particles)]
    top_solutions = []

    for _ in range(num_iterations):
        for particle in particles:
            value = particle.evaluate(items, knapsacks)
            if value > particle.best_value:
                particle.best_value = value
                particle.best_position = particle.position[:]

            # Simpan solusi jika termasuk top_n terbaik
            top_solutions.append((particle.best_value, particle.best_position[:]))
            top_solutions = sorted(top_solutions, key=lambda x: x[0], reverse=True)[:top_n]

        for particle in particles:
            particle.update_velocity(top_solutions[0][1], 0.7, 1.4, 1.4)
            particle.update_position(len(knapsacks))

    result_solutions = []
    for _, position in top_solutions:
        solution = [Knapsack(k.capacity, k.budget) for k in knapsacks]
        for i, knapsack_index in enumerate(position):
            if knapsack_index < len(knapsacks):
                solution[knapsack_index].add_item(items[i])
        result_solutions.append(solution)

    return result_solutions  