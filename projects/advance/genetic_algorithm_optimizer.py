"""
Genetic Algorithm Optimizer

Features:
- Optimization using genetic algorithms
- Modular design
- CLI interface
- Error handling
"""
import random
import sys
import numpy as np

class Individual:
    def __init__(self, genes):
        self.genes = genes
        self.fitness = None

class GeneticAlgorithm:
    def __init__(self, pop_size, gene_length, fitness_func):
        self.pop_size = pop_size
        self.gene_length = gene_length
        self.fitness_func = fitness_func
        self.population = [Individual(np.random.rand(gene_length)) for _ in range(pop_size)]

    def evaluate(self):
        for ind in self.population:
            ind.fitness = self.fitness_func(ind.genes)

    def select(self):
        sorted_pop = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        return sorted_pop[:self.pop_size//2]

    def crossover(self, parent1, parent2):
        point = random.randint(1, self.gene_length-1)
        child_genes = np.concatenate([parent1.genes[:point], parent2.genes[point:]])
        return Individual(child_genes)

    def mutate(self, individual, rate=0.1):
        for i in range(self.gene_length):
            if random.random() < rate:
                individual.genes[i] += np.random.normal()

    def run(self, generations=100):
        for gen in range(generations):
            self.evaluate()
            selected = self.select()
            children = []
            while len(children) < self.pop_size:
                p1, p2 = random.sample(selected, 2)
                child = self.crossover(p1, p2)
                self.mutate(child)
                children.append(child)
            self.population = children
            best = max(self.population, key=lambda x: x.fitness)
            print(f"Gen {gen}: Best fitness = {best.fitness}")
        return best

class CLI:
    @staticmethod
    def run():
        def fitness(x):
            return -np.sum((x-0.5)**2)
        ga = GeneticAlgorithm(50, 10, fitness)
        print("Running Genetic Algorithm Optimizer...")
        best = ga.run(50)
        print(f"Best solution: {best.genes}, Fitness: {best.fitness}")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
