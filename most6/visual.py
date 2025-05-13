import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Polygon
from matplotlib.collections import PatchCollection

def visualize_bridge(bridge, filename=None, show=True, fig=None, ax=None):
    """
    Tworzy wizualizację kratownicy mostu na podstawie modelu SimpleBridge.
    
    Args:
        bridge: Obiekt SimpleBridge do wizualizacji
        filename: Nazwa pliku do zapisania wizualizacji (opcjonalne)
        show: Czy wyświetlić wizualizację (domyślnie True)
        fig: Istniejąca figura matplotlib (opcjonalne)
        ax: Istniejąca oś matplotlib (opcjonalne)
    """
    # Utwórz figurę, jeśli nie została przekazana
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    else:
        ax.clear()  # Wyczyść oś, jeśli została przekazana
    
    # Obliczenia geometryczne
    length = bridge.length
    num_segments = bridge.num_segments
    segment_length = length / num_segments
    height = segment_length * 0.8  # Wysokość mostu jako proporcja długości segmentu
    
    # Skala grubości elementów dla wizualizacji
    max_thickness = 0.05 * height  # Maksymalna grubość jako procent wysokości
    min_thickness = 0.01 * height  # Minimalna grubość
    
    # Normalizacja grubości elementów
    max_section = max(bridge.sections)
    scaled_thickness = [min_thickness + (s / max_section) * (max_thickness - min_thickness) 
                        for s in bridge.sections]
    
    # Ustawienia osi
    ax.set_xlim(-segment_length/2, length + segment_length/2)
    ax.set_ylim(-height/2, height * 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Utwórz węzły górne i dolne
    upper_nodes = [(i * segment_length, height) for i in range(num_segments + 1)]
    lower_nodes = [(i * segment_length, 0) for i in range(num_segments + 1)]
    
    # Listy elementów
    patches = []
    
    # Funkcja do rysowania elementu jako prostokąta
    def add_element(start, end, thickness, color='gray'):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = np.sqrt(dx**2 + dy**2)
        angle = np.arctan2(dy, dx)
        
        # Środek elementu
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Utwórz prostokąt
        rect = Rectangle(
            (mid_x - length/2, mid_y - thickness/2),
            length, thickness, 
            angle=np.degrees(angle),
            color=color,
            ec='black',
            linewidth=0.5,
            zorder=1
        )
        
        # Przesuń do właściwej pozycji
        transform = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        
        offset = transform @ np.array([-length/2, 0])
        rect.set_xy((mid_x + offset[0], mid_y + offset[1]))
        
        patches.append(rect)
    
    # Narysuj pas górny
    for i in range(num_segments):
        add_element(upper_nodes[i], upper_nodes[i+1], scaled_thickness[0], 'steelblue')
    
    # Narysuj pas dolny
    for i in range(num_segments):
        add_element(lower_nodes[i], lower_nodes[i+1], scaled_thickness[1], 'steelblue')
    
    # Narysuj słupki
    for i in range(num_segments + 1):
        add_element(lower_nodes[i], upper_nodes[i], scaled_thickness[2], 'darkgray')
    
    # Narysuj krzyżulce
    for i in range(num_segments):
        add_element(lower_nodes[i], upper_nodes[i+1], scaled_thickness[3], 'firebrick')
        add_element(upper_nodes[i], lower_nodes[i+1], scaled_thickness[3], 'firebrick')
    
    # Narysuj poprzeczki (prostopadłe do płaszczyzny mostu)
    # Wizualizujemy je jako małe koła przy węzłach
    for i in range(num_segments + 1):
        circle_upper = plt.Circle(upper_nodes[i], scaled_thickness[4]/1.5, color='darkgoldenrod', 
                                  ec='black', linewidth=0.5, zorder=2)
        circle_lower = plt.Circle(lower_nodes[i], scaled_thickness[4]/1.5, color='darkgoldenrod', 
                                  ec='black', linewidth=0.5, zorder=2)
        ax.add_patch(circle_upper)
        ax.add_patch(circle_lower)
    
    # Dodaj prostokąty do wykresu
    for patch in patches:
        ax.add_patch(patch)
    
    # Dodaj podpory
    support_width = segment_length * 0.3
    support_height = height * 0.3
    
    # Lewa podpora (trójkąt)
    left_support = Polygon([
        (0, -support_height), 
        (support_width/2, 0), 
        (-support_width/2, 0)
    ], color='dimgray', ec='black', linewidth=0.5, zorder=0)
    ax.add_patch(left_support)
    
    # Prawa podpora (prostokąt z wałkiem)
    right_support_base = Rectangle(
        (length - support_width/2, -support_height),
        support_width, support_height,
        color='dimgray', ec='black', linewidth=0.5, zorder=0
    )
    ax.add_patch(right_support_base)
    
    # Wałek na prawej podporze
    roller = plt.Circle((length, -support_height/3), support_height/6, 
                         color='dimgray', ec='black', linewidth=0.5, zorder=0)
    ax.add_patch(roller)
    
    # Dodaj tytuł i informacje
    ax.set_title(f'Wizualizacja mostu kratownicowego ({length}m, {num_segments} segmentów)')
    
    # Dodaj strzałkę wskazującą na obciążenie
    arrow_length = height * 0.5
    ax.arrow(length/2, height + arrow_length, 0, -arrow_length/2, 
             head_width=segment_length*0.15, head_length=arrow_length*0.2, 
             fc='blue', ec='blue', linewidth=2)
    
    # Legenda opisująca grubości elementów
    legend_elements = [
        Rectangle((0, 0), 1, 1, color='royalblue', label=f'Pasy górne: {bridge.sections[0]*10000:.1f} cm²'),
        Rectangle((0, 0), 1, 1, color='dodgerblue', label=f'Pasy dolne: {bridge.sections[1]*10000:.1f} cm²'),
        Rectangle((0, 0), 1, 1, color='gray', label=f'Słupki: {bridge.sections[2]*10000:.1f} cm²'),
        Rectangle((0, 0), 1, 1, color='tomato', label=f'Krzyżulce: {bridge.sections[3]*10000:.1f} cm²'),
        Rectangle((0, 0), 1, 1, color='goldenrod', label=f'Poprzeczki: {bridge.sections[4]*10000:.1f} cm²')

    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))

    
    # Dodaj informacje o masie i wytrzymałości
    mass_text = f'Masa: {bridge.mass:.1f} kg'
    strength_text = f'Wytrzymałość: {bridge.strength:.4f}'
    fitness_text = f'Fitness: {bridge.fitness:.6f}'
    
    # Umieść informacje w lewym dolnym rogu
    plt.figtext(0.02, 0.02, mass_text + '\n' + strength_text + '\n' + fitness_text, 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
    
    # Zastosuj układanie
    fig.tight_layout()
    
    # Zapisz do pliku, jeśli podano nazwę
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    # Wyświetl, jeśli trzeba
    if show and fig is None:  # Tylko jeśli to nowa figura
        plt.show()
    elif not show and fig is None:  # Jeśli nowa figura, ale nie chcemy pokazywać
        plt.close(fig)
    
    return fig, ax