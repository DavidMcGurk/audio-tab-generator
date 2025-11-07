# Audio Tab Generator
This project is designed to import audio files, and then convert them into guitar tabs.

## Prerequisites
- Python 3.11
- [Poetry](https://python-poetry.org/)
- [FluidSynth](https://github.com/FluidSynth/fluidsynth/releases)
- [FFmpeg](https://www.ffmpeg.org/)

## Usage

### Basic usage
The generator can be run with any audio file of type `.mp3`, `.wav`, `.ogg`,`.flac`, or `.m4a`. It will of course
work best with instrumental files.

First, the repository must be set up using:
```bash
poetry install
```

Then the generator can be run using:
```bash
poetry run python src/audio_tab_generator/run.py -i <your-audio-file>.mp3 [--gen-mp3]
```
Where the flags `--gen-mp3` or `--gen-wav` can be used to optionally reconstruct the midi files into audio files.

For more detailed usage and options, run:
```bash
poetry run python src/audio_tab_generator/run.py -h
```

### Dev Setup

1. **Install pre-commit hooks** :
```bash
pre-commit install
```

That is pretty much it for the moment.
