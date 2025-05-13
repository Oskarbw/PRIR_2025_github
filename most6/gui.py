import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from model import SimpleBridge
from genetic import GeneticOptimizer
from visual import visualize_bridge

class OptimizationApp:
    """Prosta aplikacja do optymalizacji mostów."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Uproszczona optymalizacja mostu")
        self.root.geometry("800x600")
        
        # Tworzenie interfejsu
        self._create_widgets()
        
        # Stan aplikacji
        self.optimizer = None
        self.best_bridge = None
        self.is_running = False
    
    def _create_widgets(self):
        # Ramka główna
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel parametrów po lewej
        input_frame = ttk.LabelFrame(frame, text="Parametry", padding=10)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Parametry mostu
        ttk.Label(input_frame, text="Długość mostu [m]:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.length_var = tk.DoubleVar(value=20.0)
        ttk.Spinbox(input_frame, from_=10.0, to=50.0, increment=5.0, textvariable=self.length_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Liczba segmentów:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.segments_var = tk.IntVar(value=5)
        ttk.Spinbox(input_frame, from_=3, to=10, increment=1, textvariable=self.segments_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Parametry algorytmu
        ttk.Separator(input_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(input_frame, text="Wielkość populacji:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.pop_size_var = tk.IntVar(value=20)
        ttk.Spinbox(input_frame, from_=10, to=100, increment=10, textvariable=self.pop_size_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Liczba generacji:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.generations_var = tk.IntVar(value=20)
        ttk.Spinbox(input_frame, from_=10, to=100, increment=5, textvariable=self.generations_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Wskaźnik mutacji:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.mutation_var = tk.DoubleVar(value=0.1)
        ttk.Spinbox(input_frame, from_=0.01, to=0.5, increment=0.01, textvariable=self.mutation_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Liczba procesów:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.processes_var = tk.IntVar(value=4)
        ttk.Spinbox(input_frame, from_=1, to=8, increment=1, textvariable=self.processes_var, width=10).grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Przycisk start
        ttk.Button(input_frame, text="Rozpocznij optymalizację", command=self.start_optimization).grid(row=7, column=0, columnspan=2, pady=10)
        
        # Panel wyników po prawej
        result_frame = ttk.Frame(frame)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Panel z zakładkami (wykresy, wizualizacja)
        self.tab_control = ttk.Notebook(result_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Zakładka z wykresem postępu
        progress_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(progress_tab, text="Postęp optymalizacji")
        
        # Zakładka z wizualizacją mostu
        visualization_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(visualization_tab, text="Wizualizacja mostu")
        
        # Status
        self.status_var = tk.StringVar(value="Gotowy do rozpoczęcia")
        ttk.Label(result_frame, textvariable=self.status_var, foreground='blue').pack(anchor=tk.W, pady=(0, 10))
        
        # Wykres w pierwszej zakładce
        self.figure = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, progress_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Miejsce na wizualizację mostu w drugiej zakładce
        self.bridge_figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.bridge_figure.add_subplot(111)
        self.bridge_canvas = FigureCanvasTkAgg(self.bridge_figure, visualization_tab)
        self.bridge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Wyniki
        result_label_frame = ttk.LabelFrame(result_frame, text="Wyniki optymalizacji")
        result_label_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(result_label_frame, text="Fitness:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.fitness_var = tk.StringVar(value="-")
        ttk.Label(result_label_frame, textvariable=self.fitness_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(result_label_frame, text="Masa:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.mass_var = tk.StringVar(value="-")
        ttk.Label(result_label_frame, textvariable=self.mass_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(result_label_frame, text="Wytrzymałość:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.strength_var = tk.StringVar(value="-")
        ttk.Label(result_label_frame, textvariable=self.strength_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
    
    def start_optimization(self):
        if self.is_running:
            return
        
        # Pobierz parametry
        length = self.length_var.get()
        segments = self.segments_var.get()
        pop_size = self.pop_size_var.get()
        generations = self.generations_var.get()
        mutation_rate = self.mutation_var.get()
        num_processes = self.processes_var.get()
        
        # Utwórz szablon mostu
        bridge_template = SimpleBridge(length=length, num_segments=segments)
        
        # Utwórz optymalizator
        self.optimizer = GeneticOptimizer(
            population_size=pop_size,
            bridge_template=bridge_template,
            mutation_rate=mutation_rate
        )
        
        # Uruchom optymalizację w osobnym wątku
        self.is_running = True
        self.status_var.set("Trwa optymalizacja...")
        
        thread = threading.Thread(
            target=self._run_optimization,
            args=(generations, num_processes)
        )
        thread.daemon = True
        thread.start()
    
    def _run_optimization(self, generations, num_processes):
        try:
            # Funkcja aktualizująca wykres podczas optymalizacji
            def update_chart():
                if self.is_running and self.optimizer:
                    self._update_chart()
                    self.root.after(500, update_chart)
            
            # Rozpocznij aktualizację wykresu
            self.root.after(0, update_chart)
            
            # Uruchom algorytm genetyczny
            self.best_bridge = self.optimizer.evolve(generations, num_processes)
            
            # Aktualizuj wyniki
            def update_results():
                self.status_var.set("Optymalizacja zakończona")
                self._update_chart()
                self._show_results(self.best_bridge)
            
            self.root.after(0, update_results)
            
        except Exception as e:
            def show_error():
                self.status_var.set(f"Błąd: {str(e)}")
            
            self.root.after(0, show_error)
        
        finally:
            self.is_running = False
    
    def _update_chart(self):
        """Aktualizuje wykres."""
        if not self.optimizer or not self.optimizer.best_fitness_history:
            return
        
        self.ax.clear()
        gen = range(1, len(self.optimizer.best_fitness_history) + 1)
        self.ax.plot(gen, self.optimizer.best_fitness_history, 'b-', label='Najlepszy')
        self.ax.plot(gen, self.optimizer.avg_fitness_history, 'r-', label='Średni')
        
        self.ax.set_xlabel('Generacja')
        self.ax.set_ylabel('Fitness')
        self.ax.set_title('Postęp optymalizacji')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()
        
        # Aktualizuj wizualizację mostu jeśli jest najlepszy most
        if self.best_bridge:
            self._update_bridge_visualization()
    
    def _update_bridge_visualization(self):
        """Aktualizuje wizualizację mostu."""
        if not self.best_bridge:
            return
            
        # Upewnij się, że most ma obliczone wszystkie parametry
        self.best_bridge.evaluate()

        self.bridge_figure.clear()
        ax = self.bridge_figure.add_subplot(111)

        
        # Utwórz wizualizację bezpośrednio na istniejącej figurze i osi
        visualize_bridge(
        self.best_bridge, 
        show=False, 
        fig=self.bridge_figure,
        ax=ax
    )

        
        # Odśwież canvas
        self.bridge_canvas.draw()
    
    def _show_results(self, bridge):
        """Pokazuje wyniki optymalizacji."""
        if not bridge:
            return
        
        self.fitness_var.set(f"{bridge.fitness:.6f}")
        self.mass_var.set(f"{bridge.mass:.2f} kg")
        self.strength_var.set(f"{bridge.strength:.4f}")
        
        # Wyświetl optymalne wartości przekrojów
        result_text = "Optymalne przekroje:\n"
        sections_names = ["Pasy górne", "Pasy dolne", "Słupki", "Krzyżulce", "Poprzeczki"]
        for name, value in zip(sections_names, bridge.sections):
            result_text += f"  {name}: {value*1000:.2f} cm²\n"
        
        # Utwórz lub zaktualizuj etykietę z optymalnymi przekrojami
        if hasattr(self, 'sections_label'):
            self.sections_label.config(text=result_text)
        else:
            self.sections_label = ttk.Label(self.root, text=result_text)
            self.sections_label.pack(pady=10)
        
        # Aktualizuj wizualizację mostu
        self.best_bridge = bridge
        self._update_bridge_visualization()
        
        # Przełącz na zakładkę z wizualizacją po zakończeniu
        self.tab_control.select(1)  # Przełącz na drugą zakładkę (indeks 1)
    
    def run(self):
        """Uruchamia aplikację."""
        self.root.mainloop()