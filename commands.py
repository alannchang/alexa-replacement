from typing import Optional


def normalize(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    return text.strip().lower()


def parse_command(command: Optional[str]) -> tuple[str, Optional[str]]:
    cmd = normalize(command)
    if cmd in (None, "", "huh"):
        return ("noop", None)
    if cmd in ("hello", "hi", "good morning", "good afternoon", "good evening"):
        return ("greet", None)
    if cmd.startswith("play "):
        return ("play", cmd.replace("play", "", 1).strip())
    if cmd.startswith("download "):
        return ("download", cmd.replace("download", "", 1).strip())
    if cmd == "pause":
        return ("pause", None)
    if cmd == "unpause":
        return ("resume", None)
    if cmd == "stop":
        return ("stop", None)
    if cmd == "volume up":
        return ("vol_up", None)
    if cmd == "volume down":
        return ("vol_down", None)
    return ("unknown", None)


