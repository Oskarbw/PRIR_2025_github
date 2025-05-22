import argparse
import time
import numpy as np
import matplotlib.pyplot as plt

from model import SimpleBridge
from genetic import GeneticOptimizer
from gui import OptimizationApp
from visual import visualize_bridge

def parse_args():
    # Parsuje argumenty wiersza poleceń.
    parser = argparse.ArgumentParser(description='Uproszczona optymalizacja mostu')
    
    parser.add_argument('--gui', action='store_true', help='Uruchom interfejs graficzny')
    parser.add_argument('--length', type=float, default=20.0, help='Długość mostu w metrach')
    parser.add_argument('--segments', type=int, default=5, help='Liczba segmentów')
    parser.add_argument('--strength', type=double, default=3000, help='Wymagana wytrzymalosc w kg')
    parser.add_argument('--population', type=int, default=20, help='Wielkość populacji')
    parser.add_argument('--generations', type=int, default=20, help='Liczba generacji')
    parser.add_argument('--mutation', type=float, default=0.1, help='Współczynnik mutacji')
    parser.add_argument('--processes', type=int, default=4, help='Liczba procesów równoległych')
    parser.add_argument('--plot', action='store_true', help='Wygeneruj wykres po zakończeniu')
    
    return parser.parse_args()

def run_optimization(args):
    # Uruchamia optymalizację z linii poleceń.
    print(f"Rozpoczynam optymalizację mostu o długości {args.length}m z {args.segments} segmentami")
    
    # Utwórz szablon mostu
    bridge_template = SimpleBridge(length=args.length, num_segments=args.segments)
    
    # Utwórz optymalizator
    optimizer = GeneticOptimizer(
        population_size=args.population,
        bridge_template=bridge_template,
        mutation_rate=args.mutation
    )
    
    # Mierz czas
    start_time = time.time()
    
    # Uruchom algorytm genetyczny
    best_bridge = optimizer.evolve(args.generations, args.processes)
    
    # Pokaż czas wykonania
    elapsed_time = time.time() - start_time
    print(f"\nCzas optymalizacji: {elapsed_time:.2f} sekund")
    
    # Pokaż wyniki
    print("\nWyniki optymalizacji:")
    print(f"Fitness: {best_bridge.fitness:.6f}")
    print(f"Masa: {best_bridge.mass:.2f} kg")
    print(f"Wytrzymałość: {best_bridge.strength:.4f}")
    
    # Wyświetl optymalne wartości przekrojów
    sections_names = ["Pasy górne", "Pasy dolne", "Słupki", "Krzyżulce", "Poprzeczki"]
    print("\nOptymalne przekroje:")
    for name, value in zip(sections_names, best_bridge.sections):
        print(f"  {name}: {value*1000:.2f} cm²")
    
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