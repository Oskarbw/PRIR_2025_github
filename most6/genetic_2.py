import random
import numpy as np
import matplotlib.pyplot as plt
from model import SimpleBridge

class GeneticOptimiser:
    def __init__(self,sample_bridge, min_strength, population_size=20, generations=30, mutation_rate=0.1, 
                 crossover_rate=0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.best_fitness_history = []
        self.sample_bridge = sample_bridge
        self.min_strength = min_strength
        
    def create_individual(self):

        #Trzeba zrobic plik ze stalymi i tam wrzucic
        TOP_CHORD_LOWER_BOUND = 20
        TOP_CHORD_UPPER_BOUND = 300
        BOTTOM_CHORD_LOWER_BOUND = 20
        BOTTOM_CHORD_UPPER_BOUND = 300
        POST_LOWER_BOUND = 20
        POST_UPPER_BOUND = 300
        DIAGONAL_LOWER_BOUND = 20
        DIAGONAL_UPPER_BOUND = 300
        
        self.members.top_chord_diameter = random.uniform(TOP_CHORD_LOWER_BOUND, TOP_CHORD_UPPER_BOUND)
        self.members.bottom_chord_diameter = random.uniform(BOTTOM_CHORD_LOWER_BOUND, BOTTOM_CHORD_UPPER_BOUND)
        self.members.post_diameter = random.uniform(POST_LOWER_BOUND, POST_UPPER_BOUND)
        self.members.diagonal_diameter = random.uniform(DIAGONAL_LOWER_BOUND, DIAGONAL_UPPER_BOUND)

        random_bridge = SimpleBridge(length=self.sample_bridge.length, num_segments=self.sample_bridge.num_segments, members=self.members)  

        return random_bridge
    
    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]
    
    def fitness_function(self, bridge):
        strength = bridge.calculate_strength()
        mass = bridge.calculate_mass()
        
        if strength < self.min_strength:
            # Kara za wytrzymałość poniżej wymaganej
            # Trzeba sprawdzic jaka wartosc kary najlepiej dziala
            penalty_multiplier = 10000
            penalty = (self.min_strength - strength) * penalty_multiplier
            return mass + penalty
        else:
            return mass    

    def evaluate_population(self, population):
        fitness_scores = []
        for bridge in population:
            fitness = self.fitness_function(bridge)
            fitness_scores.append(fitness)
        return fitness_scores
    
    def tournament_selection(self, population, fitness_scores, tournament_size=3):
        selected = []
        for _ in range(self.population_size):
            # Wybierz losowo osobników do turnieju
            tournament_indices = random.sample(range(self.population_size), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Znajdź najlepszego w turnieju
            winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            selected.append(population[winner_index].copy())
        
        return selected
    
    def crossover(parent1, parent2):
        """Krzyżowanie dwóch mostów."""
        child1 = parent1.clone()
        child2 = parent2.clone()
        

        # Jedno punktowe krzyżowanie
        crossover_point = random.randint(1, 4)
        
        child1.diameters[crossover_point:] = parent2.diameters[crossover_point:]
        child2.diameters[:crossover_point] = parent1.diameters[:crossover_point]
        
        return child1, child2

    def mutation(bridge, mutation_rate=0.1, mutation_range=0.3):
        """Mutacja mostu."""
        for i in range(4):
            if random.random() < mutation_rate:
                # Zmień przekrój o losową wartość w zakresie ±30%
                factor = 1.0 + random.uniform(-mutation_range, mutation_range)
                bridge.sections[i] *= factor
                # Ogranicz minimalny i maksymalny przekrój
                bridge.sections[i] = max(20, min(300, bridge.sections[i]))
        
        return bridge
    
    
    def run(self):
        # Inicjalizacja populacji
        population = self.create_population()
        
        #print("Algorytm genetyczny - szukanie minimum funkcji f(x,y) = x² + y²")
        #print(f"Parametry: populacja={self.population_size}, generacje={self.generations}")
        #print(f"Prawdopodobieństwo mutacji={self.mutation_rate}, krzyżowania={self.crossover_rate}")
        #print("-" * 60)
        
        for generation in range(self.generations):
            # Ocena populacji
            fitness_scores = self.evaluate_population(population)
            
            # Znajdź najlepszego osobnika
            best_index = fitness_scores.index(max(fitness_scores))
            best_individual = population[best_index]
            best_value = self.objective_function(best_individual[0], best_individual[1])
            
            self.best_fitness_history.append(best_value)
            
            # Wyświetl postęp co 10 generacji
            if generation % 10 == 0:
                print(f"Generacja {generation:3d}: Najlepszy osobnik: ({best_individual[0]:.4f}, {best_individual[1]:.4f}), "
                      f"Wartość funkcji: {best_value:.6f}")
            
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
        best_index = fitness_scores.index(max(fitness_scores))
        best_individual = population[best_index]
        best_value = self.objective_function(best_individual[0], best_individual[1])
        
        print("-" * 60)
        print(f"WYNIK KOŃCOWY:")
        print(f"Najlepszy osobnik: x = {best_individual[0]:.6f}, y = {best_individual[1]:.6f}")
        print(f"Minimalna wartość funkcji: {best_value:.8f}")
        print(f"Teoretyczne minimum: (0, 0) z wartością 0")
        print(f"Błąd: {abs(best_value):.8f}")
        
        return best_individual, best_value
    
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
