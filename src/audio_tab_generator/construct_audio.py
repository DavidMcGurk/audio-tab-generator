# --------------------------------------------------------------
# construct_audio.py
# --------------------------------------------------------------
"""
Render a MIDI file to WAV (using FluidSynth) and optionally convert to MP3.

Public helpers:
    * :func:`midi_to_wav`
    * :func:`wav_to_mp3`
    * :func:`render_midi_to_audio`
"""

import pathlib

from pydub import AudioSegment
import subprocess


def midi_to_wav(
    midi_path: pathlib.Path | str,
    wav_path: pathlib.Path | str,
    soundfont_path: pathlib.Path | str,
    sample_rate: int = 44100,
) -> pathlib.Path:
    """
    Convert *midi_path* → *wav_path* using FluidSynth via direct CLI call.

    Returns
    -------
    wav_path : pathlib.Path
        Path of the created WAV file.

    Raises
    ------
    RuntimeError: If fluidsynth command fails.
    """
    midi_path = pathlib.Path(midi_path).expanduser().resolve()
    wav_path = pathlib.Path(wav_path).expanduser().resolve()
    soundfont_path = pathlib.Path(soundfont_path).expanduser().resolve()

    cmd = [
        "fluidsynth",
        "-ni",
        "-F",
        str(wav_path),
        "-r",
        str(sample_rate),
        str(soundfont_path),
        str(midi_path),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"FluidSynth failed with error {e.returncode}:\n" f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        ) from e

    return wav_path


def wav_to_mp3(
    wav_path: pathlib.Path | str,
    mp3_path: pathlib.Path | str,
    bitrate: str = "192k",
) -> pathlib.Path:
    """
    Convert a WAV file to MP3 using *ffmpeg* (via pydub).

    Returns
    -------
    mp3_path : pathlib.Path
        Path of the created MP3 file.
    """
    wav_path = pathlib.Path(wav_path).expanduser().resolve()
    mp3_path = pathlib.Path(mp3_path).expanduser().resolve()

    # pydub automatically calls ffmpeg; raise a helpful error if it is missing.
    try:
        audio = AudioSegment.from_wav(str(wav_path))
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Failed to load WAV. Is ffmpeg installed and on your PATH?") from exc

    audio.export(str(mp3_path), format="mp3", bitrate=bitrate)
    return mp3_path


def render_midi_to_audio(
    midi_path: pathlib.Path,
    out_dir: pathlib.Path,
    soundfont_path: pathlib.Path,
    generate_wav: bool = False,
    generate_mp3: bool = False,
    sample_rate: int = 44100,
    mp3_bitrate: str = "192k",
) -> dict:
    """
    High‑level helper that does the whole “MIDI → WAV → (MP3)” pipeline.

    Parameters
    ----------
    midi_path : Path
        Input MIDI file.
    out_dir : Path
        Directory where *song.wav* and (optionally) *song.mp3* will be stored.
    soundfont_path : Path
        FluidSynth SoundFont (*.sf2*). Required.
    generate_mp3 : bool, default True
        If ``True`` also produce an MP3 file.
    sample_rate : int, default 44100
        Sample rate for the intermediate WAV.
    mp3_bitrate : str, default "192k"
        Bitrate passed to ffmpeg when creating the MP3.

    Returns
    -------
    dict
        ``{'wav': Path, 'mp3': Path (if generated)}``
    """
    midi_path = pathlib.Path(midi_path)
    out_dir = pathlib.Path(out_dir.expanduser().resolve())
    out_dir.mkdir(parents=True, exist_ok=True)

    wav_path = out_dir / f"{midi_path.stem}.wav"
    wav_path = midi_to_wav(
        midi_path=midi_path,
        wav_path=wav_path,
        soundfont_path=soundfont_path,
        sample_rate=sample_rate,
    )

    result = {"wav": wav_path} if generate_wav else dict()
    if generate_mp3:
        mp3_path = out_dir / f"{midi_path.stem}.mp3"
        mp3_path = wav_to_mp3(wav_path, mp3_path, bitrate=mp3_bitrate)
        result["mp3"] = mp3_path

    print(f"result is {result}")

    return result
