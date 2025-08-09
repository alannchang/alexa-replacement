import subprocess
import signal
from typing import Dict, Optional, Tuple

from yt_dlp import YoutubeDL


def _yt_search_first(query: str) -> Tuple[Optional[str], Optional[str], Dict[str, str]]:
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
            return None, None, {}
        entry = result["entries"][0] if "entries" in result and result["entries"] else result
        video_url = entry.get("webpage_url") or entry.get("original_url") or entry.get("url")
        if not video_url:
            return None, None, {}
        info = ydl.extract_info(video_url, download=False)
        stream_url = info.get("url")
        title = info.get("title") or entry.get("title")
        headers = info.get("http_headers") or {}
        return stream_url, title, headers


class PlayerControl:
    def __init__(self) -> None:
        self._player_process: Optional[subprocess.Popen] = None

    def play_query(self, query: str) -> Optional[str]:
        result = _yt_search_first(query)
        if not result:
            return None
        stream_url, title, headers = result
        if not stream_url:
            return None
        self.stop()
        ffplay_cmd = [
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "error",
        ]
        # Forward headers if available (helps with HLS and auth)
        header_lines = []
        if headers:
            if "Referer" not in headers:
                headers["Referer"] = "https://www.youtube.com"
            for key, value in headers.items():
                header_lines.append(f"{key}: {value}")
            header_blob = "\r\n".join(header_lines)
            ffplay_cmd += ["-headers", header_blob]
            if "User-Agent" in headers:
                ffplay_cmd += ["-user_agent", headers["User-Agent"]]
        ffplay_cmd.append(stream_url)
        try:
            self._player_process = subprocess.Popen(ffplay_cmd)
        except FileNotFoundError:
            raise FileNotFoundError("ffplay is not installed. Please install ffmpeg.")
        return title

    def download_query(self, query: str) -> bool:
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
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch1:{query}"])
            return True
        except Exception:
            return False

    def stop(self) -> None:
        if self._player_process and self._player_process.poll() is None:
            try:
                self._player_process.terminate()
                try:
                    self._player_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._player_process.kill()
            finally:
                self._player_process = None

    def pause(self) -> None:
        if self._player_process and self._player_process.poll() is None:
            try:
                self._player_process.send_signal(signal.SIGSTOP)
            except Exception:
                pass

    def resume(self) -> None:
        if self._player_process and self._player_process.poll() is None:
            try:
                self._player_process.send_signal(signal.SIGCONT)
            except Exception:
                pass


