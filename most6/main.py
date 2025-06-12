import argparse
import time
import matplotlib.pyplot as plt

import constants
from model import Bridge
from genetic import GeneticOptimizer
from gui import OptimizationApp

def main():
    args = _parse_args()

    if args.gui:
        app = OptimizationApp()
        app.run()
    else:
        _run_optimization(args)

def _parse_args():
    parser = argparse.ArgumentParser(description='Uproszczona optymalizacja mostu')

    parser.add_argument('--gui', action='store_true', help='Uruchom interfejs graficzny')
    parser.add_argument('--len', type=float, default=constants.DEFAULT_LENGTH, help='Długość mostu w metrach')
    parser.add_argument('--seg', type=int, default=constants.DEFAULT_SEGMENTS, help='Liczba segmentów')
    parser.add_argument('--str', type=float, default=constants.DEFAULT_MIN_STRENGTH, help='Wymagana wytrzymalosc w kg')
    parser.add_argument('--pop', type=int, default=constants.DEFAULT_POPULATION_SIZE, help='Wielkość populacji')
    parser.add_argument('--gen', type=int, default=constants.DEFAULT_GENERATIONS, help='Liczba generacji')
    parser.add_argument('--mut', type=float, default=constants.DEFAULT_MUTATION_RATE, help='Współczynnik mutacji')
    parser.add_argument('--proc', type=int, default=constants.DEFAULT_PROCESSES, help='Liczba procesów równoległych')
    parser.add_argument('--plot', action='store_true', help='Wygeneruj wykres po zakończeniu')

    return parser.parse_args()

def _run_optimization(args):
    print(f"Rozpoczynam optymalizację mostu o długości {args.len}m z {args.seg} segmentami")

    bridge_template = Bridge(length=args.len, segments=args.seg, min_strength=args.str)

    optimizer = GeneticOptimizer(
        bridge_template = bridge_template,
        population_size=args.pop,
        generations=args.gen,
        mutation_rate=args.mut,
        processes=args.proc
    )

    start_time = time.time()

    best_bridge = optimizer.run()

    elapsed_time = time.time() - start_time
    print(f"\nCzas optymalizacji: {elapsed_time:.2f} sekund")

    print("\nWyniki optymalizacji:")
    print(f"Masa: {best_bridge.calculate_mass():.2f} kg")
    print(f"Największe naprężenie w prętach: {(best_bridge.highest_stress / constants.MEGA):.4f} MPa")
    print(f"Dopuszczalne naprężenie stali S355: {(constants.ELASTIC_LIMIT_OF_STEEL / constants.MEGA):.2f} MPa")

    diameters_names = ["Pas górny", "Pas dolny", "Słupki", "Krzyżulce"]
    print("\nOptymalne średnice:")
    for name, value in zip(diameters_names, best_bridge.diameters.as_list()):
        print(f"  {name}: {value:.2f} mm")

    if args.plot:
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(optimizer.best_fitness_history) + 1),
                 optimizer.best_fitness_history, 'b-', label='Najlepszy')

        plt.xlabel('Generacja')
        plt.ylabel('Fitness')
        plt.title('Postęp optymalizacji')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        plot_filename = 'optimization_progress.png'

        plt.savefig(plot_filename)
        print(f"\nWykres zapisany do pliku '{plot_filename}'")
        plt.close()

if __name__ == "__main__":
    main()