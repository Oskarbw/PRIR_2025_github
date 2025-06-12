import random
import multiprocessing as mp

from model import Bridge
import constants

class GeneticOptimizer:
    def __init__(self,bridge_template,
                 population_size=constants.DEFAULT_POPULATION_SIZE,
                 generations=constants.DEFAULT_GENERATIONS,
                 mutation_rate=constants.DEFAULT_MUTATION_RATE,
                 processes=constants.DEFAULT_PROCESSES):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

        self.best_fitness_history = []
        self.bridge_template = bridge_template
        self.processes = processes

    def run(self):
        population = self._create_population()
        print(f"Algorytm genetyczny - szukanie najlżejszego mostu spełniającego warunek wytrzymałości {self.bridge_template.min_strength:.2f}")
        print(f"Parametry: populacja={self.population_size}, generacje={self.generations}")
        print(f"Prawdopodobieństwo mutacji={self.mutation_rate}")
        print("------------------------------------------------")

        for generation in range(self.generations):
            fitness_scores = self._evaluate_population_multiprocessing(population)

            best_index = fitness_scores.index(min(fitness_scores))
            best_individual = population[best_index]
            best_value = min(fitness_scores)

            self.best_fitness_history.append(best_value)

            if generation % constants.GENERATION_OUTPUT_STEP == 0:
                print(f"Generacja {generation:3d}")
                print(f"Najlepszy osobnik: ({best_index})")
                print(f"Wartość funkcji: {best_value:.6f}")

            selected_population = self._tournament_selection(population, fitness_scores)

            new_population = []
            for i in range(0, self.population_size, constants.CROSSOVER_SIZE):
                parent1 = selected_population[i]
                parent2 = selected_population[(i + 1) % self.population_size]

                child1, child2 = self._crossover(parent1, parent2)
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)

                new_population.extend([child1, child2])

            population = new_population

        fitness_scores = self._evaluate_population(population)
        best_index = fitness_scores.index(min(fitness_scores))
        best_individual = population[best_index]
        best_value = min(fitness_scores)

        print("---------------")
        print(f"WYNIK KOŃCOWY:")
        print(f"Najlepszy osobnik: {best_index}, {best_individual}")
        print(f"Minimalna wartość funkcji: {best_value}")

        return best_individual

    def _create_individual(self):
        return Bridge.random(self.bridge_template)

    def _create_population(self):
        return [self._create_individual() for _ in range(self.population_size)]

    def _fitness_function(self, bridge):
        highest_stress = bridge.calculate_highest_stress()
        mass = bridge.calculate_mass()

        if highest_stress > constants.ELASTIC_LIMIT_OF_STEEL:
            penalty_multiplier = constants.PENALTY_MULTIPLIER
            penalty = (highest_stress - constants.ELASTIC_LIMIT_OF_STEEL) * penalty_multiplier
            return mass + penalty
        else:
            return mass

    def _evaluate_population(self, population):
        fitness_scores = []
        for bridge in population:
            fitness = self._fitness_function(bridge)
            fitness_scores.append(fitness)

        return fitness_scores

    def _evaluate_population_multiprocessing(self, population):
        with mp.Pool(processes=self.processes) as pool:
            fitness_scores = pool.map(self._fitness_function, population)

        return fitness_scores

    def _tournament_selection(self, population, fitness_scores):
        selected = []
        for _ in range(self.population_size):
            tournament_competitors_indices = random.sample(range(self.population_size), constants.TOURNAMENT_SIZE)
            tournament_fitness = [fitness_scores[i] for i in tournament_competitors_indices]

            winner_index = tournament_competitors_indices[tournament_fitness.index(min(tournament_fitness))]
            selected.append(population[winner_index].clone())

        return selected

    def _crossover(self, parent1, parent2):
        crossover_point = random.randint(1, constants.GENOME_LENGTH - 1)

        parent1_diameters = parent1.diameters.as_list()
        parent2_diameters = parent2.diameters.as_list()

        child1_diameters = parent1_diameters[:crossover_point] + parent2_diameters[crossover_point:]
        child2_diameters = parent2_diameters[:crossover_point] + parent1_diameters[crossover_point:]

        child1 = parent1.clone()
        child2 = parent2.clone()

        child1.diameters.update_from_list(child1_diameters)
        child2.diameters.update_from_list(child2_diameters)

        return child1, child2

    def _mutate(self,bridge, mutation_rate=constants.DEFAULT_MUTATION_RATE):
        diameters = bridge.diameters.as_list()
        for i in range(constants.GENOME_LENGTH):
            if random.random() < mutation_rate:
                factor = 1.0 + random.uniform(-constants.MUTATION_RANGE, constants.MUTATION_RANGE)
                diameters[i] *= factor
                diameters[i] = max(constants.ELEMENT_DIAMETER_LOWER_BOUND,
                                    min(constants.ELEMENT_DIAMETER_UPPER_BOUND,
                                        diameters[i]))

        bridge.diameters.update_from_list(diameters)

        return bridge