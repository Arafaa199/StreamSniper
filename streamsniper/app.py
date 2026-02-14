import tkinter as tk
from tkinter import ttk

from . import __version__, theme
from .config import Config, DownloadHistory
from .downloader import DownloadManager, DownloadProgress
from .tabs.download_tab import DownloadTab
from .tabs.history_tab import HistoryTab
from .tabs.settings_tab import SettingsTab
from .widgets import GradientFrame


class StreamSniperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"StreamSniper v{__version__}")
        self.root.configure(bg=theme.BG_DARK)

        self.config = Config()
        self.history = DownloadHistory()
        self.dm = DownloadManager()

        geo = self.config.get("window_geometry")
        self.root.geometry(geo)
        self.root.minsize(700, 500)

        theme.configure_ttk_styles()
        self._build_ui()
        self._bind_download_manager()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Gradient background
        self.gradient = GradientFrame(self.root)
        self.gradient.place(relwidth=1, relheight=1)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.download_tab = DownloadTab(self.notebook, self.config, self.history, self.dm)
        self.history_tab = HistoryTab(self.notebook, self.history)
        self.settings_tab = SettingsTab(self.notebook, self.config)

        self.notebook.add(self.download_tab, text="  Download  ")
        self.notebook.add(self.history_tab, text="  History  ")
        self.notebook.add(self.settings_tab, text="  Settings  ")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _bind_download_manager(self):
        def on_progress(task_id: str, progress: DownloadProgress):
            self.root.after(0, self.download_tab.on_progress, task_id, progress)

        def on_complete(task_id: str, filepath: str, meta: dict):
            self.root.after(0, self.download_tab.on_complete, task_id, filepath, meta)

        def on_error(task_id: str, error: str):
            self.root.after(0, self.download_tab.on_error, task_id, error)

        self.dm.on_progress = on_progress
        self.dm.on_complete = on_complete
        self.dm.on_error = on_error

    def _on_tab_change(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 1:
            self.history_tab.reload()

    def _on_close(self):
        geo = self.root.geometry().split("+")[0]
        self.config.set("window_geometry", geo)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
