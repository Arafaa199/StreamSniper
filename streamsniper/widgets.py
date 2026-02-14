import io
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

from . import theme


class GradientFrame(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, **kwargs)
        self._resize_id = None
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        if self._resize_id:
            self.after_cancel(self._resize_id)
        self._resize_id = self.after(50, lambda: theme.draw_gradient(self, event.width, event.height))


class ThumbnailPreview(tk.Label):
    def __init__(self, parent, width=280, height=158, **kwargs):
        super().__init__(parent, bg=theme.BG_CARD, fg=theme.TEXT_MUTED,
                         text="No thumbnail", font=theme.FONT_SMALL,
                         width=width // 8, height=height // 16, **kwargs)
        self._target_w = width
        self._target_h = height
        self._photo: Optional[tk.PhotoImage] = None

    def load_url(self, url: str):
        if not url:
            return
        self.configure(text="Loading...")
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url: str):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "StreamSniper/2.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            try:
                from PIL import Image, ImageTk
                img = Image.open(io.BytesIO(data))
                img = img.resize((self._target_w, self._target_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            except ImportError:
                photo = tk.PhotoImage(data=data)
                pw, ph = photo.width(), photo.height()
                if pw > 0 and ph > 0:
                    xscale = max(1, pw // self._target_w)
                    yscale = max(1, ph // self._target_h)
                    photo = photo.subsample(xscale, yscale)
            self.after(0, self._set_image, photo)
        except Exception:
            self.after(0, lambda: self.configure(text="No thumbnail", image=""))

    def _set_image(self, photo):
        self._photo = photo
        self.configure(image=photo, text="")

    def clear(self):
        self._photo = None
        self.configure(image="", text="No thumbnail")


class StatusBar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.speed_var = tk.StringVar(value="")
        self.eta_var = tk.StringVar(value="")
        self.size_var = tk.StringVar(value="")

        ttk.Label(self, textvariable=self.speed_var, style="Secondary.TLabel").pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(self, textvariable=self.eta_var, style="Secondary.TLabel").pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(self, textvariable=self.size_var, style="Secondary.TLabel").pack(side=tk.LEFT)

    def update_stats(self, speed: str = "", eta: str = "", size: str = ""):
        self.speed_var.set(f"Speed: {speed}" if speed else "")
        self.eta_var.set(f"ETA: {eta}" if eta else "")
        self.size_var.set(f"Size: {size}" if size else "")

    def clear(self):
        self.speed_var.set("")
        self.eta_var.set("")
        self.size_var.set("")
