Simple python script that utilizes a few libraries to create a voice-activated virtual assistant on the device of your choosing.   
This is my version of an "open-source Alexa" that focuses on the one feature that I use the most: playing music. It uses the Vosk voice recognition library
to interpret the user's voice, the pyttsx3 library to provide vocal feedback to the user, and queries YouTube via `yt-dlp` to stream or download audio without a browser.

Anyone interested in developing their own music-playing virtual assistant, similar to popular voice assistants, may find this repository beneficial. 
I made this so I wouldn't have to keep paying my monthly Amazon Music Unlimited subscription and the added privacy from using my own IoT device is an added plus.

Brief Demo video showcasing the ability to play music:
https://www.youtube.com/watch?v=SOPgVf_BURg

Hardware:

Raspberry Pi 4 Model B 2GB RAM - Small but powerful device to replace my Amazon Echo
https://www.raspberrypi.com/products/raspberry-pi-4-model-b/

Raspberry Pi 32GB Preloaded (NOOBS) SD Card - For Raspbian OS and storage
https://www.amazon.com/Raspberry-Pi-32GB-Preloaded-NOOBS/dp/B01LXR6EOA

GeeekPi Raspberry Pi Mini Tower Kit, Raspberry Pi 4 Case with ICE Tower Cooler - Ice tower keeps RPi temps cool and this kit includes a case that goes well with it
https://www.amazon.com/GeeekPi-Raspberry-Heatsink-Expansion-Boardfor/dp/B0B6V7XFJH

Mini USB Microphone for Laptop and Desktop Computer - I used this one, but feel free to use any microphone that works with your device
https://www.amazon.com/Microphone-Gooseneck-Universal-Compatible-CGS-M1/dp/B08M37224H

Software:

- `ffmpeg` (for `ffplay` used to stream audio) — install via your OS package manager
- `yt-dlp` (installed via uv/pyproject)


This is not intended to be a major project for me, but I will try my best when I have time to help anyone who is trying to recreate this for their own purposes.

Additional Notes: 
- Wasn't able to install the latest version of python on my raspberry pi, so I was not able to utilize match case for the process_command function.  Lots of "elif" as a result.
- Will incorporate async at some point so that wait times are shorter
- Saw in the news this morning that youtube is cracking down on adblockers, so will have to deal with that if/when that happens.
- Spent a long time trying to set up my raspberry pi so that it would run the script at startup but was not able to get it to work.  Maybe in the future...

Credit to Brandon Jacobson's youtube (https://www.youtube.com/@BrandonJacobson) videos for help with installing the libraries and setting up the 
speech to text and text to speech functionality(Vosk, pyaudio, pyttsx3, etc).  Please check out his videos if you need help with getting those to work.

## Using uv for dependency management

This project uses [`uv`](https://github.com/astral-sh/uv) for fast Python dependency management via `pyproject.toml`.

- Install uv (Linux/macOS):
  - `curl -LsSf https://astral.sh/uv/install.sh | sh`

- Create the virtual environment and lock dependencies:
  - `uv sync`

- Run the app under the managed environment:
  - `uv run alexa-replacement`

Notes:
- `PyAudio` may require system packages (e.g., `portaudio` dev headers). On Debian/Ubuntu: `sudo apt-get install portaudio19-dev` before syncing.
- `ffmpeg` is required (`ffplay` is used for playback). On Debian/Ubuntu: `sudo apt-get install ffmpeg`.

### Optional: Piper TTS (more natural voice)

You can switch to Piper TTS for higher-quality TTS, which works well on Raspberry Pi. Current upstream repo: [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl).

Install Piper either as a system binary or via pip, then download a voice model (e.g., `en_US-kusal-low.onnx` and its `.json`):

```bash
# Example (Debian/Ubuntu); see Piper docs for other platforms
sudo apt-get install piper
# or install the Python package (provides a `piper` CLI in the venv)
uv run pip install piper-tts

# Set env to enable Piper backend
export TTS_BACKEND=piper
export PIPER_MODEL_PATH=/path/to/en_US-kusal-low.onnx
# Optional (if separate config json):
export PIPER_CONFIG_PATH=/path/to/en_US-kusal-low.onnx.json

uv run alexa-replacement
```

### Configure the Vosk model path

Download a Vosk model (e.g., `vosk-model-small-en-us-0.15`) and set `VOSK_MODEL_PATH` to the extracted folder before running:

```bash
export VOSK_MODEL_PATH=/path/to/vosk-model-small-en-us-0.15
uv run alexa-replacement
```

Optional: if you activate the environment (`uv venv && source .venv/bin/activate`), you can run the command directly as `alexa-replacement`.

You can find official models at the Vosk website: `https://alphacephei.com/vosk/models`.
Download and extract one appropriate for your device and language (e.g., English small model), and point `VOSK_MODEL_PATH` to the extracted directory (it should contain subdirectories like `conf`, `am`, etc.).

Voice commands:
- "play <query>": streams the top YouTube audio match
- "download <query>": downloads the top YouTube match as MP3
- "pause" / "unpause": pause/resume playback (process-level pause)
- "stop": stop playback
