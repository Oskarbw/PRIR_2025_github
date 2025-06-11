import random
import numpy as np
import matplotlib.pyplot as plt
import constants
import multiprocessing as mp
from model import Bridge
from strength import Strength

class GeneticOptimizer:
    def __init__(self,bridge_template, population_size=20, generations=30, mutation_rate=0.1, 
                 crossover_rate=0.8,processes=4):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.best_fitness_history = []
        self.bridge_template = bridge_template
        self.processes = processes
        
    def create_individual(self):
        return Bridge.random(self.bridge_template)
    
    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]
    
    def fitness_function(self, bridge):
        highest_stress = bridge.calculate_highest_stress()
        mass = bridge.calculate_mass()
        
        if highest_stress > constants.ELASTIC_LIMIT_OF_STEEL:
            # Kara za wytrzymałość poniżej wymaganej
            penalty_multiplier = constants.PENALTY_MULTIPLIER
            penalty = (highest_stress - constants.ELASTIC_LIMIT_OF_STEEL) * penalty_multiplier
            return mass + penalty
        else:
            return mass
          
    def evaluate_population(self, population):         
        fitness_scores = []         
        for bridge in population:             
            fitness = self.fitness_function(bridge)             
            fitness_scores.append(fitness)         
        return fitness_scores

    def evaluate_population_async(self, population):
        with mp.Pool(processes=self.processes) as pool:
            fitness_scores = pool.map(self.fitness_function, population)
        return fitness_scores
    
    def tournament_selection(self, population, fitness_scores, tournament_size=3):
        selected = []
        for _ in range(self.population_size):
            # Wybierz losowo osobników do turnieju
            tournament_indices = random.sample(range(self.population_size), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Znajdź najlepszego w turnieju
            winner_index = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
            selected.append(population[winner_index].clone())
        
        return selected
    
    def crossover(self, parent1, parent2):
        # Jednopunktowe krzyżowanie
        
        crossover_point = random.randint(1, 4)

        parent1_diameters = parent1.diameters.as_list()      
        parent2_diameters = parent1.diameters.as_list()
             
        child1_diameters = parent1_diameters[:crossover_point] + parent2_diameters[crossover_point:]
        child2_diameters = parent2_diameters[:crossover_point] + parent1_diameters[crossover_point:]

        child1 = parent1.clone()
        child2 = parent2.clone()        

        child1.diameters.update_from_list(child1_diameters)
        child2.diameters.update_from_list(child2_diameters)
        
        return child1, child2

    def mutate(self,bridge, mutation_rate=0.1, mutation_range=0.3):
        diameters = bridge.diameters.as_list()
        for i in range(4):
            if random.random() < mutation_rate:
                # Zmień przekrój o losową wartość w zakresie ±30%
                factor = 1.0 + random.uniform(-mutation_range, mutation_range)
                diameters[i] *= factor
                # Ogranicz minimalny i maksymalny przekrój
                diameters[i] = max(20, min(300, diameters[i]))
                
        bridge.diameters.update_from_list(diameters)
        
        return bridge
    
    
    def run(self):
        # Inicjalizacja populacji
        population = self.create_population()
        print(f"Algorytm genetyczny - szukanie najlżejszego mostu spełniającego warunek wytrzymałości {self.bridge_template.min_strength:.2f}")
        print(f"Parametry: populacja={self.population_size}, generacje={self.generations}")
        print(f"Prawdopodobieństwo mutacji={self.mutation_rate}, krzyżowania={self.crossover_rate}")
        print("-" * 60)
        
        for generation in range(self.generations):
            # Ocena populacji
            fitness_scores = self.evaluate_population(population)
            
            # Znajdź najlepszego osobnika
            best_index = fitness_scores.index(min(fitness_scores))
            best_individual = population[best_index]
            best_value = min(fitness_scores)
            
            self.best_fitness_history.append(best_value)
            
            # Wyświetl postęp co 10 generacji
            if generation % 10 == 0:
                print(f"Generacja {generation:3d}")
                print(f"Najlepszy osobnik: ({best_index})")
                print(f"Wartość funkcji: {best_value:.6f}")
            
            # Selekcja
            selected_population = self.tournament_selection(population, fitness_scores)
            
            # Krzyżowanie i mutacja
            new_population = []
            for i in range(0, self.population_size, 2):
                parent1 = selected_population[i]
                parent2 = selected_population[(i + 1) % self.population_size]
                
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population
        
        # Finalna ocena
        fitness_scores = self.evaluate_population(population)
        best_index = fitness_scores.index(min(fitness_scores))
        best_individual = population[best_index]
        best_value = min(fitness_scores)
        
        print("-" * 60)
        print(f"WYNIK KOŃCOWY:")
        print(f"Najlepszy osobnik: {best_index}, {best_individual}")
        print(f"Minimalna wartość funkcji: {best_value}")
        
        return best_individual
    
    def plot_convergence(self):
        """Wykres zbieżności algorytmu"""
        plt.figure(figsize=(10, 6))
        plt.plot(self.best_fitness_history, 'b-', linewidth=2)
        plt.xlabel('Generacja')
        plt.ylabel('Najlepsza wartość funkcji')
        plt.title('Zbieżność algorytmu genetycznego')
        plt.grid(True, alpha=0.3)
        plt.yscale('log')  # Skala logarytmiczna dla lepszej wizualizacji
        plt.show()
