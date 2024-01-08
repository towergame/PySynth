#!/usr/bin/env python3
import os
import time
from types import FrameType

from pynput.keyboard import KeyCode, Listener, Key
from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave_generator import WaveGenerator, WaveTypes
from classes.wave import Wave
from classes.song import Song
from config import DEFAULT_ENVELOPE_PRESET, DEFAULT_WAVE_PRESET
from util import frequency_from_note, string_to_hex_color_hash
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
import signal
import sys
from file_processing import load_wave_preset, load_envelope_preset, load_song
import wx


def get_path(wildcard):
    """
    Opens a file dialog and returns the path of the selected file
    :param wildcard: A wildcard specifying the file types to be shown
    :return: A string representing the path of the selected file
    """
    # Create an app and discard it, this is purely so the dialog logic works afaik
    _ = wx.App(None)
    # Create a file dialog
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST  # File must be openable and must exist
    dialog = wx.FileDialog(None, 'Open', wildcard=wildcard, style=style)  # Create the dialog
    if dialog.ShowModal() == wx.ID_OK:
        # If the user selected a file, return its path
        path = dialog.GetPath()
    else:
        # Otherwise, return None
        path = None
    # Destroy the dialog
    dialog.Destroy()
    # Return the path
    return path


# A map of keys to notes which will be played when the key is pressed in interactive mode
note_keys = {
    KeyCode(char='a'): "C4",
    KeyCode(char='w'): "C#4",
    KeyCode(char='s'): "D4",
    KeyCode(char='e'): "D#4",
    KeyCode(char='d'): "E4",
    KeyCode(char='f'): "F4",
    KeyCode(char='t'): "F#4",
    KeyCode(char='g'): "G4",
    KeyCode(char='y'): "G#4",
    KeyCode(char='h'): "A4",
    KeyCode(char='u'): "A#4",
    KeyCode(char='j'): "B4",
    KeyCode(char='k'): "C5"
}

# A map of keys to currently playing sound generators
currently_playing: dict[KeyCode, SoundGenerator | None] = {}
for k, v in note_keys.items():
    currently_playing[k] = None

# The key to exit the program
exit_key = Key.f12

# The current wave preset
WAVE_PRESET: [Wave] = DEFAULT_WAVE_PRESET
# Key binding to load a wave preset
load_wave_key = Key.f1
# The current envelope preset
ENVELOPE_PRESET: Envelope = DEFAULT_ENVELOPE_PRESET
# Key binding to load an envelope preset
load_envelope_key = Key.f2

# The current song
SONG: Song | None = None
# Key binding to load a song
load_song_key = Key.f3
# Key binding to play a song
play_song_key = Key.f4

# The current error message
ERROR = ""

# Listener for the interactive mode
listener: Listener | None = None


def on_load_wave():
    """
    Loads a wave preset from a file
    :return: None
    """
    # Declare global variables used in the function
    global WAVE_PRESET, ERROR
    ERROR = ""
    try:
        path = get_path("*.wave.pysynth")
        if path is None:
            # If path is none, no file was selected
            ERROR = "No Wave File Selected"
            return
        # Otherwise load the wave preset
        WAVE_PRESET = load_wave_preset(path)
    except Exception as e:
        # If an exception is raised, set the error message
        ERROR = "Failed to Read Wave Preset"


def on_load_envelope():
    """
    Loads an envelope preset from a file
    :return: None
    """
    # Declare global variables used in the function
    global ENVELOPE_PRESET, ERROR
    ERROR = ""
    try:
        path = get_path("*.envelope.pysynth")
        if path is None:
            # If path is none, no file was selected
            ERROR = "No Envelope File Selected"
            return
        # Otherwise load the envelope preset
        ENVELOPE_PRESET = load_envelope_preset(path)
    except Exception as e:
        # If an exception is raised, set the error message
        ERROR = "Failed to Read Envelope"


def on_load_song():
    """
    Loads a song from a file
    :return: None
    """
    # Declare global variables used in the function
    global SONG, ENVELOPE_PRESET, WAVE_PRESET, ERROR
    ERROR = ""
    try:
        if SONG is not None:
            # If a song is already loaded, stop it
            SONG.stop_playback()
            # Similarly, kill the thread
            SONG.kill()
            # Discard the song object as it is no longer valid
            SONG = None
        # Prompt the user for the path
        path = get_path("*.song.pysynth")
        if path is None:
            # If path is none, no file was selected
            # It makes sense to fail quietly here, as this might be intentional from the user
            ERROR = ""
            # Set SONG to None to indicate no song is selected
            return
        # Otherwise, load the song
        SONG = load_song(path)
    except Exception as e:
        # If an exception is raised, set the error message
        ERROR = "Failed to Read Song"
        return
    # Otherwise, start the song thread
    SONG.start()

    # If the envelope preset is the default, set it to the currently loaded envelope preset
    if SONG.get_envelope_preset() == DEFAULT_ENVELOPE_PRESET:
        SONG.set_envelope_preset(ENVELOPE_PRESET)
    else:
        # Otherwise, set the current envelope preset to the preset of the song
        ENVELOPE_PRESET = SONG.get_envelope_preset()

    # If the wave preset is the default, set it to the currently loaded wave preset
    if SONG.get_wave_preset() == DEFAULT_WAVE_PRESET:
        SONG.set_wave_preset(WAVE_PRESET)
    else:
        # Otherwise, set the current wave preset to the preset of the song
        WAVE_PRESET = SONG.get_wave_preset()


def on_play_song():
    """
    Plays the currently loaded song
    :return: None
    """
    # Declare global variables used in the function
    global SONG, ERROR
    if SONG is None:
        # If no song is loaded, set an error
        ERROR = "No Song Loaded"
        return
    # Otherwise, start the song
    SONG.start_playback()


def on_stop_song():
    """
    Stops the currently loaded song
    :return: None
    """
    # Declare global variables used in the function
    global SONG
    if SONG is None:
        # If no song is loaded, raise an exception
        # This should not happen, as you cannot play a song if no song is loaded
        raise Exception("Impossible State")
    # Otherwise, stop the song
    SONG.stop_playback()


def on_press(key: KeyCode):
    """
    The function called when a key is pressed
    :param key: the KeyCode of the pressed key
    :return: None
    """
    # Declare global variables used in the function
    global currently_playing, SONG, ERROR
    if key in note_keys:
        # If the key is a note key, play the note
        ERROR = ""  # Clear the error message as it is likely that the user does not care about the error anymore
        if key not in currently_playing:
            # This shouldn't happen, since the map is initialized with all the note keys
            raise Exception("Impossible State")
        if currently_playing[key] is not None and currently_playing[key].is_alive():
            # If the note bound to the key is already playing, do nothing
            pass
        else:
            # Otherwise, play the note
            if currently_playing[key] is not None:
                # If the note is not playing, but the sound generator is still alive, tell it to wrap it up
                currently_playing[key].stop()
                currently_playing[key] = None
            # Create a new sound generator, with indefinite length (as it will be killed when the key is released)
            currently_playing[key] = SoundGenerator(ENVELOPE_PRESET,
                                                    WaveGenerator(WAVE_PRESET, frequency_from_note(note_keys[key])))
            # Start the sound generator thread
            currently_playing[key].start()
    elif key == exit_key:
        # Exit key is pressed.
        # Stop the listener. This will also stop the program.
        listener.stop()
    elif key == load_wave_key:
        # Load wave preset key is pressed.
        on_load_wave()
    elif key == load_envelope_key:
        # Load envelope key is pressed.
        on_load_envelope()
    elif key == load_song_key:
        # Load song key is pressed.
        on_load_song()
    elif key == play_song_key:
        # Play/Stop song key is pressed.
        if SONG is None:
            # If no song is currently loaded, set an error.
            ERROR = "No Song Loaded"
            return
        # Otherwise, play the song if it is not playing, stop it if it is.
        if not SONG.is_playing():
            on_play_song()
        else:
            on_stop_song()


def on_release(key: KeyCode):
    """
    The function called when a key is released
    :param key: The KeyCode of the released key
    :return: None
    """
    # Declare global variables used in the function
    global currently_playing
    # Stop the sound generator bound to the key
    if key in note_keys:
        if key not in currently_playing:
            # This shouldn't happen, since the map is initialized with all the note keys
            raise Exception("Impossible State")
        if currently_playing[key] is not None:
            # If the sound generator is still alive, tell it to wrap it up
            currently_playing[key].stop()
            currently_playing[key] = None


def signal_handler(sig: int, frame: FrameType):
    """
    A function handler for when the program receives a SIGINT
    :param sig: Signal code as an integer
    :param frame: FrameType object
    :return: None
    """
    # Restore input echo in the terminal
    os.system("stty echo")
    # Exit gracefully
    sys.exit(0)


class Header:
    """
    A class representing the header of the interface
    """
    @staticmethod
    def __rich__() -> Panel:
        """
        Returns the header panel
        :return: A Panel object representing the header
        """
        # Create a grid
        grid = Table.grid(expand=True)
        # Establish a layout of
        # Name      Error       Time
        grid.add_column(justify="left")
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        # Add a row with the data displayed in the grid
        grid.add_row(
            "[b]PySynth[/b]",
            ERROR,
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        # Return the panel
        return Panel(grid,
                     # If there is an error, the background is red, otherwise it is magenta
                     style=("white on magenta" if ERROR == "" else "white on red"))


class NoteInfo:
    """
    A class representing the note information panel
    """
    @staticmethod
    def __rich__() -> Panel:
        """
        Returns the note information panel
        :return: A Panel object representing the note information panel
        """
        # Create a grid
        grid = Table.grid(expand=True)
        # Give it a title and add 2 columns
        grid.title = "Notes"
        grid.add_column()
        grid.add_column()
        # Add a row detailing what each column shows
        grid.add_row(
            "[b]Key",
            "[b]Note"
        )
        # Iterate through the currently_playing map and add a row for each key
        for key, value in currently_playing.items():
            grid.add_row(
                # The key is the key code of the note key, so we need to convert it to a string
                # and process it to display only the character
                str(key).replace("Key.", "").replace("'", ""),
                # Query the note_keys map to determine the pitch of the note
                note_keys[key],
                # If the sound generator is alive, the background is black on purple, otherwise it is the default
                # This makes the table indicate which notes are being played via the keyboard
                style="black on purple" if value is not None else ""
            )
        # Return the panel
        return Panel(grid)


class EnvelopeInfo:
    """
    A class representing the envelope information panel
    """
    @staticmethod
    def __rich__() -> Panel:
        """
        Returns the envelope information panel
        :return: A Panel object representing the envelope information panel
        """
        # Create a grid
        grid = Table.grid(expand=True)
        # Give it a title and add 2 columns
        grid.title = "Envelope"
        grid.add_column()
        grid.add_column()
        # Add a row detailing what each column shows
        grid.add_row(
            "[b]Section",
            "[b]Length"
        )
        # Add a row for each section of the envelope
        grid.add_row(
            "[i]Attack",
            str(ENVELOPE_PRESET.a) + "s"
        )
        grid.add_row(
            "[i]Decay",
            str(ENVELOPE_PRESET.d) + "s"
        )
        grid.add_row(
            "[i]Sustain",
            str(ENVELOPE_PRESET.s) + "s"
        )
        grid.add_row(
            "[i]Release",
            str(ENVELOPE_PRESET.r) + "s"
        )
        # Return the panel
        return Panel(grid)


class WaveInfo:
    """
    A class representing the wave information panel
    """
    @staticmethod
    def __rich__() -> Panel:
        """
        Returns the wave information panel
        :return: A Panel object representing the wave information panel
        """
        # Create a grid
        grid = Table.grid(expand=True)
        # Give it a title and add 4 columns
        grid.title = "Wave"
        grid.add_column()
        grid.add_column()
        grid.add_column()
        grid.add_column()
        # Add a row detailing what each column shows
        grid.add_row(
            "[b]Wave",
            "[b]Offset",
            "[b]Amplitude",
            "[b]Phase"
        )
        # Add a row for each wave in the wave preset
        for wave in WAVE_PRESET:
            grid.add_row(
                # The wave type is an enum, so we need to convert it to a string and process it to display only the
                # wave type
                str(wave.wave_type).replace("WaveTypes.", "").replace("'", ""),
                # The rest of the data is floats, so we can just convert them to strings
                str(wave.offset),
                str(wave.amplitude),
                str(wave.phase)
            )
        # Return the panel
        return Panel(grid)


class ControlsInfo:
    """
    A class representing the controls information panel
    """
    @staticmethod
    def __rich__() -> Panel:
        """
        Returns the controls information panel
        :return: A panel object representing the controls information panel
        """
        # Create a grid
        grid = Table.grid(expand=True)
        # Give it a title and add 2 columns
        grid.title = "Controls"
        grid.add_column()
        grid.add_column()
        # Add a row detailing what each column shows
        grid.add_row(
            "[b]Key",
            "[b]Action"
        )
        # Add a row for each key binding
        grid.add_row(
            "[u]F1",
            "Load Wave Preset"
        )
        grid.add_row(
            "[u]F2",
            "Load Envelope Preset"
        )
        grid.add_row(
            "[u]F3",
            "Load Song"
        )
        grid.add_row(
            "[u]F4",
            "Play Song" if SONG is None or not SONG.is_playing() else "Stop Song"
        )
        # Add a blank row to separate the exit key a bit
        grid.add_row()
        grid.add_row(
            "[u]F12",
            "Exit",
        )
        # Return the panel
        return Panel(grid)


class SongInfo:
    """
    A class representing the song information panel
    """
    @staticmethod
    def __rich__() -> Panel:
        """
        Returns the song information panel
        :return: A Panel object representing the song information panel
        """
        # Create a grid
        grid = Table.grid(expand=True)
        # Give it a title and add 2 columns
        grid.title = "Song"
        grid.add_column()
        grid.add_column()
        # Generate rows for the song info
        if SONG is None:
            # If no song is loaded, display a message
            grid.add_row(
                "[u]No Song Loaded",
                ""
            )
        else:
            # Otherwise, display the song info
            grid.add_row(
                "[b]Title",
                # The title is a string, so we need to process it to remove the newline character
                SONG.title[:-1]
            )
            grid.add_row(
                "[b]BPM",
                # The BPM is an integer, so we can just convert it to a string
                str(SONG.bpm)
            )
        # Return the panel
        return Panel(grid)


def generate_interface() -> Layout:
    """
    Generates the interface layout
    :return: A Layout object representing the interface layout
    """
    # Initialize the layout
    layout = Layout()
    # Split off the header at the top
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    # Split the body into 2 columns, one for the notes and one for the rest
    layout["body"].split_row(
        Layout(name="notes", size=16),
        Layout(name="right"),
    )
    # Split the right column into 2 rows
    layout["right"].split_column(
        Layout(name="abov"),
        Layout(name="bott"),
    )
    # Split the bottom row into 2 columns, one for wave info and the other for controls
    layout["bott"].split_row(
        Layout(name="wave"),
        Layout(name="controls", size=40),
    )
    # Split the top row into 2 columns, one for envelope info and the other for song info
    layout["abov"].split_row(
        Layout(name="envelope"),
        Layout(name="song"),
    )
    # Return the layout
    return layout


def interactive_mode():
    """
    Starts the interactive mode, which displays an interface in the terminal and listens for key presses
    :return: None
    """
    # Define global variables
    global listener
    # Bind the signal handler to SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    # Disable input echo in the terminal
    os.system("stty -echo")

    # Generate the interface
    interface = generate_interface()
    # Bind information display classes to the respective layout elements
    interface["header"].update(Header())
    interface["notes"].update(NoteInfo())
    interface["envelope"].update(EnvelopeInfo())
    interface["controls"].update(ControlsInfo())
    interface["wave"].update(WaveInfo())
    interface["song"].update(SongInfo())

    # Listen for key presses with the listener
    with Listener(on_press=on_press, on_release=on_release) as listener_local:
        # Update the interface with the Live object from rich
        with Live(interface, screen=True, refresh_per_second=4) as live:
            # Update the interface until the listener stops
            live.update(interface)
            # Set the global listener to the local listener
            listener = listener_local
            listener_local.join()

    # Upon exit, restore input echo in the terminal
    os.system("stty echo")


# Read the arguments
arguments = sys.argv
# Create a rich console object
console = Console()


def print_help():
    """
    Prints the help message
    :return: None
    """
    console.print(f"Usage: {arguments[0]} [arguments]")
    console.print()
    console.print("Mode Arguments:")
    console.print("  -i, --interactive: Starts the interactive mode (requires tty)")
    console.print("  -h, --help: Prints this help message")
    console.print()
    console.print("File Arguments:")
    console.print("  -w, --wave: Path to a wave preset file")
    console.print("  -e, --envelope: Path to an envelope preset file")
    console.print("  -s, --song: Path to a song file")
    console.print()
    console.print("Note: The file arguments are ignored if ran in interactive mode")


if len(arguments) == 1:
    # Print the help message if no arguments are provided
    print_help()
else:
    interactive = False
    for i in range(len(arguments)):
        # Iterate through the arguments
        if arguments[i] in ["-i", "--interactive"]:
            # If the argument is -i or --interactive, start the interactive mode
            # Check if the program is running in a tty
            if not sys.stdin.isatty():
                console.print("Interactive mode requires a tty")
                break
            interactive = True
            interactive_mode()
            break
        elif arguments[i] in ["-h", "--help"]:
            # If the argument is -h or --help, print the help message
            print_help()
            break
        elif arguments[i] in ["-w", "--wave"]:
            # If the argument is -w or --wave, load the wave preset
            try:
                WAVE_PRESET = load_wave_preset(arguments[i + 1])
            except Exception as e:
                console.print("Failed to load wave preset")
                break
        elif arguments[i] in ["-e", "--envelope"]:
            # If the argument is -e or --envelope, load the envelope preset
            try:
                ENVELOPE_PRESET = load_envelope_preset(arguments[i + 1])
            except Exception as e:
                console.print("Failed to load envelope preset")
                break
        elif arguments[i] in ["-s", "--song"]:
            # If the argument is -s or --song, load the song
            try:
                SONG = load_song(arguments[i + 1])
                SONG.start()
            except Exception as e:
                console.print("Failed to load song")
                break
    if not interactive:
        if SONG is not None:
            # If a song is loaded, play it
            # Generate a color from the song title
            color = string_to_hex_color_hash(SONG.title)
            # Print a message that playback has begun
            console.print(f"[bold {color}]\[{SONG.title}][/] Beginning playback...")
            SONG.start_playback()
            while SONG.is_playing():
                # Wait until the song is finished playing
                time.sleep(0.1)
            # Kill the song thread
            SONG.kill()
            # After the playback has finished, print a message that playback has finished
            console.print(f"[bold {color}]\[{SONG.title}][/] Finished playback!")
        else:
            # Otherwise, print the help message
            print_help()
