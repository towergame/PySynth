def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
    """Perform linear interpolation for x between (x1,y1) and (x2,y2) """
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)


def frequency_from_note(note: str):
    octave = int(note[-1])
    note = note[:-1]
    notes = {
        "C": 261.63,
        "C#": 277.18,
        "D": 293.66,
        "D#": 311.13,
        "E": 329.63,
        "F": 349.23,
        "F#": 369.99,
        "G": 392.00,
        "G#": 415.30,
        "A": 440.00,
        "A#": 466.16,
        "B": 493.88
    }
    return notes[note] * (2 ** (octave - 4))


def delocalize_path(current_path, path):
    if path.startswith("/"):
        return path
    else:
        return current_path + "/" + path


def get_beat_length(beat: [str, float]):
    if beat[0][0] == "0":
        return float(beat[0][1:])
    else:
        shortest = float("inf")
        for note in beat:
            if float(note[1]) < shortest:
                shortest = float(note[1])
        return shortest
