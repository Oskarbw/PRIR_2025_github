import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from model import Bridge
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
        
        ttk.Label(input_frame, text="Minimalna wytrzymałość [kg]:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.strength_var = tk.DoubleVar(value=3000.0)
        ttk.Spinbox(input_frame, from_=500.0, to=10000.0, increment=100.0, textvariable=self.strength_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Parametry algorytmu
        ttk.Separator(input_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(input_frame, text="Wielkość populacji:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.pop_size_var = tk.IntVar(value=20)
        ttk.Spinbox(input_frame, from_=10, to=200, increment=10, textvariable=self.pop_size_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Liczba generacji:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.generations_var = tk.IntVar(value=20)
        ttk.Spinbox(input_frame, from_=10, to=200, increment=5, textvariable=self.generations_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Wskaźnik mutacji:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.mutation_var = tk.DoubleVar(value=0.1)
        ttk.Spinbox(input_frame, from_=0.01, to=0.5, increment=0.01, textvariable=self.mutation_var, width=10).grid(row=6, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(input_frame, text="Liczba procesów:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.processes_var = tk.IntVar(value=4)
        ttk.Spinbox(input_frame, from_=1, to=8, increment=1, textvariable=self.processes_var, width=10).grid(row=7, column=1, sticky=tk.W, pady=2)
        
        # Przycisk start
        self.start_button = ttk.Button(input_frame, text="Rozpocznij optymalizację", command=self.start_optimization)
        self.start_button.grid(row=8, column=0, columnspan=2, pady=10)
        
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
        self.bridge_ax = self.bridge_figure.add_subplot(111)
        self.bridge_canvas = FigureCanvasTkAgg(self.bridge_figure, visualization_tab)
        self.bridge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Wyniki
        result_label_frame = ttk.LabelFrame(result_frame, text="Wyniki optymalizacji")
        result_label_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(result_label_frame, text="Fitness:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.fitness_display_var = tk.StringVar(value="-")
        ttk.Label(result_label_frame, textvariable=self.fitness_display_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(result_label_frame, text="Masa:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.mass_var = tk.StringVar(value="-")
        ttk.Label(result_label_frame, textvariable=self.mass_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(result_label_frame, text="Wytrzymałość:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.strength_display_var = tk.StringVar(value="-")
        ttk.Label(result_label_frame, textvariable=self.strength_display_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Miejsce na etykietę z przekrojami
        self.sections_frame = ttk.LabelFrame(result_frame, text="Optymalne średnice")
        self.sections_frame.pack(fill=tk.X, pady=5)
        
        self.sections_text = tk.Text(self.sections_frame, height=5, width=30)
        self.sections_text.pack(padx=5, pady=5)
    
    def start_optimization(self):
        if self.is_running:
            return
        
        # Pobierz parametry
        length = self.length_var.get()
        segments = self.segments_var.get()
        min_strength = self.strength_var.get()
        pop_size = self.pop_size_var.get()
        generations = self.generations_var.get()
        mutation_rate = self.mutation_var.get()
        num_processes = self.processes_var.get()
        
        # Utwórz szablon mostu
        bridge_template = Bridge(length=length, segments=segments)
        
        # Utwórz optymalizator
        self.optimizer = GeneticOptimizer(
            bridge_template=bridge_template,
            min_strength=min_strength,
            population_size=pop_size,
            generations=generations,
            mutation_rate=mutation_rate,
            processes=num_processes
        )
        
        # Uruchom optymalizację w osobnym wątku
        self.is_running = True
        self.status_var.set("Trwa optymalizacja...")
        self.start_button.config(state='disabled')
        
        thread = threading.Thread(
            target=self._run_optimization,
            args=()
        )
        thread.daemon = True
        thread.start()
    
    def _run_optimization(self):
        try:
            # Uruchom funkcję aktualizacji wykresu
            def update_chart():
                if self.is_running and self.optimizer:
                    self._update_chart()
                    self.root.after(500, update_chart)
            self.root.after(0, update_chart)
            
            # Uruchom algorytm genetyczny
            best_bridge, _ = self.optimizer.run()
            self.best_bridge = best_bridge
            
            # Aktualizuj GUI w głównym wątku
            def update_results():
                self.status_var.set("Optymalizacja zakończona")
                self._update_chart()
                self._show_results(self.best_bridge)
                self.start_button.config(state='normal')
                
            self.root.after(0, update_results)
            
        except Exception as error:
            # Uchwyt błędu w głównym wątku
            def show_error():
                self.status_var.set(f"Błąd: {str(error)}")
                self.start_button.config(state='normal')
                
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
            
        try:
            # Wyczyść poprzednią wizualizację
            self.bridge_ax.clear()
            
            # Stwórz prostą wizualizację mostu
            self._create_simple_bridge_visualization()
            
            # Odśwież canvas
            self.bridge_canvas.draw()
            
        except Exception as e:
            print(f"Błąd podczas aktualizacji wizualizacji: {e}")
    
    def _create_simple_bridge_visualization(self):
        """Tworzy prostą wizualizację mostu."""
        if not self.best_bridge:
            return
            
        bridge = self.best_bridge
        
        # Parametry wizualizacji
        length = bridge.length
        segments = bridge.segments
        height = 5  # Wysokość mostu
        segment_length = length / segments
        
        # Węzły górne i dolne
        upper_x = [i * segment_length for i in range(segments + 1)]
        upper_y = [height] * (segments + 1)
        
        lower_x = [i * segment_length for i in range(segments + 1)]
        lower_y = [0] * (segments + 1)
        
        # Rysuj pas górny
        self.bridge_ax.plot(upper_x, upper_y, 'b-', linewidth=bridge.diameters.top_chord/50, label='Pas górny')
        
        # Rysuj pas dolny
        self.bridge_ax.plot(lower_x, lower_y, 'g-', linewidth=bridge.diameters.bottom_chord/50, label='Pas dolny')
        
        # Rysuj słupki
        for i in range(segments + 1):
            self.bridge_ax.plot([upper_x[i], lower_x[i]], [upper_y[i], lower_y[i]], 
                               'k-', linewidth=bridge.diameters.post/50)
        
        # Rysuj krzyżulce
        for i in range(segments):
            # Lewa krzyżulec
            self.bridge_ax.plot([lower_x[i], upper_x[i+1]], [lower_y[i], upper_y[i+1]], 
                               'r-', linewidth=bridge.diameters.diagonal/50, alpha=0.7)
            # Prawa krzyżulec
            self.bridge_ax.plot([upper_x[i], lower_x[i+1]], [upper_y[i], lower_y[i+1]], 
                               'r-', linewidth=bridge.diameters.diagonal/50, alpha=0.7)
        
        # Ustawienia osi
        self.bridge_ax.set_xlim(-1, length + 1)
        self.bridge_ax.set_ylim(-1, height + 1)
        self.bridge_ax.set_aspect('equal')
        self.bridge_ax.set_title(f'Most kratownicowy ({length}m, {segments} segmentów)')
        self.bridge_ax.grid(True, alpha=0.3)
        
        # Dodaj podpory
        # Lewa podpora (trójkąt)
        support_x = [0, -0.5, 0.5, 0]
        support_y = [0, -0.8, -0.8, 0]
        self.bridge_ax.plot(support_x, support_y, 'k-', linewidth=2)
        
        # Prawa podpora (prostokąt z kółkiem)
        self.bridge_ax.plot([length-0.3, length+0.3, length+0.3, length-0.3, length-0.3], 
                           [0, 0, -0.5, -0.5, 0], 'k-', linewidth=2)
        circle = plt.Circle((length, -0.3), 0.15, color='gray', alpha=0.7)
        self.bridge_ax.add_patch(circle)
        
        # Strzałka obciążenia
        arrow_y = height + 1
        self.bridge_ax.arrow(length/2, arrow_y, 0, -0.5, head_width=0.3, head_length=0.2, 
                            fc='blue', ec='blue')
        self.bridge_ax.text(length/2, arrow_y + 0.3, 'Obciążenie', ha='center', fontsize=10)
    
    def _show_results(self, bridge):
        """Pokazuje wyniki optymalizacji."""
        if not bridge:
            return
        
        mass = bridge.calculate_mass()
        strength = bridge.calculate_strength()
        
        self.fitness_display_var.set(f"{mass:.6f}")
        self.mass_var.set(f"{mass:.2f} kg")
        self.strength_display_var.set(f"{strength:.4f}")
        
        # Wyświetl optymalne wartości przekrojów
        result_text = "Optymalne średnice:\n"
        diameters_names = ["Pas górny", "Pas dolny", "Słupki", "Krzyżulce"]
        for name, value in zip(diameters_names, bridge.diameters.as_list()):
            result_text += f"  {name}: {value:.2f} mm\n"
        
        # Aktualizuj pole tekstowe z wynikami
        self.sections_text.delete(1.0, tk.END)
        self.sections_text.insert(1.0, result_text)
        
        # Aktualizuj wizualizację mostu
        self.best_bridge = bridge
        self._update_bridge_visualization()
        
        # Przełącz na zakładkę z wizualizacją po zakończeniu
        self.tab_control.select(1)  # Przełącz na drugą zakładkę (indeks 1)
    
    def run(self):
        """Uruchamia aplikację."""
        self.root.mainloop()