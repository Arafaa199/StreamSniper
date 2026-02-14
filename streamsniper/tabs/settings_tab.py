import tkinter as tk
from tkinter import filedialog, ttk

from .. import theme
from ..config import Config


class SettingsTab(ttk.Frame):
    def __init__(self, parent, config: Config):
        super().__init__(parent, style="TFrame")
        self.config = config
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        ttk.Label(container, text="Settings", style="Title.TLabel").pack(anchor=tk.W, pady=(0, 20))

        # Download directory
        dir_frame = ttk.Frame(container, style="TFrame")
        dir_frame.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(dir_frame, text="Download Directory", style="TLabel").pack(anchor=tk.W, pady=(0, 4))

        dir_row = ttk.Frame(dir_frame, style="TFrame")
        dir_row.pack(fill=tk.X)

        self.dir_var = tk.StringVar(value=self.config.get("download_dir"))
        ttk.Entry(dir_row, textvariable=self.dir_var, font=theme.FONT).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(dir_row, text="Browse", style="Secondary.TButton",
                   command=self._browse_dir).pack(side=tk.LEFT)
        self.dir_var.trace_add("write", lambda *_: self.config.set("download_dir", self.dir_var.get()))

        # Default format
        fmt_frame = ttk.Frame(container, style="TFrame")
        fmt_frame.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(fmt_frame, text="Default Format", style="TLabel").pack(anchor=tk.W, pady=(0, 4))

        self.format_var = tk.StringVar(value=self.config.get("format"))
        radio_row = ttk.Frame(fmt_frame, style="TFrame")
        radio_row.pack(anchor=tk.W)
        ttk.Radiobutton(radio_row, text="Video", variable=self.format_var, value="video").pack(
            side=tk.LEFT, padx=(0, 16))
        ttk.Radiobutton(radio_row, text="Audio", variable=self.format_var, value="audio").pack(
            side=tk.LEFT)
        self.format_var.trace_add("write", lambda *_: self.config.set("format", self.format_var.get()))

        # Video quality
        qual_frame = ttk.Frame(container, style="TFrame")
        qual_frame.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(qual_frame, text="Default Video Quality", style="TLabel").pack(anchor=tk.W, pady=(0, 4))

        self.quality_var = tk.StringVar(value=self.config.get("quality"))
        ttk.Combobox(qual_frame, textvariable=self.quality_var,
                     values=["best", "1080p", "720p", "480p"],
                     state="readonly", width=15).pack(anchor=tk.W)
        self.quality_var.trace_add("write", lambda *_: self.config.set("quality", self.quality_var.get()))

        # Audio format
        audio_frame = ttk.Frame(container, style="TFrame")
        audio_frame.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(audio_frame, text="Audio Format", style="TLabel").pack(anchor=tk.W, pady=(0, 4))

        self.audio_var = tk.StringVar(value=self.config.get("audio_format"))
        ttk.Combobox(audio_frame, textvariable=self.audio_var,
                     values=["mp3", "m4a", "opus", "wav", "flac"],
                     state="readonly", width=15).pack(anchor=tk.W)
        self.audio_var.trace_add("write", lambda *_: self.config.set("audio_format", self.audio_var.get()))

        # Embed thumbnail
        thumb_frame = ttk.Frame(container, style="TFrame")
        thumb_frame.pack(fill=tk.X, pady=(0, 24))

        self.thumb_var = tk.BooleanVar(value=self.config.get("embed_thumbnail"))
        ttk.Checkbutton(thumb_frame, text="Embed thumbnail in audio files",
                        variable=self.thumb_var).pack(anchor=tk.W)
        self.thumb_var.trace_add("write", lambda *_: self.config.set("embed_thumbnail", self.thumb_var.get()))

        # Reset
        ttk.Button(container, text="Reset to Defaults", style="Secondary.TButton",
                   command=self._reset).pack(anchor=tk.W)

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _reset(self):
        self.config.reset()
        self.dir_var.set(self.config.get("download_dir"))
        self.format_var.set(self.config.get("format"))
        self.quality_var.set(self.config.get("quality"))
        self.audio_var.set(self.config.get("audio_format"))
        self.thumb_var.set(self.config.get("embed_thumbnail"))
