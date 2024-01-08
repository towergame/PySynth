from classes.wave import Wave
from classes.wave_generator import WaveTypes
from classes.envelope import Envelope

MAX_VOL = 0.6  # Maximum volume for the program
# Both of these values were extracted from the example code of the SoundCard library
# From my empirical testing, these values seem to work the best (as in, generate the least amount of noise)
BITRATE = 48000  # Bitrate of the program
BUFFER_SIZE = 1024  # Buffer size of the program

# The wave preset to use by default
DEFAULT_WAVE_PRESET = [
    Wave(WaveTypes.SINE, 1, 1, 0)
]

# The envelope preset to use by default
DEFAULT_ENVELOPE_PRESET = Envelope(0.1, 0.1, 0.4, 0.25)
