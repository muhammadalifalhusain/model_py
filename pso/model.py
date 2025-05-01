import random
import math

class Item:
    def __init__(self, category, name, price, weight, value):
        self.category = category
        self.name = name
        self.price = price
        self.weight = weight
        self.value = value

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
    def __init__(self, items, knapsack):
        self.items = items
        self.knapsack = knapsack
        self.position = [random.randint(0, 1) for _ in items]
        self.velocity = [random.uniform(-1, 1) for _ in items]
        self.best_position = self.position[:]
        self.best_score = self.evaluate()
    def evaluate(self):
        total_weight = 0
        total_price = 0
        total_value = 0

        for i, include in enumerate(self.position):
            if include:
                item = self.items[i]
                total_weight += item.weight
                total_price += item.price
                total_value += item.value

        weight_excess = max(0, total_weight - self.knapsack.capacity)
        price_excess = max(0, total_price - self.knapsack.budget)

        normalized_weight = total_weight / (self.knapsack.capacity or 1)
        normalized_price = total_price / (self.knapsack.budget or 1)
        normalized_value = total_value / (sum(item.value for item in self.items) or 1)

        weight_penalty = math.exp(2 * weight_excess / (self.knapsack.capacity + 1e-6)) 
        price_penalty = math.exp(2 * price_excess / (self.knapsack.budget + 1e-6))   

        if weight_excess > 0 or price_excess > 0:
            return normalized_value / (weight_penalty * price_penalty) 


        weight_utilization = 1 - abs(1 - normalized_weight)
        price_utilization = 1 - abs(1 - normalized_price)

        return normalized_value * (0.5 + 0.5 * weight_utilization * price_utilization)

    def update_velocity(self, global_best_position, w, c1, c2):
        for i in range(len(self.velocity)):
            r1, r2 = random.random(), random.random()
            cognitive = c1 * r1 * (self.best_position[i] - self.position[i])
            social = c2 * r2 * (global_best_position[i] - self.position[i])
            self.velocity[i] = w * self.velocity[i] + cognitive + social
            # Limit velocity to prevent extreme changes
            self.velocity[i] = max(-4, min(4, self.velocity[i]))

    def update_position(self):
        for i in range(len(self.position)):
            sigmoid = 1 / (1 + math.exp(-self.velocity[i]))
            threshold = 0.5 + (random.random() - 0.5) * 0.1  
            self.position[i] = 1 if sigmoid > threshold else 0

def particle_swarm_optimization(items, knapsack, num_particles=50, num_iterations=200, top_n=3):
    feasible_items = [item for item in items 
                     if item.price <= knapsack.budget and item.weight <= knapsack.capacity]
    
    if not feasible_items:
        return []  
    # Inisialisasi partikel
    particles = [Particle(feasible_items, knapsack) for _ in range(num_particles)]
    
    global_best_score = -float('inf')
    global_best_position = None
    
    for particle in particles:
        if particle.best_score > global_best_score:
            global_best_score = particle.best_score
            global_best_position = particle.best_position
    
    # Jika semua partikel invalid, berikan solusi kosong
    if global_best_position is None:
        return []
    
    top_solutions = [(global_best_score, global_best_position[:])]
    
    #  iterasi PSO
    for iteration in range(num_iterations):
        # Adaptive parameters
        w = 0.9 - (0.9 - 0.4) * (iteration / num_iterations)
        c1 = 2.5 - (2.5 - 1.5) * (iteration / num_iterations)
        c2 = 1.5 + (2.5 - 1.5) * (iteration / num_iterations)
        
        for particle in particles:
            if global_best_position is not None:
                particle.update_velocity(global_best_position, w, c1, c2)
                particle.update_position()
                
                score = particle.evaluate()
                if score > particle.best_score:
                    particle.best_score = score
                    particle.best_position = particle.position[:]
                    
                    if score > global_best_score:
                        global_best_score = score
                        global_best_position = particle.best_position[:]
        
        # Update top solutions
        if global_best_position is not None:
            existing = any(all(x == y for x, y in zip(global_best_position, pos)) 
                         for _, pos in top_solutions)
            if not existing:
                top_solutions.append((global_best_score, global_best_position[:]))
                top_solutions.sort(key=lambda x: x[0], reverse=True)
                top_solutions = top_solutions[:top_n]
    
    final_results = []
    for score, position in top_solutions:
        selected_items = [feasible_items[i] for i, bit in enumerate(position) if bit]
        if not selected_items:
            continue
            
        total_price = sum(item.price for item in selected_items)
        total_weight = sum(item.weight for item in selected_items)
        total_value = sum(item.value for item in selected_items)
        
        distance = (abs(total_price - knapsack.budget)/knapsack.budget + 
                   abs(total_weight - knapsack.capacity)/knapsack.capacity)
        
        final_results.append({
            "items": selected_items,
            "total_price": total_price,
            "total_weight": total_weight,
            "total_value": total_value,
            "score": score,
            "distance": distance
        })
    
    final_results.sort(key=lambda x: (x["distance"], -x["total_value"]))
    return [res["items"] for res in final_results[:top_n]]