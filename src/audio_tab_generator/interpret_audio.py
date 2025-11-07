# --------------------------------------------------------------
# interpret_audio.py
# --------------------------------------------------------------
"""
Run basic_pitch on an audio file and write the resulting MIDI file.

The public function is :func:`predict_to_midi`.
"""

import pathlib
from typing import Tuple, List, Optional

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def predict_to_midi(
    audio_path: pathlib.Path | str,
    out_dir: pathlib.Path | str,
    *,
    model_path: pathlib.Path | str = ICASSP_2022_MODEL_PATH,
    onset_threshold: float = 0.5,
    frame_threshold: float = 0.3,
    minimum_note_length: float = 127.70,
    melodia_trick: bool = True,
    minimum_freq: float = 80,
    maximum_freq: float = 1700,
) -> Tuple[pathlib.Path, List[Tuple[float, float, int, float, Optional[List[int]]]]]:
    """
    Run ``basic_pitch.predict`` on *audio_path* and write a ``.mid`` file
    into *out_dir*.

    Returns
    -------
    midi_path : pathlib.Path
        Full path of the written MIDI file.
    note_events : list
        The raw note‑event list returned by ``basic_pitch`` (useful for debugging).
    """
    audio_path = pathlib.Path(audio_path).expanduser().resolve()
    out_dir = pathlib.Path(out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run the model
    model_output, midi_obj, note_events = predict(
        audio_path=audio_path,
        model_or_model_path=model_path,
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        minimum_note_length=minimum_note_length,
        melodia_trick=melodia_trick,
    )

    # Write the MIDI file
    midi_path = out_dir / f"{audio_path.stem}.mid"
    midi_obj.write(str(midi_path))

    return midi_path, note_events
