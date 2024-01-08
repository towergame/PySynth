import os
from pynput.keyboard import KeyCode, Listener, Key
from classes.sound_generator import SoundGenerator
from classes.envelope import Envelope
from classes.wave_generator import WaveGenerator, WaveTypes
from classes.wave import Wave
from util import frequencyFromNote
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
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open', wildcard=wildcard, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path

noteKeys = {
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

currentlyPlaying = {}
for k, v in noteKeys.items():
    currentlyPlaying[k] = None

exit_key = Key.f12

WAVE_PRESET = [Wave(WaveTypes.SINE, 1, 1, 0),
              Wave(WaveTypes.SINE, 0.5, 0.5, 2)]
load_wave_key = Key.f1
ENVELOPE_PRESET = Envelope(0.1, 0.1, 0.4, 0.25)
load_envelope_key = Key.f2

SONG = None
load_song_key = Key.f3
play_song_key = Key.f4

def on_load_wave():
    global WAVE_PRESET
    WAVE_PRESET = load_wave_preset(get_path("*.wave.pysynth"))

def on_load_envelope():
    global ENVELOPE_PRESET
    ENVELOPE_PRESET = load_wave_preset(get_path("*.envelope.pysynth"))

def on_load_song():
    global SONG, songlen
    SONG = load_song(get_path("*.song.pysynth"))
    songlen = 0
    for b in SONG.beats:
        songlen += 1

def on_play_song():
    global SONG
    SONG.play()

def on_press(key):
    global currentlyPlaying
    # print('Key: ', key, ' was held')
    if key in noteKeys:
        if key not in currentlyPlaying:
            pass
        if currentlyPlaying[key] is not None and currentlyPlaying[key].is_alive():
            # print('already clicking')
            pass
        else:
            if currentlyPlaying[key] is not None:
                currentlyPlaying[key].stop()
                currentlyPlaying[key] = None
            currentlyPlaying[key] = SoundGenerator(ENVELOPE_PRESET, WaveGenerator(WAVE_PRESET, frequencyFromNote(noteKeys[key])))
            currentlyPlaying[key].start()
    elif key == exit_key:
        listener.stop()
    elif key == load_wave_key:
        on_load_wave()
    elif key == load_envelope_key:
        on_load_envelope()
    elif key == load_song_key:
        on_load_song()
    elif key == play_song_key:
        on_play_song()


def on_release(key):
    global currentlyPlaying
    # print('Key: ', key, ' was released')
    if key in noteKeys:
        if key not in currentlyPlaying:
            pass
        # print('key released. stopping')
        if currentlyPlaying[key] is not None:
            currentlyPlaying[key].stop()
            currentlyPlaying[key] = None

def signal_handler(sig, frame):
    os.system("stty echo")
    sys.exit(0)


class Header:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]PySynth[/b]",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on magenta")

class NoteInfo:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.title = "Notes"
        grid.add_column()
        grid.add_column()
        grid.add_row(
            "Key",
            "Note"
        )
        for k, v in currentlyPlaying.items():
            grid.add_row(
                str(k).replace("Key.", "").replace("'", ""),
                noteKeys[k],
                style="black on purple" if v is not None else ""
            )
        return Panel(grid)

class EnvelopeInfo:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.title = "Envelope"
        grid.add_column()
        grid.add_column()
        grid.add_row(
            "Section",
            "Length"
        )
        grid.add_row(
            "Attack",
            str(ENVELOPE_PRESET.a) + "s"
        )
        grid.add_row(
            "Decay",
            str(ENVELOPE_PRESET.d) + "s"
        )
        grid.add_row(
            "Sustain",
            str(ENVELOPE_PRESET.s) + "s"
        )
        grid.add_row(
            "Release",
            str(ENVELOPE_PRESET.r) + "s"
        )
        return Panel(grid)

class WaveInfo:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.title = "Wave"
        grid.add_column()
        grid.add_column()
        grid.add_row(
            "Wave",
            "Offset",
            "Amplitude",
            "Phase"
        )
        for wave in WAVE_PRESET:
            grid.add_row(
                str(wave.wave_type).replace("WaveTypes.", "").replace("'", ""),
                str(wave.offset),
                str(wave.amplitude),
                str(wave.phase)
            )
        return Panel(grid)

class ControlsInfo:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.title = "Controls"
        grid.add_column()
        grid.add_column()
        grid.add_row(
            "Key",
            "Action"
        )
        grid.add_row(
            "F1",
            "Load Wave Preset"
        )
        grid.add_row(
            "F2",
            "Load Envelope Preset"
        )
        grid.add_row(
            "F3",
            "Load Song"
        )
        grid.add_row(
            "F4",
            "Play Song"
        )
        grid.add_row(
            "F12",
            "Exit"
        )
        return Panel(grid)


class SongInfo:
    def __rich__(self) -> Panel:
            grid = Table.grid(expand=True)
            grid.title = "Song"
            grid.add_column()
            grid.add_column()
            if SONG is None:
                grid.add_row(
                    "No Song Loaded",
                    ""
                )
            else:
                grid.add_row(
                    "Title",
                    SONG.title[:-1]
                )
                grid.add_row(
                    "Length",
                    str(round(len(SONG.beats) / SONG.bpm * 60 * 100) / 100) + "s"
                )
                grid.add_row(
                    "BPM",
                    str(SONG.bpm)
                )
            return Panel(grid)

def generate_interface() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="notes", size=16),
        Layout(name="right"),
    )
    layout["right"].split_column(
        Layout(name="abov"),
        Layout(name="bott"),
    )
    layout["bott"].split_row(
        Layout(name="wave"),
        Layout(name="controls", size=40),
    )
    layout["abov"].split_row(
        Layout(name="envelope"),
        Layout(name="song"),
    )
    return layout


signal.signal(signal.SIGINT, signal_handler)
os.system("stty -echo")

layout = generate_interface()
layout["header"].update(Header())
layout["notes"].update(NoteInfo())
layout["envelope"].update(EnvelopeInfo())
layout["controls"].update(ControlsInfo())
layout["wave"].update(WaveInfo())
layout["song"].update(SongInfo())

with Listener(on_press=on_press, on_release=on_release) as listener:
    with Live(layout, screen=True, refresh_per_second=4) as live:
        live.update(layout)
        listener.join()