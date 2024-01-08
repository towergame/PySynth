from classes.wave import Wave
from classes.wave_generator import WaveTypes
from classes.envelope import Envelope

MAX_VOL = 0.6
BITRATE = 44100
BUFFSIZE = 4096

DEFAULT_WAVE_PRESET = [
    Wave(WaveTypes.SINE, 1, 1, 0)
]

DEFAULT_ENVELOPE_PRESET = Envelope(0.1, 0.1, 0.4, 0.25)