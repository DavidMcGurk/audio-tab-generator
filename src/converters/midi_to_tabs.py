import pathlib
import pretty_midi
from typing import Optional
from src.models.note_cluster import NoteCluster
from src.models.note import NoteCandidate, FinalNote


def midi_to_guitar_tab(
    midi_path: pathlib.Path,
    out_dir: pathlib.Path,
    max_fret: int = 24,
) -> pathlib.Path:
    """
    Convert a MIDI file into guitar tablature using standard EADGBE tuning.

    Parameters
    ----------
    midi_path : Path
        Path to the input MIDI file.
    out_dir : Path
        Directory where the generated tablature (.txt) will be written.
    max_fret : int, default 24
        Highest fret number allowed when mapping notes to strings.

    Returns
    -------
    Path
        The path to the created tablature file.

    Raises
    ------
    ValueError
        If the MIDI file is invalid or contains no usable notes.

    Notes
    -----
    - Standard tuning MIDI values: E2=40, A2=45, D3=50, G3=55, B3=59, E4=64.
    - The output is a plain-text tablature with one line per string.
    """

    midi_path = pathlib.Path(midi_path).expanduser().resolve()
    out_dir = pathlib.Path(out_dir).expanduser().resolve()
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    # String tuning values (low E → high e)
    STRING_MIDI = [40, 45, 50, 55, 59, 64]
    STRING_NAMES = ["E", "A", "D", "G", "B", "e"]
    NUM_STRINGS = len(STRING_MIDI)

    out_file = out_dir / f"{midi_path.stem}.txt"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Load MIDI data and ensure validity
    try:
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
        midi_data.remove_invalid_notes()
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid MIDI file: {midi_path}") from e

    # Flatten notes and sort by onset
    notes = sorted(
        [note for inst in midi_data.instruments for note in inst.notes],
        key=lambda n: n.start,
    )

    if not notes:
        raise ValueError(f"No playable notes found in {midi_path}")

    # Convert MIDI notes into NoteCandidate objects with possible fret positions
    note_candidates = []
    for note in notes:
        candidates = []
        for string_midi in STRING_MIDI:
            fret = note.pitch - string_midi
            candidates.append(fret if 0 <= fret <= max_fret else -1)

        note_candidates.append(
            NoteCandidate(
                start_time=note.start,
                end_time=note.end,
                candidates=candidates,
            )
        )

    # Group overlapping notes into buckets
    clusters = []
    idx = 0
    while idx < len(note_candidates):
        group = [note_candidates[idx]]
        group_end_time = note_candidates[idx].end_time
        while idx + 1 < len(note_candidates) and note_candidates[idx + 1].start_time < group_end_time:
            idx += 1
            group.append(note_candidates[idx])
            group_end_time = max(group_end_time, note_candidates[idx].end_time)

        clusters.append(group)
        idx += 1

    # Let cluster determine the optimal fingering for each group
    final_notes: list[list[FinalNote]] = []
    for group in clusters:
        cluster = NoteCluster(notes=group)
        cluster.assign_notes()
        final_notes.append(cluster.optimal)

    # Create and write tablature
    with out_file.open("w") as f:
        tab_lines = [[f"{STRING_NAMES[i]}|-"] for i in range(NUM_STRINGS)]

        # Track currently ringing notes per string
        # None = not ringing; otherwise store FinalNote
        active_notes: dict[int, Optional[FinalNote]] = {}

        # Iterate cluster by cluster
        for note_cluster in final_notes:
            for note in note_cluster:
                for s in range(1, 7):
                    active = active_notes.get(s)

                    # Case 1: Note is played on string
                    if note.string == s:
                        tab_lines[s - 1].append(f"{note.fret}")
                        active_notes[s] = note
                        continue

                    # Case 2: Note is ringing on string
                    if active is not None:
                        if active.end_time <= note.start_time:
                            active_notes[s] = None
                            tab_lines[s - 1].append("-")
                        else:
                            tab_lines[s - 1].append("~")
                        continue

                    # Case 3: nothing happening on this string
                    tab_lines[s - 1].append("-")

                # Append separator
                for s in range(NUM_STRINGS):
                    tab_lines[s - 1].append("-")

        # Finalize output
        tab_text = "\n".join("".join(line) for line in tab_lines[::-1])
        f.write(tab_text)

    return out_file
