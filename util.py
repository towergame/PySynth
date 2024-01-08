import hashlib


def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
    """
    Linear interpolation function between two points
    :param x1: The x value of the start point
    :param x2: The x value of the end point
    :param y1: The y value of the start point
    :param y2: The y value of the end point
    :param x: The x value to interpolate for
    :return: The value y at the point x
    """
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)


# A map of notes to their frequencies in the 4th octave
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


def frequency_from_note(note_octave: str):
    """
    Returns the frequency of the given note
    :param note_octave: A string representing the note in the format <note><octave>
    :return: A float of the frequency of the note
    """
    # Read the note
    note = ""
    for char in note_octave:
        if char.isdigit():
            # Notes most definitely do not contain digits, so if we encounter one, we have reached the octave
            break
        else:
            note += char
    if note not in notes:
        # If the note is not in the map, raise an exception
        raise Exception("Invalid note: " + note)
    # Interpret the octave
    octave = int(note_octave[len(note):])
    # Return the frequency of the note based on the octave
    return notes[note] * (2 ** (octave - 4))


def delocalize_path(current_path, path):
    """
    Returns the path of the given path, relative to the current path
    :param current_path: the current path of the file
    :param path: the path to delocalize
    :return: the delocalized path
    """
    # If the path starts with /, it is absolute, so return it
    if path.startswith("/"):
        return path
    else:
        # Otherwise, return the current path + the path
        return current_path + "/" + path


def get_beat_length(beat: [str, float]):
    """
    Returns the length of the beat
    :param beat: An array of tuples containing notes and the length they should be played
    :return: A float of the length of the beat
    """
    # If the beat is a pause, return the length of the pause
    if beat[0][0] == "0":
        return float(beat[0][1:])
    else:
        # Otherwise, return the length of the shortest note
        shortest = float("inf")
        for note in beat:
            if float(note[1]) < shortest:
                shortest = float(note[1])
        return shortest


def string_to_hex_color_hash(string: str):
    """
    Returns a hex color hash of the given string
    :param string: The string to hash
    :return: A hex color string
    """
    # Hash the string and truncate it to a number that can be displayed as a hex color
    hash_num = int(hashlib.sha256(string.encode('utf-8')).hexdigest(), 16) % 16777215
    # Return the number as a hex color
    return "#" + '{0:06X}'.format(hash_num)
