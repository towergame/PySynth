from enum import Enum
import numpy as np
import scipy.signal as signal
from classes.wave import Wave


class WaveTypes(Enum):
    SINE = "sine"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    TRIANGLE = "triangle"


class WaveGenerator:
    def __init__(self, wave_types: [Wave], frequency):
        self.wave_types = wave_types
        self.frequency = frequency

    def generate_wave(self, time):
        samples = np.ones(len(time))
        for wave in self.wave_types:
            if wave.wave_type == WaveTypes.SINE:
                samples *= wave.amplitude * np.sin(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase)
            elif wave.wave_type == WaveTypes.SQUARE:
                samples *= wave.amplitude * signal.square(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase)
            elif wave.wave_type == WaveTypes.SAWTOOTH:
                samples *= wave.amplitude * signal.sawtooth(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase)
            elif wave.wave_type == WaveTypes.TRIANGLE:
                samples *= wave.amplitude * signal.sawtooth(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase, width=0.5)
            else:
                raise Exception("Invalid Wave Type")
        return samples
