import queue
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

import yt_dlp


class DownloadState(Enum):
    QUEUED = auto()
    EXTRACTING = auto()
    DOWNLOADING = auto()
    PROCESSING = auto()
    COMPLETE = auto()
    ERROR = auto()
    CANCELLED = auto()


@dataclass
class DownloadProgress:
    state: DownloadState = DownloadState.QUEUED
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    downloaded: str = ""
    total: str = ""
    filename: str = ""
    title: str = ""
    error: str = ""


@dataclass
class VideoInfo:
    url: str = ""
    title: str = ""
    duration: str = ""
    duration_seconds: int = 0
    thumbnail_url: str = ""
    uploader: str = ""
    formats: list = field(default_factory=list)
    is_playlist: bool = False
    playlist_count: int = 0


def _format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "Unknown"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _format_bytes(b: Optional[float]) -> str:
    if b is None or b == 0:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(b) < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def build_format_spec(fmt: str, quality: str) -> dict:
    opts = {}
    if fmt == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        quality_map = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        }
        opts["format"] = quality_map.get(quality, quality_map["best"])
    return opts


class Downloader:
    def extract_info(self, url: str) -> VideoInfo:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if info is None:
            raise ValueError("Could not extract video info")

        is_playlist = info.get("_type") == "playlist"
        entries = info.get("entries", [])

        formats = []
        for f in info.get("formats", []):
            if f.get("vcodec", "none") != "none":
                h = f.get("height")
                if h and h not in formats:
                    formats.append(h)
        formats.sort(reverse=True)

        return VideoInfo(
            url=url,
            title=info.get("title", "Unknown"),
            duration=_format_duration(info.get("duration")),
            duration_seconds=info.get("duration", 0) or 0,
            thumbnail_url=info.get("thumbnail", ""),
            uploader=info.get("uploader", info.get("channel", "Unknown")),
            formats=formats,
            is_playlist=is_playlist,
            playlist_count=len(entries) if is_playlist else 0,
        )

    def download(self, url: str, output_dir: str, fmt: str = "video",
                 quality: str = "best", audio_format: str = "mp3",
                 embed_thumbnail: bool = True,
                 progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
                 cancel_event: Optional[threading.Event] = None) -> Optional[str]:
        progress = DownloadProgress(state=DownloadState.EXTRACTING)
        if progress_callback:
            progress_callback(progress)

        format_opts = build_format_spec(fmt, quality)
        if fmt == "audio" and audio_format != "mp3":
            format_opts["postprocessors"][0]["preferredcodec"] = audio_format

        final_filepath = None

        def hook(d):
            nonlocal final_filepath
            if cancel_event and cancel_event.is_set():
                raise yt_dlp.utils.DownloadCancelled("Cancelled by user")

            status = d.get("status", "")
            if status == "downloading":
                progress.state = DownloadState.DOWNLOADING
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                progress.percent = (downloaded / total * 100) if total else 0
                speed = d.get("speed")
                progress.speed = f"{_format_bytes(speed)}/s" if speed else ""
                eta = d.get("eta")
                progress.eta = f"{eta}s" if eta else ""
                progress.downloaded = _format_bytes(downloaded)
                progress.total = _format_bytes(total)
                progress.filename = d.get("filename", "")
                if progress_callback:
                    progress_callback(progress)
            elif status == "finished":
                progress.state = DownloadState.PROCESSING
                progress.percent = 100
                final_filepath = d.get("filename", "")
                if progress_callback:
                    progress_callback(progress)

        opts = {
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "progress_hooks": [hook],
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4" if fmt == "video" else None,
            "overwrites": True,
            **format_opts,
        }

        if embed_thumbnail and fmt == "audio":
            opts.setdefault("postprocessors", []).append({
                "key": "EmbedThumbnail",
            })
            opts["writethumbnail"] = True

        opts = {k: v for k, v in opts.items() if v is not None}

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                progress.title = info.get("title", "") if info else ""
                if info and not final_filepath:
                    final_filepath = ydl.prepare_filename(info)
        except yt_dlp.utils.DownloadCancelled:
            progress.state = DownloadState.CANCELLED
            if progress_callback:
                progress_callback(progress)
            return None

        progress.state = DownloadState.COMPLETE
        progress.percent = 100
        if progress_callback:
            progress_callback(progress)
        return final_filepath


@dataclass
class _Task:
    task_id: str
    url: str
    output_dir: str
    fmt: str
    quality: str
    audio_format: str
    embed_thumbnail: bool


class DownloadManager:
    def __init__(self):
        self._queue: queue.Queue[_Task] = queue.Queue()
        self._downloader = Downloader()
        self._cancel_event = threading.Event()
        self._current_task: Optional[_Task] = None
        self.on_progress: Optional[Callable[[str, DownloadProgress], None]] = None
        self.on_complete: Optional[Callable[[str, str, dict], None]] = None
        self.on_error: Optional[Callable[[str, str], None]] = None
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def enqueue(self, url: str, output_dir: str, fmt: str = "video",
                quality: str = "best", audio_format: str = "mp3",
                embed_thumbnail: bool = True) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = _Task(task_id, url, output_dir, fmt, quality, audio_format, embed_thumbnail)
        self._queue.put(task)
        return task_id

    def cancel_current(self):
        self._cancel_event.set()

    def _run(self):
        while True:
            task = self._queue.get()
            self._current_task = task
            self._cancel_event.clear()

            def progress_cb(p: DownloadProgress):
                if self.on_progress:
                    self.on_progress(task.task_id, p)

            try:
                filepath = self._downloader.download(
                    url=task.url,
                    output_dir=task.output_dir,
                    fmt=task.fmt,
                    quality=task.quality,
                    audio_format=task.audio_format,
                    embed_thumbnail=task.embed_thumbnail,
                    progress_callback=progress_cb,
                    cancel_event=self._cancel_event,
                )
                if filepath and self.on_complete:
                    import os
                    size_mb = 0.0
                    actual_path = filepath
                    if task.fmt == "audio":
                        base = os.path.splitext(filepath)[0]
                        for ext in (".mp3", ".m4a", ".opus", ".wav", ".flac"):
                            if os.path.exists(base + ext):
                                actual_path = base + ext
                                break
                    if os.path.exists(actual_path):
                        size_mb = os.path.getsize(actual_path) / (1024 * 1024)
                    self.on_complete(task.task_id, actual_path, {
                        "url": task.url,
                        "format": task.fmt,
                        "quality": task.quality,
                        "filesize_mb": size_mb,
                    })
            except Exception as e:
                if self.on_error:
                    self.on_error(task.task_id, str(e))
            finally:
                self._current_task = None
                self._queue.task_done()
