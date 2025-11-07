# --------------------------------------------------------------
# generate_tabs.py
# --------------------------------------------------------------
"""
Convert MIDI file to guitar tablature (standard tuning).

Public function:
    * :func:`midi_to_guitar_tab`
"""

import pathlib
import pretty_midi


def midi_to_guitar_tab(
    midi_path: pathlib.Path,
    out_dir: pathlib.Path,
    *,
    max_fret: int = 22,
) -> pathlib.Path:
    """
    Convert *midi_file* to guitar tablature (standard EADGBE tuning) and write to *output_file*.

    Parameters
    ----------
    midi_path : Path | str
        Path to input MIDI file.
    out_dir : Path | str
        Path for output tablature file (.txt).
    max_fret : int, default 22
        Maximum fret number to consider. Notes requiring higher frets will not be displayed.

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

    try:
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid MIDI file: {midi_path}") from e

    # Collect and sort all notes by start time
    all_notes = sorted((note for inst in midi_data.instruments for note in inst.notes), key=lambda n: n.start)

    if not all_notes:
        raise ValueError(f"No playable notes found in MIDI file: {midi_path}")

    # Assign each note to optimal string
    fret_assignments: dict[int, list[int]] = {i: [] for i in range(6)}
    for note in all_notes:
        best_string = None
        for i, base_note in enumerate(STRING_MIDI):
            fret = note.pitch - base_note
            if 0 <= fret <= max_fret:
                if best_string is None or fret < (note.pitch - STRING_MIDI[best_string]):
                    best_string = i

        if best_string is not None:
            fret_assignments[best_string].append(note.pitch - STRING_MIDI[best_string])

    # Build tab output (reverse order: high e string first)

    out_dir = out_dir / f"{midi_path.stem}.txt"
    with out_dir.open("w") as f:
        for i in range(5, -1, -1):
            frets = "-".join(map(str, fret_assignments[i])) if fret_assignments[i] else ""
            f.write(f"{STRING_NAMES[i]}|--{frets}--\n")

    print(f"Generated guitar tab at: {out_dir}")
    return out_dir
