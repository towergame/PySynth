from enum import Enum
import numpy as np
import scipy.signal as signal
from classes.wave import Wave
from classes.wave_types import WaveTypes


class WaveGenerator:
    """
    A class representing a wave generator (so, a collection of oscillators)

    Attributes
    ----------
    wave_types : [Wave]
        A list of waves to be generated
    frequency : float
        The frequency of the wave generator

    Methods
    -------
    generate_wave(time)
        Generates a wave at the given time
    """
    def __init__(self, wave_types: [Wave], frequency: float):
        """
        Constructs the object
        :param wave_types: A list of waves comprising the final waveform
        :param frequency: The base frequency to use
        """
        # Set all of the attributes
        self.wave_types = wave_types
        self.frequency = frequency

    def generate_wave(self, time: np.ndarray) -> np.ndarray:
        """
        Generates a waveform in the given timespan
        :param time: a ndarray of time values
        :return: A ndarray of samples of the waveform
        """
        # Generate an array of ones for the entire timespan to use for further wave transformations
        samples = np.ones(len(time))
        # Multiply the samples by each wave (thus creating the target wave)
        for wave in self.wave_types:
            # Use the specific wave generation function for each respective wave type
            if wave.wave_type == WaveTypes.SINE:
                samples *= wave.amplitude * np.sin(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase)
            elif wave.wave_type == WaveTypes.SQUARE:
                samples *= wave.amplitude * signal.square(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase)
            elif wave.wave_type == WaveTypes.SAWTOOTH:
                samples *= wave.amplitude * signal.sawtooth(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase)
            elif wave.wave_type == WaveTypes.TRIANGLE:
                samples *= wave.amplitude * signal.sawtooth(2 * np.pi * (self.frequency * wave.offset) * time + wave.phase, width=0.5)
            # TODO: Add a noise wave type
            else:
                # If the wave is not found, raise an exception (this should never happen)
                raise Exception("Invalid Wave Type")
        # Return the generated waveform
        return samples
