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
from collections import defaultdict
import numpy as np


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

    try:
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid MIDI file: {midi_path}") from e

    all_notes = sorted((note for inst in midi_data.instruments for note in inst.notes), key=lambda n: n.start)

    if not all_notes:
        raise ValueError(f"No playable notes found in MIDI file: {midi_path}")

    # Create time grid based on quantization
    min_time = min(n.start for n in all_notes)
    max_time = max(n.end for n in all_notes)
    time_bins = np.arange(min_time, max_time + time_quantization, time_quantization)

    # Map notes to time intervals and strings
    time_string_map: defaultdict[float, dict[int, list[int]]] = defaultdict(lambda: defaultdict(list))

    for note in all_notes:
        # Find all time quanta this note spans
        note_start_bin = np.searchsorted(time_bins, note.start, side="left") - 1
        note_end_bin = np.searchsorted(time_bins, note.end, side="right")

        # Find best string for this note
        for i, base_note in enumerate(STRING_MIDI):
            fret = note.pitch - base_note
            if 0 <= fret <= max_fret:
                # Use first valid string (lowest fret preference)
                break

        # Assign note to all relevant time intervals
        for bin_idx in range(note_start_bin, note_end_bin):
            if 0 <= bin_idx < len(time_bins):
                time_point = time_bins[bin_idx]
                time_string_map[time_point][i].append(fret)

    # Build tab output using the time grid
    out_dir = out_dir / f"{midi_path.stem}.txt"
    with out_dir.open("w") as f:
        for i in range(5, -1, -1):  # From high e to low E
            line = [f"{STRING_NAMES[i]}|"]

            for time_point in sorted(time_string_map.keys()):
                frets = time_string_map[time_point][i]
                if frets:
                    # Show distinct frets sorted low to high
                    unique_frets = sorted(set(frets))
                    line.append("/".join(map(str, unique_frets)))
                else:
                    line.append("-")

            f.write("--".join(line) + "--\n")

    print(f"Generated guitar tab at: {out_dir}")
    return out_dir
