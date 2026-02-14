import json
import os
import sys
from datetime import datetime
from pathlib import Path


def _config_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "StreamSniper"
    d.mkdir(parents=True, exist_ok=True)
    return d


DEFAULTS = {
    "download_dir": str(Path.home() / "Downloads"),
    "format": "video",
    "quality": "best",
    "audio_format": "mp3",
    "embed_thumbnail": True,
    "sponsorblock": False,
    "window_geometry": "900x620",
}


class Config:
    def __init__(self):
        self._path = _config_dir() / "config.json"
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                with open(self._path) as f:
                    stored = json.load(f)
                self._data.update(stored)
            except (json.JSONDecodeError, OSError):
                pass

    def _save(self):
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str):
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value):
        self._data[key] = value
        self._save()

    def reset(self):
        self._data = dict(DEFAULTS)
        self._save()


class DownloadHistory:
    def __init__(self):
        self._path = _config_dir() / "history.json"
        self._entries: list[dict] = []
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                with open(self._path) as f:
                    self._entries = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def _save(self):
        with open(self._path, "w") as f:
            json.dump(self._entries, f, indent=2)

    def add(self, url: str, title: str, filename: str, path: str,
            fmt: str, quality: str, filesize_mb: float, duration: str):
        self._entries.insert(0, {
            "url": url,
            "title": title,
            "filename": filename,
            "path": path,
            "format": fmt,
            "quality": quality,
            "filesize_mb": round(filesize_mb, 2),
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def remove(self, index: int):
        if 0 <= index < len(self._entries):
            self._entries.pop(index)
            self._save()

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [e for e in self._entries if q in e.get("title", "").lower()
                or q in e.get("url", "").lower()]

    def all(self) -> list[dict]:
        return list(self._entries)

    def clear(self):
        self._entries = []
        self._save()
