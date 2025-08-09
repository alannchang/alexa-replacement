from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import time
import subprocess
import signal
import os
import sys
from datetime import datetime
from yt_dlp import YoutubeDL

# text-to-speech setup
engine = pyttsx3.init()
engine.setProperty('voice', 'en-us')

engine.say("Initializing. Please wait")
engine.runAndWait()


# vosk speech recognition setup
VOSK_MODEL_PATH = os.environ.get("VOSK_MODEL_PATH")
if not VOSK_MODEL_PATH or not os.path.isdir(VOSK_MODEL_PATH):
    print("Error: VOSK_MODEL_PATH is not set to a valid directory.")
    print("Please download a Vosk model (e.g., 'vosk-model-small-en-us-0.15') and set VOSK_MODEL_PATH to that folder.")
    try:
        engine.say("Speech model not configured. Please set V O S K model path.")
        engine.runAndWait()
    except Exception:
        pass
    sys.exit(1)

model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()

# set wake word to word(s) of your choice
WAKE_WORD = "jarvis"

def listen_for_wake():
    listening = True
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    while listening:
        stream.start_stream()
        try:
            data = stream.read(4096)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                response = result[14:-3]
                listening = False
                stream.close()
                return response
        except OSError:
            pass

# I set it to timeout after 5 seconds if no command given, feel free to play with it
def get_command(timeout=5):
    listening = True
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    start_time = time.monotonic()
    while listening:
        stream.start_stream()
        try:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                response = result[14:-3]
                listening = False
                stream.close()
                return response
        except OSError:
            pass
        if time.monotonic() - start_time > timeout:
            print("Timeout")
            listening = False
            stream.close()
            return None


player_process = None

def _yt_search_first(query: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "format": "bestaudio/best",
        "default_search": "ytsearch",
        # Use Android client to avoid SABR web client issues
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if result is None:
            return None, None
        entry = result["entries"][0] if "entries" in result and result["entries"] else result
        # Ensure we resolve to a concrete video info with the chosen format
        video_url = entry.get("webpage_url") or entry.get("original_url") or entry.get("url")
        if not video_url:
            return None, None
        info = ydl.extract_info(video_url, download=False)
        stream_url = info.get("url")
        title = info.get("title") or entry.get("title")
        headers = info.get("http_headers") or {}
        return (stream_url, title, headers)

def play_query(query: str):
    global player_process
    result = _yt_search_first(query)
    if not result:
        engine.say("I couldn't find anything to play.")
        engine.runAndWait()
        return
    stream_url, title, headers = result
    if not stream_url:
        engine.say("I couldn't find anything to play.")
        engine.runAndWait()
        return
    try:
        # Stop any existing playback first
        stop_playback()
        ffplay_cmd = [
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "error",
        ]
        # Forward headers if available (helps with HLS and auth)
        header_lines = []
        if headers:
            # Ensure Referer header is present
            if "Referer" not in headers:
                headers["Referer"] = "https://www.youtube.com"
            for key, value in headers.items():
                header_lines.append(f"{key}: {value}")
            header_blob = "\r\n".join(header_lines)
            ffplay_cmd += ["-headers", header_blob]
            # Also set user agent explicitly if provided
            if "User-Agent" in headers:
                ffplay_cmd += ["-user_agent", headers["User-Agent"]]
        ffplay_cmd.append(stream_url)
        player_process = subprocess.Popen(ffplay_cmd)
        if title:
            engine.say(f"Now playing {title}")
            engine.runAndWait()
    except FileNotFoundError:
        engine.say("ffplay is not installed. Please install ffmpeg.")
        engine.runAndWait()

def download_query(query: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "default_search": "ytsearch",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        # Use Android client to avoid SABR web client issues
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])
        engine.say("Download complete.")
        engine.runAndWait()
    except Exception:
        engine.say("I was unable to download that.")
        engine.runAndWait()

def stop_playback():
    global player_process
    if player_process and player_process.poll() is None:
        try:
            player_process.terminate()
            try:
                player_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                player_process.kill()
        finally:
            player_process = None

def pause_playback():
    global player_process
    if player_process and player_process.poll() is None:
        try:
            player_process.send_signal(signal.SIGSTOP)
        except Exception:
            pass

def resume_playback():
    global player_process
    if player_process and player_process.poll() is None:
        try:
            player_process.send_signal(signal.SIGCONT)
        except Exception:
            pass
  
def process_command(command):
  # do nothing when no sound or ambient sound
  if command in ["", "huh"]:
    pass
  # basic greeting
  elif command in ["hello", "hi", "good morning", "good afternoon", "good evening"]:
    engine.say("Hello, how are you today?")
    engine.runAndWait()
  # play music using youtube
  elif command is not None and command.startswith("play"):
    play_query(command.replace("play", "").strip())
  # download audio
  elif command is not None and command.startswith("download"):
    download_query(command.replace("download", "").strip())
  # volume control
  elif command == "volume up":
    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
    engine.say("Volume increased.")
    engine.runAndWait()
  elif command == "volume down":
    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
    engine.say("Volume decreased.")
    engine.runAndWait()
  # "Stop"
  elif command == "stop":
    stop_playback()
  # Toggle play/pause button
  elif command in ["pause", "unpause"]:
    if command == "pause":
      pause_playback()
    else:
      resume_playback()
  # Toggle autoplay
  elif command == "auto play off":
    engine.say("Autoplay control is not available without a browser.")
    engine.runAndWait()
  # Next (song)
  elif command == "next":
    engine.say("Next is not available without a playlist.")
    engine.runAndWait()
  # time out handler
  elif command == None:
    pass
  # if command not recognized, simply say I don't know
  else:
    engine.say("I'm sorry, I don't understand that.")
    engine.runAndWait()
    
# event loop
while True:
    print("Listening for wake word.")
    command = listen_for_wake()
    print(command)
    if command == WAKE_WORD:
        engine.say("How can I help you?")
        engine.runAndWait()
        print("Waiting for command.")
        command = get_command()
        print(command)
        process_command(command)
    else:
        pass
