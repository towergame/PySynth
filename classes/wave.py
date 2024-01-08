from classes.wave_types import WaveTypes


class Wave:
    """
    A class representing a single wave

    Attributes
    ----------
    wave_type : WaveTypes
        The type of wave
    offset : float
        The offset of the wave relative to the base frequency (multiplicative)
    amplitude : float
        The amplitude of the wave
    phase : float
        The phase of the wave in radians
    """
    def __init__(self, wave_type: WaveTypes, offset: float, amplitude: float, phase: float = 0):
        """
        Constructs the object
        :param wave_type: The type of wave
        :param offset: The offset of the wave relative to the base frequency (multiplicative)
        :param amplitude: The amplitude of the wave
        :param phase: The phase of the wave in radians
        """
        # Set all of the attributes
        self.wave_type = wave_type
        self.offset = offset
        self.amplitude = amplitude
        self.phase = phase
