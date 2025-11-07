# --------------------------------------------------------------
# run.py
# --------------------------------------------------------------
"""
CLI entry point:

    $ python run.py -i <audio>.mp3 -o <output_dir> [options]

The script:
    Calls :func:`interpret_audio.predict_to_midi`
    Calls :func:`construct_audio.render_midi_to_audio`
    Prints a short summary and exits.
"""

import argparse
import pathlib
import sys

from audio_tab_generator.generate_tabs import midi_to_guitar_tab
from interpret_audio import predict_to_midi
from generate_audio import render_midi_to_audio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run basic_pitch → MIDI → audio (wav/mp3) pipeline.")
    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        required=True,
        help="Path to the input audio (mp3, wav, …).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path("./src/output"),
        help="Directory where MIDI, Tab, WAV and MP3 will be written (default: src/output).",
    )
    parser.add_argument(
        "--soundfont",
        type=pathlib.Path,
        default=pathlib.Path("./src/instruments/clean_acoustic.sf2"),
        help="Path to a .sf2 SoundFont. Default is an acoustic guitar",
    )
    parser.add_argument(
        "--gen-wav",
        action="store_true",
        help="Additionally generates WAV audio from the midi file.",
    )
    parser.add_argument(
        "--gen-mp3",
        action="store_true",
        help="Additionally generated MP3 audio from the midi file.",
    )

    # Basic‑pitch hyper‑parameters (optional – keep defaults if you don't need them)
    parser.add_argument("--onset-threshold", type=float, default=0.5)
    parser.add_argument("--frame-threshold", type=float, default=0.3)
    parser.add_argument("--min-note-length", type=float, default=127.70)
    parser.add_argument("--melodia-trick", action="store_true", default=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve paths & defaults
    input_path = args.input.expanduser().resolve()
    out_dir = args.output_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    soundfont = args.soundfont

    # Predict → MIDI
    try:
        midi_path, note_events = predict_to_midi(
            audio_path=input_path,
            out_dir=out_dir,
            onset_threshold=args.onset_threshold,
            frame_threshold=args.frame_threshold,
            minimum_note_length=args.min_note_length,
            melodia_trick=args.melodia_trick,
        )
    except Exception as exc:
        print(f"basic_pitch failed: {exc}", file=sys.stderr)
        return 1

    print(f"MIDI written to {midi_path}")

    # Generate guitar tabs
    tab_path = midi_to_guitar_tab(midi_path=midi_path, out_dir=out_dir)

    # Render → WAV / MP3
    if args.gen_wav or args.gen_mp3:
        try:
            render_result = render_midi_to_audio(
                midi_path=midi_path,
                out_dir=out_dir,
                soundfont_path=soundfont,
                generate_wav=args.gen_wav,
                generate_mp3=args.gen_mp3,
            )
        except Exception as exc:
            print(f"Rendering failed: {exc}", file=sys.stderr)
            return 1

    print("\n=== Summary ===")
    print(f"Input audio   : {input_path}")
    print(f"MIDI file     : {midi_path}")
    print(f"Tab file      : {tab_path}")
    if args.gen_wav:
        print(f"WAV file     : {render_result['wav']}")
    if args.gen_mp3:
        print(f"MP3 file     : {render_result['mp3']}")
    print(f"Detected notes: {len(note_events)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
