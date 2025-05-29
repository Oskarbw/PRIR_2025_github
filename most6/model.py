import math

class SimpleBridge:
    def __init__(self, length=20.0, num_segments=5, diameters=None):
        self.length = length
        self.num_segments = num_segments
        
        # średnice elementów w mm
        if diameters is None:
            self.diameters = [150,200,100,75] # top, bottom, posts, diagonals
        else:
            self.diameters = diameters
        
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
        volumes = [(s/1000)**2 *math.pi * l for s, l in zip(self.diameters, total_lengths)]
        total_mass = sum(volumes) * density
        
        return total_mass
    
    def calculate_strength(self):
        # Bardzo uproszczona ocena - im większe przekroje, tym lepsza wytrzymałość,
        strength = 1000 * self.num_segments * (self.diameters[0]/100 
                                               * self.diameters[1]/100 
                                               * self.diameters[2]/50 
                                               * self.diameters[3]/40) / (self.length/10)**2
        return strength
    
    def clone(self):
        # Tworzy kopię mostu
        return SimpleBridge(
            length=self.length,
            num_segments=self.num_segments,
            diameters=self.diameters.copy()
        )