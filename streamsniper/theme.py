import sys
import tkinter as tk
from tkinter import ttk

BG_DARK = "#0a0e1a"
BG_CARD = "#141a2e"
BG_INPUT = "#1c2342"
BG_HOVER = "#252d50"
TEXT_PRIMARY = "#e8eaf0"
TEXT_SECONDARY = "#8b92a8"
TEXT_MUTED = "#555d78"
ACCENT = "#e63946"
ACCENT_HOVER = "#ff4d5a"
SUCCESS = "#2ecc71"
BORDER = "#2a3154"
GRADIENT_TOP = "#0a0e1a"
GRADIENT_BOTTOM = "#1a0a12"

FONT_FAMILY = "SF Pro Display"
if sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "linux":
    FONT_FAMILY = "Liberation Sans"

FONT = (FONT_FAMILY, 12)
FONT_BOLD = (FONT_FAMILY, 12, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_HEADING = (FONT_FAMILY, 14, "bold")


def configure_ttk_styles():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=BG_DARK, foreground=TEXT_PRIMARY,
                     font=FONT, borderwidth=0)

    style.configure("TNotebook", background=BG_DARK, borderwidth=0,
                     tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab", background=BG_CARD, foreground=TEXT_SECONDARY,
                     padding=[20, 10], font=FONT_BOLD)
    style.map("TNotebook.Tab",
              background=[("selected", BG_DARK), ("active", BG_HOVER)],
              foreground=[("selected", ACCENT), ("active", TEXT_PRIMARY)])

    style.configure("TFrame", background=BG_DARK)
    style.configure("Card.TFrame", background=BG_CARD)

    style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT)
    style.configure("Secondary.TLabel", foreground=TEXT_SECONDARY, font=FONT_SMALL)
    style.configure("Title.TLabel", font=FONT_TITLE)
    style.configure("Heading.TLabel", font=FONT_HEADING)

    style.configure("TEntry", fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                     insertcolor=TEXT_PRIMARY, borderwidth=1, padding=8)
    style.map("TEntry", bordercolor=[("focus", ACCENT), ("!focus", BORDER)])

    style.configure("Accent.TButton", background=ACCENT, foreground="white",
                     font=FONT_BOLD, padding=[20, 10], borderwidth=0)
    style.map("Accent.TButton",
              background=[("active", ACCENT_HOVER), ("disabled", TEXT_MUTED)])

    style.configure("Secondary.TButton", background=BG_CARD, foreground=TEXT_PRIMARY,
                     font=FONT, padding=[16, 8], borderwidth=1)
    style.map("Secondary.TButton",
              background=[("active", BG_HOVER)],
              bordercolor=[("!disabled", BORDER)])

    style.configure("TCombobox", fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                     selectbackground=ACCENT, selectforeground="white",
                     borderwidth=1, padding=6)
    style.map("TCombobox", bordercolor=[("focus", ACCENT), ("!focus", BORDER)],
              fieldbackground=[("readonly", BG_INPUT)])

    style.configure("red.Horizontal.TProgressbar",
                     troughcolor=BG_INPUT, background=ACCENT,
                     borderwidth=0, thickness=6)

    style.configure("Treeview", background=BG_CARD, foreground=TEXT_PRIMARY,
                     fieldbackground=BG_CARD, borderwidth=0, font=FONT_SMALL,
                     rowheight=32)
    style.configure("Treeview.Heading", background=BG_DARK, foreground=TEXT_SECONDARY,
                     font=FONT_BOLD, borderwidth=0)
    style.map("Treeview",
              background=[("selected", BG_HOVER)],
              foreground=[("selected", TEXT_PRIMARY)])
    style.map("Treeview.Heading",
              background=[("active", BG_HOVER)])

    style.configure("TCheckbutton", background=BG_DARK, foreground=TEXT_PRIMARY,
                     font=FONT, indicatorbackground=BG_INPUT,
                     indicatorforeground=ACCENT)
    style.map("TCheckbutton",
              indicatorbackground=[("selected", ACCENT)],
              background=[("active", BG_DARK)])

    style.configure("TRadiobutton", background=BG_DARK, foreground=TEXT_PRIMARY,
                     font=FONT, indicatorbackground=BG_INPUT)
    style.map("TRadiobutton",
              indicatorbackground=[("selected", ACCENT)],
              background=[("active", BG_DARK)])


def draw_gradient(canvas: tk.Canvas, width: int, height: int):
    canvas.delete("gradient")
    r1, g1, b1 = int(GRADIENT_TOP[1:3], 16), int(GRADIENT_TOP[3:5], 16), int(GRADIENT_TOP[5:7], 16)
    r2, g2, b2 = int(GRADIENT_BOTTOM[1:3], 16), int(GRADIENT_BOTTOM[3:5], 16), int(GRADIENT_BOTTOM[5:7], 16)
    bands = max(1, height // 4)
    band_h = height / bands
    for i in range(bands):
        t = i / max(1, bands - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y0 = int(i * band_h)
        y1 = int((i + 1) * band_h) + 1
        canvas.create_rectangle(0, y0, width, y1, fill=color, outline="", tags="gradient")
    canvas.tag_lower("gradient")
