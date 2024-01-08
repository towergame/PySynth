import threading

from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave import Wave
from classes.wave_generator import WaveGenerator
from config import DEFAULT_WAVE_PRESET, DEFAULT_ENVELOPE_PRESET
from util import frequency_from_note, get_beat_length
import time


class Song(threading.Thread):
    """
    A class representing a song (a collection of beats)

    Attributes
    ----------
    title : str
        The title of the song (for display purposes)
    beats : [[(str, float)]]
        A list of beats, where each beat is a list of notes, where each note is a tuple of (note, duration)
        A notable exception are pauses, which are represented as a single note with a note of "0"
        and a duration of the pause
    bpm : int
        The beats per minute measure of the song
    waves : [Wave]
        The wave preset which will be used for the song
    env : Envelope
        The envelope preset which will be used for the song
    playing : bool
        Whether the song is currently playing
    active : bool
        Whether the song thread is active

    Methods
    -------
    start_playback()
        Starts playback of the song
    stop_playback()
        Stops playback of the song
    set_wave_preset(wave)
        Sets the wave preset to the given Wave list
    get_wave_preset()
        Returns the current wave preset
    set_envelope_preset(envelope)
        Sets the envelope preset to the given Envelope
    get_envelope_preset()
        Returns the current envelope preset
    is_playing()
        Returns whether the song is currently playing
    start_playback()
        Begins playing the song
    stop_playback()
        Stops playing the song
    """

    def __init__(self, title: str,
                 beats: [[(str, float)]],
                 bpm: int = 100,
                 wave: [Wave] = None,
                 envelope: Envelope | None = None):
        """
        Constructs the object

        Parameters
        :param title: Title of the song, used for display purposes
        :param beats: A list of beats, where each beat is a list of notes, where each note is a tuple of (note, duration)
            A notable exception are pauses, which are represented as a single note with a note of "0"
            and a duration of the pause
        :param bpm: The beats per minute measure of the song
        :param wave: The wave preset which will be used for the song
        :param envelope: The envelope preset which will be used for the song
        """
        self.title = title
        self.waves = DEFAULT_WAVE_PRESET if wave is None else wave
        self.env = DEFAULT_ENVELOPE_PRESET if envelope is None else envelope
        self.bpm = bpm
        self.beats = beats
        self.playing = False
        self.active = True
        super().__init__()

    def run(self):
        """
        The main loop of the thread, which plays the song, if the song is playing
        :return: None
        """
        while self.active:
            if self.playing:
                self.__play()
            else:
                time.sleep(0.1)

    def start_playback(self):
        """
        Tells the object to begin playback of the song
        :return: None
        """
        self.playing = True

    def stop_playback(self):
        """
        Tells the object to stop playback of the song
        :return: None
        """
        self.playing = False

    def set_wave_preset(self, wave: [Wave]):
        """
        Sets the wave preset to the given Wave list
        :param wave: The list of waves to set the wave preset to
        :return: None
        """
        self.waves = wave

    def get_wave_preset(self):
        """
        Returns the current wave preset
        :return: A list of waves representing the current wave preset of the song
        """
        return self.waves

    def set_envelope_preset(self, envelope):
        """
        Sets the envelope preset to the given Envelope
        :param envelope: The Envelope to set the envelope preset to
        :return: None
        """
        self.env = envelope

    def get_envelope_preset(self):
        """
        Returns the current envelope preset
        :return: An Envelope object representing the current envelope preset of the song
        """
        return self.env

    def is_playing(self):
        """
        Returns whether the song is currently playing
        :return: A boolean whether the song is currently playing
        """
        return self.playing

    def kill(self):
        """
        Kills the song thread
        :return: None
        """
        self.active = False

    def __play(self):
        """
        The main loop of the playback, which plays the song
        :return: None
        """
        for beat in self.beats:
            if not self.playing:  # If self.playing is no longer True, it means we must stop
                break
            if beat[0][0] == "0":  # 0 indicates that this is a pause
                time.sleep(60 / self.bpm * beat[0][1])  # Pause for the time specified
                continue
            self.__play_beat(beat)  # Otherwise, play the notes in the beat
            # The shortest note in the beat should indicate the time until the next beat should be played
            time.sleep(60 / self.bpm * get_beat_length(beat))
        self.playing = False  # Once the song is done, change self.playing to false as we are done

    def __play_beat(self, beat):
        """
        Plays the notes in the given beat
        :param beat: An array of tuples containing notes and the length they should be played
        :return: None
        """
        for note in beat:
            self.__play_note(note[0], note[1] * (60 / self.bpm)) # Play the note for the specified length

    def __play_note(self, note, duration):
        """
        Plays the given note for the given duration
        :param note: A string representing the note to play
        :param duration: A float representing the duration to play the note for
        :return: None
        """
        # Instantiate the SoundGenerator with the given envelope and wave preset
        sound_generator = SoundGenerator(self.env, WaveGenerator(self.waves, frequency_from_note(note)), duration)
        # Start the SoundGenerator thread which will begin playback
        sound_generator.start()
