from classes.wave import Wave
from classes.wave_generator import WaveTypes, WaveGenerator
from classes.envelope import Envelope
from classes.song import Song
from util import delocalize_path

# A map of wave types in the .wave.pysynth format spec to their respective WaveTypes
WAVE_TYPE_MAP = {
    "1": WaveTypes.SINE,
    "2": WaveTypes.SQUARE,
    "3": WaveTypes.SAWTOOTH,
    "4": WaveTypes.TRIANGLE
}

def load_wave_preset(path: str) -> [Wave]:
    """
    Loads a wave preset from the given path
    :param path: a file path leading to a valid .wave.pysynth format file
    :return: A wave preset expressed as a list of Wave objects
    """
    preset = [] # Instantiate the list
    # Open the file
    with open(path, "r") as file:
        # Read each line
        for line in file.readlines():
            # If the line starts with $, it's a comment - ignore it
            if line.startswith("$"):
                continue
            else:
                # Otherwise, parse the line
                tokens = line.split(" ")
                wave_type = tokens[0]
                if wave_type not in WAVE_TYPE_MAP:
                    # If the wave type cannot be mapped - the file is invalid, raise an exception
                    raise Exception("Invalid Wave Type")
                # Otherwise, parse the rest of the line
                if len(tokens) != 4:
                    # If the line is not of the correct length, raise an exception
                    raise Exception("Invalid Wave Format")
                # Otherwise, parse the rest of the line into the respective variables
                offset = float(tokens[1])
                amplitude = float(tokens[2])
                phase = float(tokens[3])
                # Append the wave to the list
                preset.append(Wave(WAVE_TYPE_MAP[wave_type], offset, amplitude, phase))
    return preset  # Return the list


def load_envelope_preset(path: str) -> Envelope:
    """
    Loads an envelope preset from the given path
    :param path: a file path leading to a valid .envelope.pysynth format file
    :return: An envelope preset expressed as an Envelope object
    """
    # Open the file
    with open(path, "r") as file:
        # Read each line
        for line in file.readlines():
            # If the line starts with $, it's a comment - ignore it
            if line.startswith("$"):
                continue
            else:
                tokens = line.split(" ")
                if len(tokens) != 5:
                    # If the line is not of the correct length, raise an exception
                    raise Exception("Invalid Envelope Format")
                # Ignore type for now, though might be useful if more envelope types are made
                # Parse the rest into variables
                a = float(tokens[1])
                d = float(tokens[2])
                s = float(tokens[3])
                r = float(tokens[4])
                # The file should contain only one envelope, thus we can return
                # immediately after parsing
                return Envelope(a, d, s, r)



def load_song(path: str) -> Song:
    """
    Loads a song from the given path
    :param path: a file path leading to a valid .song.pysynth format file
    :return: A Song object containing the parsed song
    """
    # Open the file
    with open(path, "r") as file:
        # Until we reach the end of the meta section, we are reading metadata
        reading_meta = True
        # The first line is always the title of the song
        title = file.readline().strip('\n')
        # Assume some default values
        bpm = 100
        waves = None
        envelope = None
        # Instantiate the list of beats
        beats = []
        for line in file.readlines():
            # If the line starts with $, it's a comment - ignore it
            if line.startswith("$"):
                continue
            else:
                if reading_meta:
                    # If while reading metadata we find a line consisting of ---, end the metadata section
                    if line[:3] == "---":
                        reading_meta = False
                        continue
                    else:
                        # Otherwise, interpret which metadata we are reading
                        tokens = line.split(" ")
                        # Get the directory
                        directory_path = "/".join(path.split("/")[:-1])
                        # Type 1 indicates that the line defines BPM
                        if tokens[0] == "1":
                            bpm = int(tokens[1])
                        # Type 2 indicates that the line defines the wave preset which should be used
                        elif tokens[0] == "2":
                            waves = load_wave_preset(delocalize_path(directory_path, tokens[1].strip('\n')))
                        # Type 3 indicates that the line defines the envelope preset which should be used
                        elif tokens[0] == "3":
                            envelope = load_envelope_preset(delocalize_path(directory_path, tokens[1].strip('\n')))
                        else:
                            # If the type is not recognized, raise an exception
                            raise Exception("Invalid Meta Type")
                else:
                    # If we are not in the metadata reading mode, then every line is guaranteed to be a beat
                    beat = []
                    tokens = line.split(" ")
                    # If the beat consists of more than one note, parse each note
                    if tokens[0] != "0":
                        if len(tokens) - 1 != int(tokens[0]):
                            # If the number of notes does not match the number of notes specified, raise an exception
                            raise Exception("Invalid Beat Format at beat " + str(len(beats) + 1))
                        for note in tokens[1:]:
                            # Parse each note into a tuple of (note, duration)
                            beat.append([note.split(":")[0], float(note.split(":")[1])])
                    else:
                        # If the beat is a pause, parse it into a tuple of ("0", duration)
                        beat.append(["0", float(tokens[1])])
                    beats.append(beat)  # Append the beat to the list of beats
        return Song(title, beats, bpm, waves, envelope)  # Instantiate a song object with the parsed data and return it
