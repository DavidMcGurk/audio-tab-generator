# --------------------------------------------------------------
# midi_to_tabs.py
# --------------------------------------------------------------
"""
Convert MIDI file to guitar tablature (standard tuning).

Public function:
    * :func:`midi_to_guitar_tab`
"""

import pathlib
import pretty_midi
from audio_tab_generator.models.chord import Chord
from typing import Any
from audio_tab_generator.models.note import NoteCandidate


def midi_to_guitar_tab(
    midi_path: pathlib.Path, out_dir: pathlib.Path, max_fret: int = 24, time_quantization: float = 0.1
) -> pathlib.Path:
    """
    Convert MIDI file at *midi_path* to guitar tablature (standard EADGBE tuning) and write to *out_dir*.

    Parameters
    ----------
    midi_path : Path
        Path to input MIDI file.
    out_dir : Path
        Path for output tablature file (.txt).
    max_fret : int, default 22
        Maximum fret number to consider. Notes requiring higher frets will not be displayed.
    time_quantization : float, default 0.1
        Time window (seconds) for grouping simultaneous notes.
        Notes within this interval are considered simultaneous.

    Returns
    -------
    output_path : Path
        Path of the created tablature file.

    Raises
    ------
    ValueError: If MIDI file contains no playable notes.

    Notes
    -----
    - Standard tuning is used (E2=40, A2=45, D3=50, G3=55, B3=59, E4=64 in MIDI notes)
    - Displays notes chronologically with minimal fret movement heuristic
    - Doesn't show note durations or rhythmic notation
    - Chord handling is limited (notes appear sequentially)
    """
    midi_path = pathlib.Path(midi_path).expanduser().resolve()
    out_dir = pathlib.Path(out_dir).expanduser().resolve()
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    # Standard tuning MIDI note numbers (low E to high E)
    STRING_MIDI = [40, 45, 50, 55, 59, 64]
    STRING_NAMES = ["E", "A", "D", "G", "B", "e"]
    NUM_STRINGS = len(STRING_MIDI)

    midi_path = midi_path.expanduser().resolve()
    out_file = out_dir.expanduser().resolve() / f"{midi_path.stem}.txt"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Load and parse MIDI data
    try:
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
        midi_data.remove_invalid_notes()
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid MIDI file: {midi_path}") from e

    # Collect all notes
    notes = sorted([note for inst in midi_data.instruments for note in inst.notes], key=lambda n: n.start)
    if not notes:
        raise ValueError(f"No playable notes found in {midi_path}")

    note_candidates = []
    for note in notes:
        string_candidates = [-1 for _ in range(NUM_STRINGS)]
        for string in range(NUM_STRINGS):
            base = STRING_MIDI[string]
            fret = note.pitch - base
            if 0 <= fret <= max_fret:
                string_candidates[string] = fret

        note_candidates.append(NoteCandidate(start_time=note.start, end_time=note.end, candidates=string_candidates))

    chords = []
    idx = 0
    while idx < len(note_candidates):
        chord_notes = [note_candidates[idx]]
        while idx + 1 < len(note_candidates) and note_candidates[idx + 1].start_time < note_candidates[idx].end_time:
            chord_notes.append(note_candidates[idx + 1])
            idx += 1

        chords.append(chord_notes)
        idx += 1

    optimal_chords: list[list] = []
    for chord in chords:
        processed_chord = Chord(notes=chord)
        processed_chord.find_optimal()
        optimal_chords.append(processed_chord.optimal)

    with out_file.open("w") as f:
        # Initialize tab lines for each string
        tab_lines: list[Any] = [[f"{STRING_NAMES[i]}|-"] for i in range(len(STRING_NAMES))]

        for chord in optimal_chords:
            for string_idx in range(NUM_STRINGS):
                fret = chord[string_idx]
                if fret == -1:
                    tab_lines[string_idx].append("--")
                else:
                    tab_lines[string_idx].append(f"{fret}-")

        for idx, line in enumerate(tab_lines):
            tab_lines[idx] = "".join(line)

        f.write("\n".join(tab_lines))

    return out_file
