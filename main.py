import math
import threading
from pynput.keyboard import KeyCode, Listener, Key
import time
# import curses
import os

# import alsaaudio
import numpy as np
# import pyaudio
import soundcard as sc
# import matplotlib.pyplot as plt
# p = pyaudio.PyAudio()

MAX_VOL = 0.6
BITRATE = 44100
BUFFSIZE = 4096


# with sc.default_speaker().player(samplerate=fs, channels=1, blocksize=blocksize) as speaker:
#    while True:
#        samples = (np.sin(2 * np.pi * np.arange(t, t + duration, 1/fs) * f)).astype(np.float32)
#        t += duration
#        speaker.play(samples * volume)
#        # print(f)

class Envelope:
    def __init__(self, a, d, s,r):
        self.a = a
        self.d = d
        self.s = s
        self.r = r

def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
    """Perform linear interpolation for x between (x1,y1) and (x2,y2) """
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)

class WaveGenerator(threading.Thread):
    def __init__(self, freq, envelope):
        self.deadTime = -1
        self.volume = 0  # range [0.0, 1.0]
        self.fs = BITRATE  # sampling rate, Hz, must be integer
        self.blocksize = BUFFSIZE
        self.f = freq  # sine frequency, Hz, may be float
        self.t = 0.0
        self.duration = self.blocksize / self.fs  # in seconds, may be float
        self.dead = False
        self.envelope = envelope
        super().__init__()

    def run(self):
        with sc.default_speaker().player(samplerate=self.fs, channels=1, blocksize=self.blocksize) as speaker:
            while not (self.volume <= 0 and self.t > self.envelope.a):
                # Wrath of God
                self.volume = interpolate(self.deadTime, self.deadTime + self.envelope.r, self.deadVolume, 0.0, self.t) if self.dead \
                                else interpolate(0.0, self.envelope.a, 0.0, MAX_VOL, self.t) if self.t < self.envelope.a \
                                else interpolate(self.envelope.a, self.envelope.a + self.envelope.d, MAX_VOL, self.envelope.s * MAX_VOL, self.t) if self.t < self.envelope.a + self.envelope.d \
                                else self.envelope.s * MAX_VOL
                samples = (np.sin(2 * np.pi * np.arange(self.t, self.t + self.duration, 1 / self.fs) * self.f)).astype(
                    np.float32)
                self.t += self.duration
                speaker.play(samples * self.volume)

    def stop(self):
        self.dead = True
        self.deadTime = self.t
        self.deadVolume = self.volume

    def getFreq(self):
        return self.f


ar = {
    KeyCode(char='a'): None,
    KeyCode(char='s'): None,
    KeyCode(char='d'): None,
    KeyCode(char='f'): None,
    KeyCode(char='g'): None,
    KeyCode(char='h'): None,
    KeyCode(char='j'): None,
    KeyCode(char='k'): None,
}

noteKeys = {
    KeyCode(char='a'): 261.63,  # C4
    KeyCode(char='s'): 293.665,  # D
    KeyCode(char='d'): 329.628,  # E
    KeyCode(char='f'): 349.228,  # F
    KeyCode(char='g'): 391.995,  # G
    KeyCode(char='h'): 440,  # A
    KeyCode(char='j'): 493.883,  # B
    KeyCode(char='k'): 523.25,  # C5
}
exit_key = Key.f7


def on_press(key):
    global ar
    print('Key: ', key, ' was held')
    if key in noteKeys:
        if key not in ar:
            pass
        if ar[key] is not None and ar[key].getFreq() == noteKeys[key]:
            print('already clicking')
            pass
        else:
            if ar[key] is not None:
                ar[key].stop()
                ar[key] = None
            ar[key] = WaveGenerator(noteKeys[key], Envelope(0.1, 0.1, 0.4, 0.25))
            ar[key].start()
    elif key == exit_key:
        listener.stop()

def on_release(key):
    global ar
    print('Key: ', key, ' was released')
    if key in noteKeys:
        if key not in ar:
            pass
        print('key released. stopping')
        if ar[key] is not None:
            ar[key].stop()
            ar[key] = None


with Listener(on_press=on_press, on_release=on_release) as listener:
    print('listener starts')
    listener.join()