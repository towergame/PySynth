import threading

from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave_generator import WaveGenerator
from config import DEFAULT_WAVE_PRESET, DEFAULT_ENVELOPE_PRESET
from util import frequency_from_note, get_beat_length
import time


class Song(threading.Thread):
    def __init__(self, title, beats, bpm=100, wave=None, envelope=None):
        self.title = title
        self.waves = DEFAULT_WAVE_PRESET if wave is None else wave
        self.env = DEFAULT_ENVELOPE_PRESET if envelope is None else envelope
        self.bpm = bpm
        self.beats = beats
        self.playing = False
        super().__init__()

    def run(self):
        while True:
            if self.playing:
                self.play()
            else:
                time.sleep(0.1)

    def start_playback(self):
        self.playing = True

    def stop_playback(self):
        self.playing = False

    def set_wave_preset(self, wave):
        self.waves = wave

    def set_envelope_preset(self, envelope):
        self.env = envelope

    def get_status(self):
        return self.playing

    def play(self):
        for beat in self.beats:
            if not self.playing:
                break
            if beat[0][0] == "0":
                time.sleep(60 / self.bpm * beat[0][1])
                continue
            self.play_beat(beat)
            time.sleep(60 / self.bpm * get_beat_length(beat))
        self.playing = False

    def play_beat(self, beat):
        for note in beat:
            self.play_note(note[0], note[1] * (60 / self.bpm))

    def play_note(self, note, duration):
        sound_generator = SoundGenerator(self.env, WaveGenerator(self.waves, frequency_from_note(note)), duration)
        sound_generator.start()
