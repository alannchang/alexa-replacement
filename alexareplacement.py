from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import time
import subprocess
from datetime import datetime

# text-to-speech setup
engine = pyttsx3.init()
engine.setProperty('voice', 'en-us')

# selenium setup
options = webdriver.ChromeOptions()
# uBlock origin extension
# options.add_argument('--load-extension=/home/pi/.config/chromium/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm/1.49.2_0')
# Music mode for youtube extension
options.add_argument('--load-extension=/home/pi/.config/chromium/Default/Extensions/abbpaepbpakcpipajigmlpnhlnbennna/6.1.3_0')
driver = webdriver.Chrome(options=options)

# OPEN WEBPAGE
engine.say("Initializing. Please wait")
engine.runAndWait()
driver.get("https://www.youtube.com")
driver.switch_to.window(driver.window_handles[0])


# vosk speech recognition setup
model = Model(r"/home/pi/Downloads/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()

# set wake word to word(s) of your choice
WAKE_WORD = "joker"

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


# use youtube search bar to find and play videos
def search_youtube(query):
  search_box = driver.find_element(By.NAME, 'search_query')
  search_box.clear()
  search_box.send_keys(query)
  search_button = driver.find_element(By.ID, 'search-icon-legacy')
  search_button.click()
  while True:
    try:
      first_video = driver.find_element(By.CLASS_NAME, 'title-and-badge')
      title = first_video.text
      first_video.click()
      engine.say(f"Now playing {title}")
      engine.runAndWait()
      break
    except:
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
    search_youtube(command.replace("play", "").strip())
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
    driver.get("https://www.youtube.com")
  # Toggle play/pause button
  elif command in ["pause", "unpause"]:
    try:
      play_button = driver.find_element(By.CLASS_NAME, 'ytp-play-button')
      play_button.click()
    except:
      engine.say("I am unable to do that")
      engine.runAndWait()
  # Toggle autoplay
  elif command == "auto play off":
    try:
      autoplay_button = driver.find_element(By.CLASS_NAME, 'ytp-autonav-toggle-button')
      autoplay_button.click()
    except:
      engine.say("I am unable to do that")
      engine.runAndWait()
  # Next (song)
  elif command == "next":
    try:
      autoplay_button = driver.find_element(By.CLASS_NAME, 'ytp-next-button')
      autoplay_button.click()
    except:
      engine.say("I am unable to do that")
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
