import threading
import numpy as np
import soundcard as sc
from config import BITRATE, BUFFER_SIZE, MAX_VOL
from util import interpolate


class SoundGenerator(threading.Thread):
    """
    A class representing a sound generator (a thread which produces a wave with a specific frequency)

    A SoundGenerator is "dead" when the key is released, after which it will run for r seconds (release time)
    in order to gradually fade out

    Attributes
    ----------
    dead_time : float
        The time at which the sound generator died
    dead_volume : float
        The volume at which the sound generator died
    length : float
        The length of the sound generator in seconds, -1 if infinite
        This is mainly used for song playback
    volume : float
        The volume of the sound generator, range [0.0, 1.0]
    fs : int
        The sampling rate of the sound generator, read from config.py
    block_size : int
        The block size of the sound generator, read from config.py
    t : float
        The current time of the sound generator
    duration : float
        The duration of each individual block
    dead : bool
        Whether the sound generator is dead
    envelope : Envelope
        The envelope of the sound generator
    waveGenerator : WaveGenerator
        The wave generator of the sound generator

    Methods
    -------
    run()
        The main loop of the sound generator
    stop()
        Stops the sound generator
    """

    def __init__(self, envelope, wave_generator, length=-1):
        """
        Constructs the object
        :param envelope: The envelope to be used by the sound generator
        :param wave_generator: The wave generator to be used by the sound generator
        :param length: The length (if any) the sound generator should remain active.
            If unspecified, the generator will play forever until stop() is called.
        """
        # Instantiate dead time and volume, these will be used later
        self.dead_time = -1
        self.dead_volume = -1
        # Set length
        self.length = length
        # Volume starts out at 0
        self.volume = 0  # range [0.0, 1.0]
        # Both of these will be read from config.py
        self.fs = BITRATE
        self.block_size = BUFFER_SIZE
        # Instantiate time and duration
        self.t = 0.0
        self.duration = self.block_size / self.fs  # in seconds, may be float
        # The generator starts out active
        self.dead = False
        # Set envelope and wave generator
        self.envelope = envelope
        self.waveGenerator = wave_generator
        super().__init__()

    def run(self):
        """
        The main loop of the sound generator
        :return: None
        """
        # Use sc to get the default speaker, this will be used to play the generated waveform
        with sc.default_speaker().player(samplerate=self.fs, channels=1, blocksize=self.block_size) as speaker:
            while not (self.volume <= 0 and self.t > self.envelope.a):
                # The generator will stop generating when the volume is 0,
                # and we are not in the attack segment of the envelope
                if self.length != -1 and self.t > self.length and not self.dead:
                    # If the generator has a specified length, and we have exceeded that length, stop the generator
                    self.stop()
                # Calculate the volume of the generator from the envelope
                # TODO: Refactor this to the Envelope class
                self.volume = interpolate(self.dead_time, self.dead_time + self.envelope.r, self.dead_volume, 0.0,
                                          self.t) if self.dead \
                    else interpolate(0.0, self.envelope.a, 0.0, MAX_VOL, self.t) if self.t < self.envelope.a \
                    else interpolate(self.envelope.a, self.envelope.a + self.envelope.d, MAX_VOL,
                                     self.envelope.s * MAX_VOL, self.t) if self.t < self.envelope.a + self.envelope.d \
                    else self.envelope.s * MAX_VOL
                # Generate the waveform for the current block
                samples = self.waveGenerator.generate_wave(
                    np.arange(self.t, self.t + self.duration, 1 / self.fs)).astype(np.float32)
                # TODO: Add support for sound filtering
                # Increment time
                self.t += self.duration
                # Play the waveform
                speaker.play(samples * self.volume)

    def stop(self):
        """
        Stops the sound generator
        :return: None
        """
        # Set dead to True, this will cause the generator to start fading out
        self.dead = True
        # Record the time and volume at which the generator is stopped, this is used to interpolate the fade out
        self.dead_time = self.t
        self.dead_volume = self.volume
