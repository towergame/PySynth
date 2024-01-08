from classes.wave import Wave
from classes.wave_generator import WaveTypes, WaveGenerator
from classes.envelope import Envelope
from classes.song import Song
from util import delocalize_path

# Load Wave Preset
WAVE_TYPE_MAP = {
    "1": WaveTypes.SINE,
    "2": WaveTypes.SQUARE,
    "3": WaveTypes.SAWTOOTH,
    "4": WaveTypes.TRIANGLE
}

def load_wave_preset(path) -> [Wave]:
    preset = []
    with open(path, "r") as file:
        for line in file.readlines():
            if line.startswith("$"):
                continue
            else:
                wave_type = line.split(" ")[0]
                if wave_type not in WAVE_TYPE_MAP:
                    raise Exception("Invalid Wave Type")
                offset = float(line.split(" ")[1])
                amplitude = float(line.split(" ")[2])
                phase = float(line.split(" ")[3])
                preset.append(Wave(WAVE_TYPE_MAP[wave_type], offset, amplitude, phase))
    return preset

# Load Envelope Preset
def load_envelope_preset(path) -> Envelope:
    with open(path, "r") as file:
        for line in file.readlines():
            if line.startswith("$"):
                continue
            else:
                # Ignore type for now, though might be useful if more envelope types are made
                a = float(line.split(" ")[1])
                d = float(line.split(" ")[2])
                s = float(line.split(" ")[3])
                r = float(line.split(" ")[4])
                return Envelope(a, d, s, r) # The file should contain only one envelope


# Load Song
def load_song(path) -> Song:
    with open(path, "r") as file:
        reading_meta = True
        title = file.readline()
        bpm = 100
        waves = None
        envelope = None
        beats = []
        for line in file.readlines():
            # print(line, end="")
            if line.startswith("$"):
                continue
            else:
                if reading_meta:
                    if line[:3] == "---":
                        reading_meta = False
                        continue
                    else:
                        tokens = line.split(" ")
                        if tokens[0] == "1":
                            bpm = int(tokens[1])
                        elif tokens[0] == "2":
                            waves = load_wave_preset(delocalize_path(path, tokens[1]))
                        elif tokens[0] == "3":
                            envelope = load_envelope_preset(delocalize_path(path, tokens[1]))
                        else:
                            raise Exception("Invalid Meta Type")
                else:
                    beat = []
                    tokens = line.split(" ")
                    if tokens[0] != "0":
                        for note in tokens[1:]:
                            beat.append([note.split(":")[0], float(note.split(":")[1])])
                    else:
                        beat.append(["0", float(tokens[1])])
                    beats.append(beat)
        return Song(title, beats, bpm, waves, envelope)