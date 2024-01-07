from pynput.keyboard import KeyCode, Listener, Key
from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave_generator import WaveGenerator, WaveTypes
from classes.wave import Wave

currentlyPlaying = {
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
    print('listener starts')
    listener.join()
