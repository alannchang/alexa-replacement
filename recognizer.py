import os
import sys
import time
from typing import Optional

import pyaudio
from vosk import Model, KaldiRecognizer


class SpeechRecognizer:
    def __init__(self, model_path_env: str = "VOSK_MODEL_PATH") -> None:
        model_path = os.environ.get(model_path_env)
        if not model_path or not os.path.isdir(model_path):
            raise RuntimeError(
                f"Environment variable {model_path_env} is not set to a valid Vosk model directory"
            )
        self._model = Model(model_path)
        self._recognizer = KaldiRecognizer(self._model, 16000)
        self._mic = pyaudio.PyAudio()

    def listen_for_wake(self) -> str:
        stream = self._mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192,
        )
        while True:
            stream.start_stream()
            try:
                data = stream.read(4096)
                if self._recognizer.AcceptWaveform(data):
                    result = self._recognizer.Result()
                    response = result[14:-3]
                    stream.close()
                    return response
            except OSError:
                pass

    def get_command(self, timeout: int = 5) -> Optional[str]:
        stream = self._mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192,
        )
        start_time = time.monotonic()
        while True:
            stream.start_stream()
            try:
                data = stream.read(4096, exception_on_overflow=False)
                if self._recognizer.AcceptWaveform(data):
                    result = self._recognizer.Result()
                    response = result[14:-3]
                    stream.close()
                    return response
            except OSError:
                pass
            if time.monotonic() - start_time > timeout:
                stream.close()
                return None


