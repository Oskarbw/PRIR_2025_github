class SimpleBridge:
    """Bardzo uproszczony model mostu."""
    
    def __init__(self, length=20.0, num_segments=5, sections=None):
        self.length = length
        self.num_segments = num_segments
        
        # Przekroje elementów w m²
        if sections is None:
            self.sections = [0.01, 0.01, 0.008, 0.006, 0.007]
        else:
            self.sections = sections
        
        # Oceny
        self.mass = None
        self.strength = None
        self.fitness = None
    
    def calculate_mass(self):
        """Oblicza przybliżoną masę mostu."""
        # Gęstość stali: 7850 kg/m³
        density = 7850
        
        # Długości elementów
        seg_len = self.length / self.num_segments
        total_length = [
            self.length * 2,                        # pasy górne
            self.length * 2,                        # pasy dolne
            (self.num_segments + 1) * 2,            # słupki
            self.num_segments * 2 * 1.414 * seg_len,  # krzyżulce
            (self.num_segments + 1) * 2             # poprzeczki
        ]
        
        # Objętości i masa
        volumes = [s * l for s, l in zip(self.sections, total_length)]
        total_mass = sum(volumes) * density
        
        return total_mass
    
    def calculate_strength(self):
        """Oblicza przybliżoną ocenę wytrzymałości."""
        # Bardzo uproszczona ocena - im większe przekroje, tym lepsza wytrzymałość,
        # ale z malejącymi zwrotami
        strength = sum(section ** 0.5 for section in self.sections)
        
        return strength
    
    def evaluate(self):
        """Ocenia most."""
        self.mass = self.calculate_mass()
        self.strength = self.calculate_strength()
        
        # Funkcja przystosowania: maksymalizacja wytrzymałości, minimalizacja masy
        self.fitness = self.strength / (self.mass ** 0.5)
        
        return self.fitness
    
    def clone(self):
        """Tworzy kopię mostu."""
        return SimpleBridge(
            length=self.length,
            num_segments=self.num_segments,
            sections=self.sections.copy()
        )