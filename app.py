import subprocess
import pyttsx3

from commands import parse_command
from player import PlayerControl
from recognizer import SpeechRecognizer


WAKE_WORD = "joker"


class App:
    def __init__(self) -> None:
        self.tts = pyttsx3.init()
        self.tts.setProperty('voice', 'en-us')
        self.recognizer = SpeechRecognizer()
        self.player = PlayerControl()

    def say(self, text: str) -> None:
        self.tts.say(text)
        self.tts.runAndWait()

    def handle_command(self, command: str) -> None:
        action, arg = parse_command(command)
        if action == "noop":
            return
        if action == "greet":
            self.say("Hello, how are you today?")
            return
        if action == "play" and arg:
            title = self.player.play_query(arg)
            if not title:
                self.say("I couldn't find anything to play.")
            else:
                self.say(f"Now playing {title}")
            return
        if action == "download" and arg:
            ok = self.player.download_query(arg)
            self.say("Download complete." if ok else "I was unable to download that.")
            return
        if action == "pause":
            self.player.pause()
            return
        if action == "resume":
            self.player.resume()
            return
        if action == "stop":
            self.player.stop()
            return
        if action == "vol_up":
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
            self.say("Volume increased.")
            return
        if action == "vol_down":
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
            self.say("Volume decreased.")
            return
        if action == "unknown":
            self.say("I'm sorry, I don't understand that.")

    def run(self) -> None:
        while True:
            print("Listening for wake word.")
            heard = self.recognizer.listen_for_wake()
            print(heard)
            if heard == WAKE_WORD:
                self.say("How can I help you?")
                print("Waiting for command.")
                command = self.recognizer.get_command()
                print(command)
                if command is not None:
                    self.handle_command(command)


def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()


