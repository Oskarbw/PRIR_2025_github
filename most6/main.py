import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
import constants

from model import Bridge
from genetic import GeneticOptimizer
from gui import OptimizationApp
from visual import visualize_bridge

def parse_args():
    parser = argparse.ArgumentParser(description='Uproszczona optymalizacja mostu')
    
    parser.add_argument('--gui', action='store_true', help='Uruchom interfejs graficzny')
    parser.add_argument('--length', type=float, default=constants.DEFAULT_LENGTH, help='Długość mostu w metrach')
    parser.add_argument('--segments', type=int, default=constants.DEFAULT_SEGMENTS, help='Liczba segmentów')
    parser.add_argument('--strength', type=float, default=constants.DEFAULT_MIN_STRENGTH, help='Wymagana wytrzymalosc w kg')
    parser.add_argument('--population', type=int, default=constants.DEFAULT_POPULATION_SIZE, help='Wielkość populacji')
    parser.add_argument('--generations', type=int, default=constants.DEFAULT_GENERATIONS, help='Liczba generacji')
    parser.add_argument('--mutation', type=float, default=constants.DEFAULT_MUTATION_RATE, help='Współczynnik mutacji')
    parser.add_argument('--processes', type=int, default=constants.DEFAULT_PROCESSES, help='Liczba procesów równoległych')
    parser.add_argument('--plot', action='store_true', help='Wygeneruj wykres po zakończeniu')
    parser.add_argument('--visualize', action='store_true', help='Wygeneruj wizualizacje po zakończeniu')
    
    return parser.parse_args()

def run_optimization(args):
    # Uruchamia optymalizację z linii poleceń.
    print(f"Rozpoczynam optymalizację mostu o długości {args.length}m z {args.segments} segmentami")
    
    # Utwórz szablon mostu
    bridge_template = Bridge(length=args.length, segments=args.segments)
    
    optimizer = GeneticOptimizer(
        bridge_template = bridge_template,
        min_strength=args.strength, 
        population_size=args.population,
        generations=args.generations,
        mutation_rate=args.mutation, 
        processes=args.processes # dodac wielowatkowosc
    )

    # Mierz czas
    start_time = time.time()
    
    best_bridge, best_strength = optimizer.run() 
    #może lepiej dawac argumenty do run zeby nie musiec tworzyc nowego obie
    #ktu za kazdym razem
    
    # Pokaż czas wykonania
    elapsed_time = time.time() - start_time
    print(f"\nCzas optymalizacji: {elapsed_time:.2f} sekund")
    
    # Pokaż wyniki
    print("\nWyniki optymalizacji:")
    print(f"Masa: {best_bridge.calculate_mass():.2f} kg")
    print(f"Wytrzymałość: {best_bridge.calculate_strength():.6f} kg")
    
    # Wyświetl optymalne wartości przekrojów
    diameters_names = ["Pas górny", "Pas dolny", "Słupki", "Krzyżulce"]
    print("\nOptymalne średnice:")
    for name, value in zip(diameters_names, best_bridge.diameters):
        print(f"  {name}: {value:.2f} mm")
    
    # Wygeneruj wykres
    if args.plot:
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(optimizer.best_fitness_history) + 1), 
                 optimizer.best_fitness_history, 'b-', label='Najlepszy')
        plt.plot(range(1, len(optimizer.avg_fitness_history) + 1), 
                 optimizer.avg_fitness_history, 'r-', label='Średni')
        
        plt.xlabel('Generacja')
        plt.ylabel('Fitness')
        plt.title('Postęp optymalizacji')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        plot_filename = 'optimization_progress.png'
        if args.output:
            plot_filename = f"{args.output}_progress.png"
            
        plt.savefig(plot_filename)
        print(f"\nWykres zapisany do pliku '{plot_filename}'")
        plt.close()
    
    # Wygeneruj wizualizację mostu
    if args.visualize:
        vis_filename = None
        if args.output:
            vis_filename = f"{args.output}_bridge.png"
        
        visualize_bridge(best_bridge, filename=vis_filename)
        if vis_filename:
            print(f"Wizualizacja mostu zapisana do pliku '{vis_filename}'")
    
    return best_bridge, optimizer

def main():
    """Funkcja główna programu."""
    args = parse_args()
    
    if args.gui:
        # Uruchom interfejs graficzny
        app = OptimizationApp()
        app.run()
    else:
        # Uruchom z linii poleceń
        run_optimization(args)

if __name__ == "__main__":
    main()