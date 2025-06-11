import math
import random
from dataclasses import dataclass

import constants

@dataclass
class Diameters: # średnice w mlimetrach
    top_chord: float
    bottom_chord: float
    post: float
    diagonal: float

    def __init__(self, values=None):
        if values is None:
            self.top_chord= constants.DEFAULT_TOP_CHORD_DIAMETER
            self.bottom_chord = constants.DEFAULT_BOTTOM_CHORD_DIAMETER
            self.post = constants.DEFAULT_POST_DIAMETER
            self.diagonal = constants.DEFAULT_DIAGONAL_DIAMETER
        else:
            self.top_chord, self.bottom_chord, self.post, self.diagonal = values

    def as_list(self):
        return [self.top_chord, self.bottom_chord, self.post, self.diagonal]

    def update_from_list(self, values) -> None:
        self.top_chord, self.bottom_chord, self.post, self.diagonal = values


class Bridge:
    def __init__(self, length=20.0, segments=5, diameters=Diameters()):
        self.length = length
        self.segments = segments
        self.diameters = diameters
        
        self.highest_stress = None
        self.mass = None
        self.strength = None
    
    def calculate_mass(self):
        density = constants.STEEL_DENSITY
        
        segment_length = self.length / self.segments
        height = constants.BRIDGE_HEIGHT
        diagonal_length = math.sqrt(segment_length**2 + height**2)

        total_lengths = [
            self.length,                            # top_chord
            self.length,                            # bottom_chord
            (self.segments + 1) * height,           # posts
            (self.segments * 2) * diagonal_length,  # diagonals
        ]
        
        volumes = [(s/1000)**2 *math.pi * l for s, l in zip(self.diameters.as_list(), total_lengths)]
        total_mass = sum(volumes) * density
        
        return total_mass
    
    def calculate_strength(self):
        # Bardzo uproszczona ocena - im większe przekroje, tym lepsza wytrzymałość,
        strength = 1000 * self.segments * (self.diameters.as_list()[0]/100 
                                               * self.diameters.as_list()[1]/100 
                                               * self.diameters.as_list()[2]/50 
                                               * self.diameters.as_list()[3]/40) / (self.length/10)**2
        
        return strength
    
    def clone(self):
        
        return Bridge(
            length=self.length,
            segments=self.segments,
            diameters=Diameters(self.diameters.as_list())
        )
    
    @classmethod
    def random(cls, length, segments):
        top_chord_diameter = random.uniform(constants.TOP_CHORD_LOWER_BOUND, constants.TOP_CHORD_UPPER_BOUND)
        bottom_chord_diameter = random.uniform(constants.BOTTOM_CHORD_LOWER_BOUND, constants.BOTTOM_CHORD_UPPER_BOUND)
        post_diameter = random.uniform(constants.POST_LOWER_BOUND, constants.POST_UPPER_BOUND)
        diagonal_diameter = random.uniform(constants.DIAGONAL_LOWER_BOUND, constants.DIAGONAL_UPPER_BOUND)
        
        diameters = Diameters([top_chord_diameter,
                     bottom_chord_diameter,
                     post_diameter,
                     diagonal_diameter])
        
        random_bridge = Bridge(length=length, segments=segments, diameters=diameters)  

        return random_bridge