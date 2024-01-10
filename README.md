# PySynth
*A CLI synthesizer written from scratch in Python*

## Format Specification
The program also accepts multiple file custom file formats in order to modify settings and/or automatically playback a song.  
The formats are as such:
- '.wave.psynth' - A file that specifies a specific waveform. Each line details a wave:  
  - The first token is the waveform type:  
    - '1' - Sine wave
    - '2' - Square wave
    - '3' - Sawtooth wave
    - '4' - Triangle wave 
  - The second token is the offset of the wave frequency (multiplication factor)
  - The third token is the amplitude of the wave
  - The fourth token is the phase of the wave
  - Example: `1 1 1 0` - A sine wave with the same frequency as the note, amplitude of 1, and phase of 0
  - Example: `2 2 0.5 0` - A triangle wave with half the frequency of the note (thus, an octave lower), amplitude of 0.5, and phase of 0
- '.envelope.psynth' - A file that specifies a specific envelope. Each line details an envelope:  
  - The first token is the envelope type:  
    - '1' - Linear envelope
  - The second token is the attack time of the envelope
  - The third token is the decay time of the envelope
  - The fourth token is the sustain level of the envelope
  - The fifth token is the release time of the envelope
  - Example: `1 0.1 0.1 0.5 0.1` - A linear envelope with an attack time of 0.1 seconds, decay time of 0.1 seconds, sustain level of 0.5, and release time of 0.1 seconds
- '.song.psynth' - A file that specifies a song. Each line details a note:  
  - The first line is the name of the song
    - This can be as long as you wish, the main criterion being that it is a single line
  - Any subsequent lines are song metainfo
    - The first token is the metainfo type:
      - '1' - BPM
        - The second token is the BPM of the song
        - By default, this will be assumed to be 100
        - Example: `1 120` - A song with a BPM of 120
      - '2' - Waveform
        - The second token is the path to the waveform (a '.wave.psynth' file)
      - '3' - Envelope 
        - The second token is the path to the envelope (a '.envelope.psynth' file)
  - The metainfo section is terminated by a line consisting of '---'
  - Any subsequent lines are notes
    - The first token is note count
    - This is then followed by the note count number of notes
      - Notes are formatted as such: `<note>:<duration>`
    - Example: `1 C4:1` - A C4 note with a duration of 1
    - Example: `2 C4:1 D4:2` - A C4 note with a duration of 1 and a D4 note with a duration of 2
    - Example: `0` - An empty beat

Additionally, all formats support `$` comments. Any line that begins with a `$` will be ignored by the program.