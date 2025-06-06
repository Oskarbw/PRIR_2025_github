import math
import constants
import random

class Bridge:
    def __init__(self, length=20.0, segments=5, diameters=None):
        self.length = length
        self.segments = segments
        
        # średnice elementów w mm
        if diameters is None:
            self.diameters = [constants.DEFAULT_TOP_CHORD_DIAMETER,
                              constants.DEFAULT_BOTTOM_CHORD_DIAMETER,
                              constants.DEFAULT_POSTS_DIAMETER,
                              constants.DEFAULT_DIAGONALS_DIAMETER]
        else:
            self.diameters = diameters
        
        # Oceny
        self.mass = None
        self.strength = None
    
    def calculate_mass(self):
        # Gęstość stali: 7850 kg/m³
        density = constants.STEEL_DENSITY
        
        # Długości elementów w metrach
        segment_length = self.length / self.segments
        height = 5
        diagonal_length = math.sqrt(segment_length**2 + height**2)

        total_lengths = [
            self.length,                                # top_chord
            self.length,                                # bottom_chord
            (self.segments + 1) * height,           # posts
            (self.segments * 2) * diagonal_length,  # diagonals
        ]
        
        # Objętości i masa
        volumes = [(s/1000)**2 *math.pi * l for s, l in zip(self.diameters, total_lengths)]
        total_mass = sum(volumes) * density
        
        return total_mass
    
    def calculate_strength(self):
        # Bardzo uproszczona ocena - im większe przekroje, tym lepsza wytrzymałość,
        strength = 1000 * self.segments * (self.diameters[0]/100 
                                               * self.diameters[1]/100 
                                               * self.diameters[2]/50 
                                               * self.diameters[3]/40) / (self.length/10)**2
        return strength
    
    def clone(self):
        # Tworzy kopię mostu
        return Bridge(
            length=self.length,
            segments=self.segments,
            diameters=self.diameters.copy()
        )
    @classmethod
    def random(cls, length, segments):
        top_chord_diameter = random.uniform(constants.TOP_CHORD_LOWER_BOUND, constants.TOP_CHORD_UPPER_BOUND)
        bottom_chord_diameter = random.uniform(constants.BOTTOM_CHORD_LOWER_BOUND, constants.BOTTOM_CHORD_UPPER_BOUND)
        post_diameter = random.uniform(constants.POST_LOWER_BOUND, constants.POST_UPPER_BOUND)
        diagonal_diameter = random.uniform(constants.DIAGONAL_LOWER_BOUND, constants.DIAGONAL_UPPER_BOUND)
        
        diameters = [top_chord_diameter,
                     bottom_chord_diameter,
                     post_diameter,
                     diagonal_diameter]
        
        random_bridge = Bridge(length=length, segments=segments, diameters=diameters)  

        return random_bridge