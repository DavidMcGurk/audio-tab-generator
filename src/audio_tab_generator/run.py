from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH  # noqa: F401
from pathlib import Path
import time

SCRIPT_DIR = Path(__file__).parent.parent
INPUT_PATH = SCRIPT_DIR / "test_audio/tristeza_toquinho.mp3"

start_time = time.time()
model_output, midi_data, note_events = predict(INPUT_PATH)
end_time = time.time()
print(note_events)
print(f"Calculation took {end_time - start_time}")
