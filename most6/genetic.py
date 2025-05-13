import random
import numpy as np
import multiprocessing as mp
from model import SimpleBridge
import time

def evaluate_bridge(bridge):
    """Ocenia pojedynczy most."""
    return bridge.evaluate()

def evaluate_chunk(bridges):
    """Ocenia całą grupę mostów."""
    return [evaluate_bridge(bridge) for bridge in bridges]

def evaluate_population_parallel(population, num_processes=None):
    """Równoległa ocena populacji."""
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    # Podziel populację na części
    chunk_size = max(1, len(population) // num_processes)
    chunks = [population[i:i+chunk_size] for i in range(0, len(population), chunk_size)]
    
    # Równoległa ocena
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(evaluate_chunk, chunks)
    
    # Złącz wyniki
    fitness_values = []
    for chunk_result in results:
        fitness_values.extend(chunk_result)
    
    return fitness_values

def tournament_selection(population, fitness_values, tournament_size=3):
    """Selekcja turniejowa."""
    indices = np.random.randint(0, len(population), tournament_size)
    tournament_fitness = [fitness_values[i] for i in indices]
    winner_idx = indices[np.argmax(tournament_fitness)]
    return population[winner_idx]

def crossover(parent1, parent2):
    """Krzyżowanie dwóch mostów."""
    child1 = parent1.clone()
    child2 = parent2.clone()
    
    # Jedno punktowe krzyżowanie
    crossover_point = random.randint(1, len(parent1.sections) - 1)
    
    child1.sections[crossover_point:] = parent2.sections[crossover_point:]
    child2.sections[:crossover_point] = parent1.sections[:crossover_point]
    
    return child1, child2

def mutation(bridge, mutation_rate=0.1, mutation_range=0.3):
    """Mutacja mostu."""
    for i in range(len(bridge.sections)):
        if random.random() < mutation_rate:
            # Zmień przekrój o losową wartość w zakresie ±30%
            factor = 1.0 + random.uniform(-mutation_range, mutation_range)
            bridge.sections[i] *= factor
            # Ogranicz minimalny i maksymalny przekrój
            bridge.sections[i] = max(0.001, min(0.05, bridge.sections[i]))
    
    return bridge

def apply_crossover_mutation(args):
    """Funkcja do zrównoleglonego krzyżowania i mutacji par rodziców."""
    parent1, parent2, crossover_rate, mutation_rate = args
    
    # Krzyżowanie
    if random.random() < crossover_rate:
        child1, child2 = crossover(parent1, parent2)
    else:
        child1, child2 = parent1.clone(), parent2.clone()
    
    # Mutacja
    child1 = mutation(child1, mutation_rate)
    child2 = mutation(child2, mutation_rate)
    
    return child1, child2

def parallel_crossover_mutation(parent_pairs, crossover_rate, mutation_rate, num_processes=None):
    """Równoległe krzyżowanie i mutacja."""
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    # Przygotuj argumenty dla każdej pary rodziców
    args = [(parent1, parent2, crossover_rate, mutation_rate) for parent1, parent2 in parent_pairs]
    
    # Wykonaj równoległe krzyżowanie i mutację
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(apply_crossover_mutation, args)
    
    # Złącz wyniki
    children = []
    for child1, child2 in results:
        children.append(child1)
        children.append(child2)
    
    return children

def evolve_island(args):
    """Funkcja do ewolucji pojedynczej wyspy."""
    island_population, fitness_values, num_offspring, crossover_rate, mutation_rate, tournament_size = args
    
    # Wybierz najlepszego osobnika (elityzm)
    best_idx = np.argmax(fitness_values)
    best_individual = island_population[best_idx].clone()
    new_population = [best_individual]
    
    # Generuj pary rodziców
    parent_pairs = []
    while len(parent_pairs) * 2 < num_offspring:
        parent1 = tournament_selection(island_population, fitness_values, tournament_size)
        parent2 = tournament_selection(island_population, fitness_values, tournament_size)
        parent_pairs.append((parent1, parent2))
    
    # Równoległe krzyżowanie i mutacja w obrębie wyspy
    children = parallel_crossover_mutation(parent_pairs, crossover_rate, mutation_rate, num_processes=1)
    
    # Dodaj dzieci do populacji
    new_population.extend(children[:num_offspring])
    
    return new_population

class IslandGeneticOptimizer:
    """Optymalizator genetyczny z modelem wyspowym."""
    
    def __init__(self, population_size=100, num_islands=4, bridge_template=None, 
                 mutation_rate=0.1, crossover_rate=0.8, migration_interval=5, migration_rate=0.1):
        self.population_size = population_size
        self.num_islands = num_islands
        self.island_size = population_size // num_islands
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.migration_interval = migration_interval
        self.migration_rate = migration_rate
        
        if bridge_template is None:
            bridge_template = SimpleBridge()
        
        # Inicjalizacja wysp (populacji)
        self.islands = []
        for i in range(num_islands):
            island = []
            for _ in range(self.island_size):
                bridge = bridge_template.clone()
                # Losowe przekroje
                bridge.sections = [random.uniform(0.005, 0.015) for _ in range(5)]
                island.append(bridge)
            self.islands.append(island)
        
        self.fitness_values = [[0] * self.island_size for _ in range(num_islands)]
        
        self.best_bridge = None
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
    
    def migrate(self):
        """Migracja osobników między wyspami."""
        # Liczba osobników do migracji z każdej wyspy
        migrants_per_island = max(1, int(self.island_size * self.migration_rate))
        
        # Dla każdej wyspy wybierz najlepszych migrantów
        migrants = []
        for i in range(self.num_islands):
            island = self.islands[i]
            fitness = self.fitness_values[i]
            
            # Wybierz indeksy najlepszych osobników
            indices = np.argsort(fitness)[-migrants_per_island:]
            
            # Dodaj najlepszych do listy migrantów
            migrants.append([island[idx].clone() for idx in indices])
        
        # Dla każdej wyspy zastąp najgorszych osobników migrantami z innych wysp
        for i in range(self.num_islands):
            island = self.islands[i]
            fitness = self.fitness_values[i]
            
            # Wybierz indeksy najgorszych osobników
            worst_indices = np.argsort(fitness)[:migrants_per_island]
            
            # Zastąp najgorszych osobników migrantami z następnej wyspy
            next_island = (i + 1) % self.num_islands
            for j, idx in enumerate(worst_indices):
                island[idx] = migrants[next_island][j]
    
    def evolve(self, generations=20, num_processes=None):
        """Ewolucja populacji z modelem wyspowym."""
        for gen in range(generations):
            self.generation = gen + 1
            
            # Ocena populacji na wszystkich wyspach równolegle
            all_fitness = []
            for i in range(self.num_islands):
                self.fitness_values[i] = evaluate_population_parallel(self.islands[i], num_processes)
                all_fitness.extend(self.fitness_values[i])
            
            # Zapisanie historii
            best_fitness = max(all_fitness)
            avg_fitness = np.mean(all_fitness)
            
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            # Znajdź najlepszy most globalnie
            best_island_idx = -1
            best_individual_idx = -1
            for i in range(self.num_islands):
                island_best_idx = np.argmax(self.fitness_values[i])
                if best_island_idx == -1 or self.fitness_values[i][island_best_idx] > self.fitness_values[best_island_idx][best_individual_idx]:
                    best_island_idx = i
                    best_individual_idx = island_best_idx
            
            # Zachowanie najlepszego mostu
            best_bridge = self.islands[best_island_idx][best_individual_idx]
            if self.best_bridge is None or best_bridge.fitness > self.best_bridge.fitness:
                self.best_bridge = best_bridge.clone()
                # Upewniamy się, że wszystkie wartości są obliczone
                self.best_bridge.evaluate()
            
            # Informacja o postępie
            print(f"Generacja {gen+1}/{generations}: Najlepszy fitness = {best_fitness:.6f}")
            
            # Zatrzymanie, jeśli to ostatnia generacja
            if gen == generations - 1:
                break
            
            # Migracja między wyspami
            if (gen + 1) % self.migration_interval == 0:
                self.migrate()
            
            # Równoległa ewolucja każdej wyspy
            args = []
            for i in range(self.num_islands):
                args.append((
                    self.islands[i], 
                    self.fitness_values[i], 
                    self.island_size - 1,  # -1 bo zachowujemy najlepszego (elityzm)
                    self.crossover_rate, 
                    self.mutation_rate, 
                    3  # tournament_size
                ))
            
            # Ewolucja wysp równolegle
            with mp.Pool(processes=min(self.num_islands, mp.cpu_count())) as pool:
                new_islands = pool.map(evolve_island, args)
            
            # Aktualizacja wysp
            self.islands = new_islands
        
        # Upewnij się, że najlepszy most ma obliczone wszystkie wartości przed zwróceniem
        if self.best_bridge:
            self.best_bridge.evaluate()
        
        return self.best_bridge

class GeneticOptimizer:
    """Optymalizator genetyczny dla mostów."""
    
    def __init__(self, population_size=20, bridge_template=None, mutation_rate=0.1, crossover_rate=0.8):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        if bridge_template is None:
            bridge_template = SimpleBridge()
        
        # Inicjalizacja populacji
        self.population = []
        for _ in range(population_size):
            bridge = bridge_template.clone()
            # Losowe przekroje
            bridge.sections = [random.uniform(0.005, 0.015) for _ in range(5)]
            self.population.append(bridge)
        
        self.fitness_values = [0] * population_size
        self.best_bridge = None
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
    
    def evolve(self, generations=20, num_processes=None):
        """Ewolucja populacji z wszystkimi trzema metodami zrównoleglenia."""
        for gen in range(generations):
            self.generation = gen + 1
            
            # 1. Równoległa ocena populacji
            self.fitness_values = evaluate_population_parallel(self.population, num_processes)
            
            # Zapisanie historii
            best_idx = np.argmax(self.fitness_values)
            best_fitness = self.fitness_values[best_idx]
            avg_fitness = np.mean(self.fitness_values)
            
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            # Zachowanie najlepszego mostu
            if self.best_bridge is None or best_fitness > self.best_bridge.fitness:
                self.best_bridge = self.population[best_idx].clone()
                # Upewniamy się, że wszystkie wartości są obliczone
                self.best_bridge.evaluate()
            
            # Informacja o postępie
            print(f"Generacja {gen+1}/{generations}: Najlepszy fitness = {best_fitness:.6f}")
            
            # Zatrzymanie, jeśli to ostatnia generacja
            if gen == generations - 1:
                break
            
            # 2. Równoległe krzyżowanie i mutacja
            
            # Tworzenie nowej populacji
            new_population = [self.population[best_idx].clone()]  # Elityzm
            
            # Przygotowanie par rodziców
            parent_pairs = []
            while len(parent_pairs) * 2 + 1 < self.population_size:  # +1 bo już dodaliśmy elitę
                parent1 = tournament_selection(self.population, self.fitness_values)
                parent2 = tournament_selection(self.population, self.fitness_values)
                parent_pairs.append((parent1, parent2))
            
            # Równoległe krzyżowanie i mutacja
            children = parallel_crossover_mutation(
                parent_pairs,
                self.crossover_rate,
                self.mutation_rate,
                num_processes
            )
            
            # Dodaj dzieci do nowej populacji
            new_population.extend(children[:self.population_size - 1])  # -1 bo już dodaliśmy elitę
            
            # Zastąpienie populacji
            self.population = new_population
        
        # Upewnij się, że najlepszy most ma obliczone wszystkie wartości przed zwróceniem
        if self.best_bridge:
            self.best_bridge.evaluate()
        
        return self.best_bridge


# Funkcja do testowania i porównywania wydajności różnych strategii zrównoleglenia
def benchmark(bridge_template, test_cases, num_runs=3):
    """
    Benchmark różnych strategii zrównoleglenia dla algorytmu genetycznego.
    
    Args:
        bridge_template: Szablon mostu do klonowania
        test_cases: Lista przypadków testowych (populacja, generacje, strategia, procesy)
        num_runs: Ile razy uruchomić każdy test
    
    Returns:
        Słownik z wynikami dla każdego przypadku testowego
    """
    results = {}
    
    for case in test_cases:
        name, pop_size, generations, strategy, processes = case
        print(f"\nTestowanie: {name}")
        
        times = []
        fitness = []
        
        for run in range(num_runs):
            print(f"  Przebieg {run+1}/{num_runs}")
            
            if strategy == "basic":
                optimizer = GeneticOptimizer(
                    population_size=pop_size,
                    bridge_template=bridge_template,
                    mutation_rate=0.1,
                    crossover_rate=0.8
                )
                
                # Wyłącz zrównoleglenie krzyżowania/mutacji nadpisując metodę
                optimizer.evolve = lambda generations, num_processes: evolve_original(
                    optimizer, generations, num_processes
                )
                
            elif strategy == "parallel_eval":
                optimizer = GeneticOptimizer(
                    population_size=pop_size,
                    bridge_template=bridge_template,
                    mutation_rate=0.1,
                    crossover_rate=0.8
                )
                
                # Używamy oryginalnej implementacji z równoległą oceną
                
            elif strategy == "full_parallel":
                optimizer = GeneticOptimizer(
                    population_size=pop_size,
                    bridge_template=bridge_template,
                    mutation_rate=0.1,
                    crossover_rate=0.8
                )
                
                # Używamy pełnego zrównoleglenia (ocena + krzyżowanie/mutacja)
                
            elif strategy == "island":
                optimizer = IslandGeneticOptimizer(
                    population_size=pop_size,
                    num_islands=4,
                    bridge_template=bridge_template,
                    mutation_rate=0.1,
                    crossover_rate=0.8,
                    migration_interval=5,
                    migration_rate=0.1
                )
            
            start_time = time.time()
            best_bridge = optimizer.evolve(generations, processes)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            fitness.append(best_bridge.fitness)
        
        # Zbierz wyniki
        results[name] = {
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "avg_fitness": sum(fitness) / len(fitness),
            "best_fitness": max(fitness)
        }
        
        print(f"  Średni czas: {results[name]['avg_time']:.2f}s")
        print(f"  Średni fitness: {results[name]['avg_fitness']:.6f}")
    
    return results


# Oryginalna metoda evolve dla porównania wydajności
def evolve_original(self, generations=20, num_processes=None):
    """Oryginalna ewolucja populacji."""
    for gen in range(generations):
        self.generation = gen + 1
        
        # Równoległa ocena populacji
        self.fitness_values = evaluate_population_parallel(self.population, num_processes)
        
        # Zapisanie historii
        best_idx = np.argmax(self.fitness_values)
        best_fitness = self.fitness_values[best_idx]
        avg_fitness = np.mean(self.fitness_values)
        
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)
        
        # Zachowanie najlepszego mostu
        if self.best_bridge is None or best_fitness > self.best_bridge.fitness:
            self.best_bridge = self.population[best_idx].clone()
            # Upewniamy się, że wszystkie wartości są obliczone
            self.best_bridge.evaluate()
        
        # Informacja o postępie
        print(f"Generacja {gen+1}/{generations}: Najlepszy fitness = {best_fitness:.6f}")
        
        # Zatrzymanie, jeśli to ostatnia generacja
        if gen == generations - 1:
            break
        
        # Tworzenie nowej populacji
        new_population = [self.population[best_idx].clone()]  # Elityzm
        
        while len(new_population) < self.population_size:
            # Selekcja
            parent1 = tournament_selection(self.population, self.fitness_values)
            parent2 = tournament_selection(self.population, self.fitness_values)
            
            # Krzyżowanie
            if random.random() < self.crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.clone(), parent2.clone()
            
            # Mutacja
            child1 = mutation(child1, self.mutation_rate)
            child2 = mutation(child2, self.mutation_rate)
            
            # Dodanie do nowej populacji
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        
        # Zastąpienie populacji
        self.population = new_population
    
    # Upewnij się, że najlepszy most ma obliczone wszystkie wartości przed zwróceniem
    if self.best_bridge:
        self.best_bridge.evaluate()
    
    return self.best_bridge