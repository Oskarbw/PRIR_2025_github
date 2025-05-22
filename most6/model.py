import math

class SimpleBridge:
    def __init__(self, length=20.0, num_segments=5, members=None):
        self.length = length
        self.num_segments = num_segments
        
        # średnice elementów w mm
        if members is None:
            self.members.top_chord = 150
            self.members.bottom_chord = 200
            self.members.posts = 100
            self.members.diagonals = 75
        else:
            self.members = members
        
        # Oceny
        self.mass = None
        self.strength = None
    
    def calculate_mass(self):
        # Gęstość stali: 7850 kg/m³
        density = 7850
        
        # Długości elementów w metrach
        segment_length = self.length / self.num_segments
        height = 5
        diagonal_length = math.sqrt(segment_length**2 + height**2)

        total_lengths = [
            self.length,                                # top_chord
            self.length,                                # bottom_chord
            (self.num_segments + 1) * height,           # posts
            (self.num_segments * 2) * diagonal_length,  # diagonals
        ]
        
        # Objętości i masa
        members_merged = [self.members.top_chord, self.members.bottom_chord, self.members.posts, self.members.diagonals]
        volumes = [s**2 *math.pi * l for s, l in zip(members_merged, total_lengths)]
        total_mass = sum(volumes) * density
        
        return total_mass
    
    def calculate_strength(self):
        # Bardzo uproszczona ocena - im większe przekroje, tym lepsza wytrzymałość,
        strength = 1000 * self.num_segments * (self.members.top_chord/100 
                                               * self.members.top_chord/100 
                                               * self.members.top_chord/50 
                                               * self.members.top_chord/40) / (self.length/10)**2
        return strength
    
    # ta funkcja powinna być w genetic.py
    """ 
    def evaluate(self):
        self.mass = self.calculate_mass()
        self.strength = self.calculate_strength()
        
        # Funkcja przystosowania: maksymalizacja wytrzymałości, minimalizacja masy
        self.fitness = self.strength / (self.mass ** 0.5)
        
        return self.fitness
    """
    
    def clone(self):
        # Tworzy kopię mostu
        return SimpleBridge(
            length=self.length,
            num_segments=self.num_segments,
            sections=self.sections.copy()
        )