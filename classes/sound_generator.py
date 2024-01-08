import threading
import numpy as np
import soundcard as sc

from classes.wave_generator import WaveGenerator, WaveTypes
from config import BITRATE, BUFFSIZE, MAX_VOL
from util import interpolate


class SoundGenerator(threading.Thread):
    def __init__(self, envelope, wave_generator, length=-1):
        self.dead_time = -1
        self.dead_volume = -1
        self.length = length
        self.volume = 0  # range [0.0, 1.0]
        self.fs = BITRATE  # sampling rate, Hz, must be integer
        self.block_size = BUFFSIZE
        self.t = 0.0
        self.duration = self.block_size / self.fs  # in seconds, may be float
        self.dead = False
        self.envelope = envelope
        self.waveGenerator = wave_generator
        super().__init__()

    def run(self):
        with sc.default_speaker().player(samplerate=self.fs, channels=1, blocksize=self.block_size) as speaker:
            while not (self.volume <= 0 and self.t > self.envelope.a):
                if self.length != -1 and self.t > self.length and not self.dead:
                    self.stop()
                # Wrath of God
                self.volume = interpolate(self.dead_time, self.dead_time + self.envelope.r, self.dead_volume, 0.0, self.t) if self.dead \
                                else interpolate(0.0, self.envelope.a, 0.0, MAX_VOL, self.t) if self.t < self.envelope.a \
                                else interpolate(self.envelope.a, self.envelope.a + self.envelope.d, MAX_VOL, self.envelope.s * MAX_VOL, self.t) if self.t < self.envelope.a + self.envelope.d \
                                else self.envelope.s * MAX_VOL
                samples = self.waveGenerator.generate_wave(np.arange(self.t, self.t + self.duration, 1 / self.fs)).astype(np.float32)
                self.t += self.duration
                speaker.play(samples * self.volume)

    def stop(self):
        self.dead = True
        self.dead_time = self.t
        self.dead_volume = self.volume
