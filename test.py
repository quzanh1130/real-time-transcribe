from faster_whisper import WhisperModel
import os
from config import model_en_name

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model_name = model_en_name
model = WhisperModel(model_name, device="cuda", compute_type="float16")

segments, info = model.transcribe("audio.mp3", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))