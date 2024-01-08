from enum import Enum


class WaveTypes(Enum):
    """
    An enum representing the different types of waves
    """
    SINE = "sine"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    TRIANGLE = "triangle"
