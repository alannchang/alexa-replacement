import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

import pyttsx3


class TextToSpeech(ABC):
    @abstractmethod
    def say(self, text: str) -> None:  # blocking
        ...


class Pyttsx3TTS(TextToSpeech):
    def __init__(self) -> None:
        self._engine = pyttsx3.init()
        self._engine.setProperty("voice", "en-us")

    def say(self, text: str) -> None:
        self._engine.say(text)
        self._engine.runAndWait()


class PiperTTS(TextToSpeech):
    def __init__(self, model_path: str, config_path: Optional[str] = None, piper_bin: str = "piper") -> None:
        if shutil.which(piper_bin) is None:
            raise FileNotFoundError("piper binary not found in PATH. Install Piper or set PIPER_BIN")
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Piper model not found: {model_path}")
        if config_path is None:
            with_json = model_path + ".json"
            config_path = with_json if os.path.isfile(with_json) else None
        self._piper_bin = piper_bin
        self._model_path = model_path
        self._config_path = config_path

    def say(self, text: str) -> None:
        # Synthesize to a temporary wav and play via ffplay
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            wav_path = tmp_wav.name
        try:
            cmd = [self._piper_bin, "--model", self._model_path, "--output_file", wav_path]
            if self._config_path:
                cmd += ["--config", self._config_path]
            # Use --sentence for simple input; avoids shell echo issues
            cmd += ["--sentence", text]
            subprocess.run(cmd, check=True)
            # Play the wav
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", wav_path], check=True)
        finally:
            try:
                os.remove(wav_path)
            except OSError:
                pass


def get_tts_engine() -> TextToSpeech:
    backend = os.environ.get("TTS_BACKEND", "pyttsx3").strip().lower()
    if backend == "piper":
        model = os.environ.get("PIPER_MODEL_PATH")
        if not model:
            raise RuntimeError("PIPER_MODEL_PATH must be set when TTS_BACKEND=piper")
        config = os.environ.get("PIPER_CONFIG_PATH")
        piper_bin = os.environ.get("PIPER_BIN", "piper")
        return PiperTTS(model_path=model, config_path=config, piper_bin=piper_bin)
    # default
    return Pyttsx3TTS()


