from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave_generator import WaveGenerator
from config import DEFAULT_WAVE_PRESET, DEFAULT_ENVELOPE_PRESET
from util import frequencyFromNote
import time

class Song:
    def __init__(self, title, beats, bpm=100, wave=None, envelope=None):
        self.title = title
        self.waves = DEFAULT_WAVE_PRESET if wave is None else wave
        self.env = DEFAULT_ENVELOPE_PRESET if envelope is None else envelope
        self.bpm = bpm
        self.beats = beats

    def play(self):
        for beat in self.beats:
            self.play_beat(beat)
            time.sleep(60 / self.bpm)

    def play_beat(self, beat):
        for note in beat:
            self.play_note(
                note[0],
                note[1] * (60 / self.bpm)
            )

    def play_note(
        self,
        note,
        duration
    ):
        sound_generator = SoundGenerator(self.env, WaveGenerator(self.waves, frequencyFromNote(note)), duration)
        sound_generator.start()
