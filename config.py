import torch
import pyaudio

# Model name
MODEL_EN_NAME = "medium"
MODEL_VI_NAME = "PhoWhisper-small-VietBud500"


# Device
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

# Audio stream parameters
CHUNK = 1024*3  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate