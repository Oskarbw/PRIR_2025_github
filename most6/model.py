import math
import random
from dataclasses import dataclass

import constants
from strength import Strength

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
    def __init__(self,
                 length=constants.DEFAULT_LENGTH,
                 segments=constants.DEFAULT_SEGMENTS,
                 min_strength=constants.DEFAULT_MIN_STRENGTH,
                 diameters=Diameters()):
        self.length = length
        self.segments = segments
        self.min_strength = min_strength
        self.diameters = diameters
        
        self.highest_stress = None
        self.strength = Strength(self)
    
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
        
        volumes = [(s * constants.MM_TO_M)**2 *math.pi * l for s, l in zip(self.diameters.as_list(), total_lengths)]
        mass = sum(volumes) * density  
        
        return mass
    
    def calculate_highest_stress(self):
        highest_stress = self.strength.highest_stress(self.diameters)
        self.highest_stress = highest_stress
        
        return highest_stress
    
    def clone(self):
        
        return Bridge(
            length=self.length,
            segments=self.segments,
            min_strength=self.min_strength,
            diameters=Diameters(self.diameters.as_list())
        )
    
    @classmethod
    def random(cls, bridge_template):
        top_chord_diameter = random.uniform(constants.TOP_CHORD_LOWER_BOUND, constants.TOP_CHORD_UPPER_BOUND)
        bottom_chord_diameter = random.uniform(constants.BOTTOM_CHORD_LOWER_BOUND, constants.BOTTOM_CHORD_UPPER_BOUND)
        post_diameter = random.uniform(constants.POST_LOWER_BOUND, constants.POST_UPPER_BOUND)
        diagonal_diameter = random.uniform(constants.DIAGONAL_LOWER_BOUND, constants.DIAGONAL_UPPER_BOUND)
        
        diameters = Diameters([top_chord_diameter,
                     bottom_chord_diameter,
                     post_diameter,
                     diagonal_diameter])
        
        random_bridge = Bridge(length=bridge_template.length,
                                segments=bridge_template.segments,
                                min_strength=bridge_template.min_strength,
                                diameters=diameters)
        return random_bridge