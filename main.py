from pynput.keyboard import KeyCode, Listener, Key
from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave_generator import WaveGenerator, WaveTypes
from classes.wave import Wave
from util import frequencyFromNote

noteKeys = {
    KeyCode(char='a'): frequencyFromNote("C4"),
    KeyCode(char='w'): frequencyFromNote("C#4"),
    KeyCode(char='s'): frequencyFromNote("D4"),
    KeyCode(char='e'): frequencyFromNote("D#4"),
    KeyCode(char='d'): frequencyFromNote("E4"),
    KeyCode(char='f'): frequencyFromNote("F4"),
    KeyCode(char='t'): frequencyFromNote("F#4"),
    KeyCode(char='g'): frequencyFromNote("G4"),
    KeyCode(char='y'): frequencyFromNote("G#4"),
    KeyCode(char='h'): frequencyFromNote("A4"),
    KeyCode(char='u'): frequencyFromNote("A#4"),
    KeyCode(char='j'): frequencyFromNote("B4"),
    KeyCode(char='k'): frequencyFromNote("C5"),
}

currentlyPlaying = {}
for k, v in noteKeys.items():
    currentlyPlaying[k] = None

exit_key = Key.f7

WAVEPRESET = [Wave(WaveTypes.SINE, 1, 1, 0),
              Wave(WaveTypes.SINE, 0.5, 0.5, 2)]


def on_press(key):
    global currentlyPlaying
    print('Key: ', key, ' was held')
    if key in noteKeys:
        if key not in currentlyPlaying:
            pass
        if currentlyPlaying[key] is not None and currentlyPlaying[key].is_alive():
            print('already clicking')
            pass
        else:
            if currentlyPlaying[key] is not None:
                currentlyPlaying[key].stop()
                currentlyPlaying[key] = None
            currentlyPlaying[key] = SoundGenerator(Envelope(0.1, 0.1, 0.4, 0.25),
                                     WaveGenerator(WAVEPRESET, noteKeys[key]))
            currentlyPlaying[key].start()
    elif key == exit_key:
        listener.stop()


def on_release(key):
    global currentlyPlaying
    print('Key: ', key, ' was released')
    if key in noteKeys:
        if key not in currentlyPlaying:
            pass
        print('key released. stopping')
        if currentlyPlaying[key] is not None:
            currentlyPlaying[key].stop()
            currentlyPlaying[key] = None


with Listener(on_press=on_press, on_release=on_release) as listener:
    console.print("PySynth")
    listener.join()
