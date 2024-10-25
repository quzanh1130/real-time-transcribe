import threading
import wave
import pyaudio
from config import CHUNK, FORMAT, CHANNELS, RATE

class AudioRecorder:
    def __init__(self):
        self.audio_queue = []
        self.lock = threading.Lock()
        self.recording = False
        self.audio = None
        self.stream = None

    def callback(self, in_data, frame_count, time_info, status):
        with self.lock:
            self.audio_queue.append(in_data)
        return (in_data, pyaudio.paContinue)

    def start(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK,
                                      stream_callback=self.callback)
        self.stream.start_stream()
        self.recording = True

    def stop(self):
        self.recording = False
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio is not None:
            self.audio.terminate()

    def save_chunk_to_file(self, file_path):
        with self.lock:
            frames = self.audio_queue[:]  # Make a copy to avoid interference
            self.audio_queue = []  # Clear the queue

        audio_data = b''.join(frames)

        if self.audio is not None:
            sample_width = self.audio.get_sample_size(FORMAT)
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(sample_width)
                wf.setframerate(RATE)
                wf.writeframes(audio_data)
