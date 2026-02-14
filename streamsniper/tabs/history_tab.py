import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

from .. import theme
from ..config import DownloadHistory


class HistoryTab(ttk.Frame):
    def __init__(self, parent, history: DownloadHistory):
        super().__init__(parent, style="TFrame")
        self.history = history
        self._sort_col = "date"
        self._sort_reverse = True
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # Search bar
        search_frame = ttk.Frame(container, style="TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(search_frame, text="Search", style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=theme.FONT)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        ttk.Button(search_frame, text="Clear All", style="Secondary.TButton",
                   command=self._clear_all).pack(side=tk.RIGHT)

        # Treeview
        cols = ("date", "title", "format", "size", "path")
        self.tree = ttk.Treeview(container, columns=cols, show="headings",
                                  selectmode="browse")

        self.tree.heading("date", text="Date", command=lambda: self._sort("date"))
        self.tree.heading("title", text="Title", command=lambda: self._sort("title"))
        self.tree.heading("format", text="Format", command=lambda: self._sort("format"))
        self.tree.heading("size", text="Size (MB)", command=lambda: self._sort("size"))
        self.tree.heading("path", text="Path", command=lambda: self._sort("path"))

        self.tree.column("date", width=140, minwidth=100)
        self.tree.column("title", width=300, minwidth=150)
        self.tree.column("format", width=70, minwidth=50)
        self.tree.column("size", width=80, minwidth=60)
        self.tree.column("path", width=250, minwidth=100)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right-click menu
        self.context_menu = tk.Menu(self, tearoff=0, bg=theme.BG_CARD,
                                     fg=theme.TEXT_PRIMARY, activebackground=theme.BG_HOVER,
                                     activeforeground=theme.TEXT_PRIMARY, font=theme.FONT_SMALL)
        self.context_menu.add_command(label="Open file", command=self._open_file)
        self.context_menu.add_command(label="Open folder", command=self._open_folder)
        self.context_menu.add_command(label="Copy URL", command=self._copy_url)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete entry", command=self._delete_entry)

        self.tree.bind("<Button-2>", self._show_context)
        self.tree.bind("<Button-3>", self._show_context)

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        q = self.search_var.get().strip()
        entries = self.history.search(q) if q else self.history.all()
        for entry in entries:
            ts = entry.get("timestamp", "")[:16].replace("T", " ")
            self.tree.insert("", tk.END, values=(
                ts,
                entry.get("title", "")[:60],
                entry.get("format", ""),
                f"{entry.get('filesize_mb', 0):.1f}",
                entry.get("path", ""),
            ))

    def _sort(self, col: str):
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = True
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort(reverse=self._sort_reverse)
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, "", idx)

    def _selected_entry(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        idx = self.tree.index(sel[0])
        q = self.search_var.get().strip()
        entries = self.history.search(q) if q else self.history.all()
        if 0 <= idx < len(entries):
            return idx, entries[idx]
        return None, None

    def _show_context(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _open_file(self):
        _, entry = self._selected_entry()
        if entry and os.path.exists(entry.get("path", "")):
            path = entry["path"]
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])

    def _open_folder(self):
        _, entry = self._selected_entry()
        if entry:
            folder = os.path.dirname(entry.get("path", ""))
            if os.path.isdir(folder):
                if sys.platform == "darwin":
                    subprocess.Popen(["open", folder])
                elif sys.platform == "win32":
                    os.startfile(folder)
                else:
                    subprocess.Popen(["xdg-open", folder])

    def _copy_url(self):
        _, entry = self._selected_entry()
        if entry:
            self.clipboard_clear()
            self.clipboard_append(entry.get("url", ""))

    def _delete_entry(self):
        idx, _ = self._selected_entry()
        if idx is not None:
            self.history.remove(idx)
            self._refresh()

    def _clear_all(self):
        self.history.clear()
        self._refresh()

    def reload(self):
        self._refresh()
