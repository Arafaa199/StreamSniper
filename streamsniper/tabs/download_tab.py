import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk

from .. import theme
from ..downloader import DownloadManager, DownloadProgress, DownloadState, Downloader, VideoInfo
from ..widgets import StatusBar, ThumbnailPreview


class DownloadTab(ttk.Frame):
    def __init__(self, parent, config, history, download_manager: DownloadManager):
        super().__init__(parent, style="TFrame")
        self.config = config
        self.history = history
        self.dm = download_manager
        self._current_info: VideoInfo | None = None
        self._extracting = False
        self._downloading = False

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # URL bar
        url_frame = ttk.Frame(container, style="TFrame")
        url_frame.pack(fill=tk.X, pady=(0, 16))

        ttk.Label(url_frame, text="URL", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 6))

        input_row = ttk.Frame(url_frame, style="TFrame")
        input_row.pack(fill=tk.X)

        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(input_row, textvariable=self.url_var, font=theme.FONT)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self._on_fetch())

        self.paste_btn = ttk.Button(input_row, text="Paste", style="Secondary.TButton",
                                     command=self._paste_url)
        self.paste_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.fetch_btn = ttk.Button(input_row, text="Fetch", style="Accent.TButton",
                                     command=self._on_fetch)
        self.fetch_btn.pack(side=tk.LEFT)

        # Info panel
        info_frame = ttk.Frame(container, style="Card.TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 16), ipady=12, ipadx=12)

        info_inner = ttk.Frame(info_frame, style="Card.TFrame")
        info_inner.pack(fill=tk.X, padx=12, pady=8)

        self.thumbnail = ThumbnailPreview(info_inner, width=200, height=112)
        self.thumbnail.pack(side=tk.LEFT, padx=(0, 16))

        details = ttk.Frame(info_inner, style="Card.TFrame")
        details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_var = tk.StringVar(value="Paste a URL and click Fetch")
        ttk.Label(details, textvariable=self.title_var, style="Heading.TLabel",
                  wraplength=400).pack(anchor=tk.W, pady=(0, 4))

        meta_frame = ttk.Frame(details, style="Card.TFrame")
        meta_frame.pack(anchor=tk.W)

        self.uploader_var = tk.StringVar()
        ttk.Label(meta_frame, textvariable=self.uploader_var,
                  style="Secondary.TLabel").pack(side=tk.LEFT, padx=(0, 16))

        self.duration_var = tk.StringVar()
        ttk.Label(meta_frame, textvariable=self.duration_var,
                  style="Secondary.TLabel").pack(side=tk.LEFT)

        # Format controls
        fmt_frame = ttk.Frame(container, style="TFrame")
        fmt_frame.pack(fill=tk.X, pady=(0, 16))

        ttk.Label(fmt_frame, text="Format", style="TLabel").pack(side=tk.LEFT, padx=(0, 12))

        self.format_var = tk.StringVar(value=self.config.get("format"))
        ttk.Radiobutton(fmt_frame, text="Video", variable=self.format_var, value="video",
                        style="TRadiobutton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Radiobutton(fmt_frame, text="Audio", variable=self.format_var, value="audio",
                        style="TRadiobutton").pack(side=tk.LEFT, padx=(0, 24))

        ttk.Label(fmt_frame, text="Quality", style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.quality_var = tk.StringVar(value=self.config.get("quality"))
        self.quality_combo = ttk.Combobox(fmt_frame, textvariable=self.quality_var,
                                          values=["best", "1080p", "720p", "480p"],
                                          state="readonly", width=10)
        self.quality_combo.pack(side=tk.LEFT)

        # Download button row
        btn_frame = ttk.Frame(container, style="TFrame")
        btn_frame.pack(fill=tk.X, pady=(0, 12))

        self.download_btn = ttk.Button(btn_frame, text="Download", style="Accent.TButton",
                                        command=self._on_download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", style="Secondary.TButton",
                                      command=self._on_cancel, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 16))

        self.open_folder_btn = ttk.Button(btn_frame, text="Open Folder", style="Secondary.TButton",
                                           command=self._open_download_folder)
        self.open_folder_btn.pack(side=tk.RIGHT)

        # Progress
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(container, variable=self.progress_var,
                                             maximum=100, style="red.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))

        self.status_bar = StatusBar(container)
        self.status_bar.pack(fill=tk.X, pady=(0, 8))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(container, textvariable=self.status_var,
                  style="Secondary.TLabel").pack(anchor=tk.W)

    def _paste_url(self):
        try:
            text = self.clipboard_get()
            self.url_var.set(text.strip())
            self._on_fetch()
        except tk.TclError:
            pass

    def _on_fetch(self):
        url = self.url_var.get().strip()
        if not url or self._extracting:
            return
        self._extracting = True
        self.fetch_btn.configure(state=tk.DISABLED)
        self.status_var.set("Extracting info...")
        self.title_var.set("Loading...")
        self.uploader_var.set("")
        self.duration_var.set("")
        self.thumbnail.clear()
        threading.Thread(target=self._extract_info, args=(url,), daemon=True).start()

    def _extract_info(self, url: str):
        try:
            dl = Downloader()
            info = dl.extract_info(url)
            self.after(0, self._update_info, info)
        except Exception as e:
            self.after(0, self._extract_error, str(e))

    def _update_info(self, info: VideoInfo):
        self._current_info = info
        self._extracting = False
        self.fetch_btn.configure(state=tk.NORMAL)
        self.title_var.set(info.title)
        self.uploader_var.set(info.uploader)
        self.duration_var.set(info.duration)
        self.status_var.set("Ready to download")
        if info.thumbnail_url:
            self.thumbnail.load_url(info.thumbnail_url)
        if info.formats:
            available = ["best"] + [f"{h}p" for h in info.formats if h]
            self.quality_combo.configure(values=available)

    def _extract_error(self, error: str):
        self._extracting = False
        self.fetch_btn.configure(state=tk.NORMAL)
        self.title_var.set("Error fetching info")
        self.status_var.set(f"Error: {error[:100]}")

    def _on_download(self):
        url = self.url_var.get().strip()
        if not url or self._downloading:
            return
        self._downloading = True
        self.download_btn.configure(state=tk.DISABLED)
        self.cancel_btn.configure(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Starting download...")

        self.dm.enqueue(
            url=url,
            output_dir=self.config.get("download_dir"),
            fmt=self.format_var.get(),
            quality=self.quality_var.get(),
            audio_format=self.config.get("audio_format"),
            embed_thumbnail=self.config.get("embed_thumbnail"),
        )

    def _on_cancel(self):
        self.dm.cancel_current()
        self.status_var.set("Cancelling...")

    def on_progress(self, task_id: str, progress: DownloadProgress):
        self.progress_var.set(progress.percent)
        state_text = {
            DownloadState.EXTRACTING: "Extracting...",
            DownloadState.DOWNLOADING: f"Downloading... {progress.percent:.0f}%",
            DownloadState.PROCESSING: "Processing...",
            DownloadState.CANCELLED: "Cancelled",
        }
        self.status_var.set(state_text.get(progress.state, str(progress.state.name)))
        self.status_bar.update_stats(progress.speed, progress.eta,
                                      f"{progress.downloaded} / {progress.total}")

    def on_complete(self, task_id: str, filepath: str, meta: dict):
        self._downloading = False
        self.download_btn.configure(state=tk.NORMAL)
        self.cancel_btn.configure(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_var.set(f"Complete: {os.path.basename(filepath)}")
        self.status_bar.clear()

        title = self._current_info.title if self._current_info else os.path.basename(filepath)
        duration = self._current_info.duration if self._current_info else ""
        self.history.add(
            url=meta.get("url", ""),
            title=title,
            filename=os.path.basename(filepath),
            path=filepath,
            fmt=meta.get("format", ""),
            quality=meta.get("quality", ""),
            filesize_mb=meta.get("filesize_mb", 0),
            duration=duration,
        )

    def on_error(self, task_id: str, error: str):
        self._downloading = False
        self.download_btn.configure(state=tk.NORMAL)
        self.cancel_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set(f"Error: {error[:100]}")
        self.status_bar.clear()

    def _open_download_folder(self):
        path = self.config.get("download_dir")
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
