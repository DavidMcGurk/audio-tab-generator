# Audio Tab Generator

This project is designed to import audio files, and then convert them into guitar tabs. Note, this is still a WIP.

## Prerequisites

- Python 3.11
- [Poetry](https://python-poetry.org/)
- [FluidSynth](https://github.com/FluidSynth/fluidsynth/releases)
- [FFmpeg](https://www.ffmpeg.org/)
- [pre-commit](https://pre-commit.com/#install)

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
poetry run python run.py -i <your-audio-file>.mp3 [--gen-mp3]
```

Where the flags `--gen-mp3` or `--gen-wav` can be used to optionally reconstruct the midi files into audio files.

If the predicted tabs are poor, it is likely because the onset threshold (and to a lesser extent the frame threshold
or minimum note length) are incorrectly tuned. If the onset is too low, it will pick up harmonics and general noise,
too high and it will not pick up quiter notes. Therefore, this should be adjusted based on the input audio to produce
better results.

For more detailed usage and options, run:

```bash
poetry run python run.py -h
```

### Dev Setup

1. **Install pre-commit hooks** :

```bash
pre-commit install
```

2. **Run E2E tests** :

Some end to end tests have been written to ensure that the output of the generator is working as expected. To try them out,
in e2e_tests, run:

```bash
poetry run pytest
```
