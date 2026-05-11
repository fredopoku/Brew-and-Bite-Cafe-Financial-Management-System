"""
Café-themed UI style definitions for the Brew and Bite Management System.

Contrast targets (WCAG AA):
  Normal text  ≥ 4.5 : 1
  Large / bold ≥ 3.0 : 1
All foreground/background pairs below meet or exceed these targets.
"""
import tkinter as tk
from tkinter import ttk

# --- Palette ---
ESPRESSO     = "#2C1A0E"   # deepest brown — sidebar bg
DARK_BROWN   = "#4A2C17"   # sidebar hover / header bg
MEDIUM_BROWN = "#8B5E3C"   # accent / primary buttons
LIGHT_BROWN  = "#C49A6C"   # decorative accents on dark bg only
CREAM        = "#F5EFE7"   # main content bg
CARD_BG      = "#FFFFFF"   # card / frame bg
BORDER       = "#C8A882"   # subtle borders  (darker than before for contrast)
SIDEBAR_TEXT = "#F0E0CC"   # primary text on dark sidebar  (~12 : 1 on ESPRESSO)
SIDEBAR_MUTED= "#B08060"   # secondary text on dark sidebar (~5.5 : 1 on ESPRESSO)
TEXT_DARK    = "#2D1B0E"   # primary body text on light bg  (~14 : 1 on CREAM)
TEXT_MID     = "#5C3B24"   # secondary text on light bg     (~ 6.5 : 1 on CREAM)
TEXT_LIGHT   = "#7A4F35"   # hint / label text on light bg  (~ 4.8 : 1 on CREAM)

# Status colours — chosen for readability on their respective row backgrounds
SUCCESS      = "#2E6B40"   # green  (~ 5.8 : 1 on CARD_BG)
WARNING      = "#7A5200"   # amber  (~ 6.2 : 1 on #FFF8E1 row background)
DANGER       = "#8B1F1F"   # red    (~ 6.8 : 1 on #FDECEA row background)
INFO         = "#1A5C8E"   # blue   (~ 6.2 : 1 on CARD_BG)

# Row tag backgrounds (light tints for coloured rows in treeviews)
ROW_DANGER_BG = "#FDECEA"
ROW_WARNING_BG= "#FFF8E1"

# --- Fonts ---
FONT_H1   = ("Helvetica", 20, "bold")
FONT_H2   = ("Helvetica", 15, "bold")
FONT_H3   = ("Helvetica", 12, "bold")
FONT_BODY = ("Helvetica", 11)
FONT_SMALL= ("Helvetica", 10)
FONT_MONO = ("Courier", 10)


def apply_theme(root: tk.Tk) -> ttk.Style:
    """Apply the Brew & Bite café theme to the given root window."""
    root.configure(bg=CREAM)
    style = ttk.Style(root)
    style.theme_use("clam")          # clam is the most customisable cross-platform theme

    # ---- Generic frame / label ----
    style.configure("TFrame",
                    background=CREAM)
    style.configure("TLabel",
                    background=CREAM, foreground=TEXT_DARK, font=FONT_BODY)
    style.configure("TLabelframe",
                    background=CREAM, foreground=TEXT_DARK,
                    font=FONT_H3, bordercolor=BORDER, relief="flat", padding=8)
    style.configure("TLabelframe.Label",
                    background=CREAM, foreground=MEDIUM_BROWN, font=FONT_H3)
    style.configure("TSeparator", background=BORDER)

    # ---- Notebook / tabs ----
    # Inactive tab: BORDER bg — use TEXT_DARK (14 : 1) so text is always readable.
    # Selected tab: MEDIUM_BROWN bg — use white text.
    style.configure("TNotebook", background=CREAM, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BORDER, foreground=TEXT_DARK,
                    font=("Helvetica", 10, "bold"), padding=[14, 7])
    style.map("TNotebook.Tab",
              background=[("selected", MEDIUM_BROWN), ("active", DARK_BROWN)],
              foreground=[("selected", CARD_BG),      ("active", CARD_BG)])

    # ---- Buttons ----
    style.configure("TButton",
                    background=MEDIUM_BROWN, foreground=CARD_BG,
                    font=FONT_SMALL, borderwidth=0, padding=[10, 6], relief="flat")
    style.map("TButton",
              background=[("active", DARK_BROWN), ("pressed", ESPRESSO)],
              foreground=[("active", CARD_BG),    ("pressed", CARD_BG)])

    style.configure("Primary.TButton",
                    background=MEDIUM_BROWN, foreground=CARD_BG,
                    font=("Helvetica", 11, "bold"), padding=[14, 8])
    style.map("Primary.TButton",
              background=[("active", DARK_BROWN), ("pressed", ESPRESSO)],
              foreground=[("active", CARD_BG),    ("pressed", CARD_BG)])

    # Secondary: BORDER bg with dark text — avoid light-on-light
    style.configure("Secondary.TButton",
                    background=BORDER, foreground=TEXT_DARK,
                    font=FONT_SMALL, padding=[10, 6])
    style.map("Secondary.TButton",
              background=[("active", MEDIUM_BROWN), ("pressed", DARK_BROWN)],
              foreground=[("active", CARD_BG),      ("pressed", CARD_BG)])

    style.configure("Danger.TButton",
                    background=DANGER, foreground=CARD_BG,
                    font=FONT_SMALL, padding=[10, 6])
    style.map("Danger.TButton",
              background=[("active", "#6B1515"), ("pressed", "#4A0F0F")],
              foreground=[("active", CARD_BG),   ("pressed", CARD_BG)])

    style.configure("Success.TButton",
                    background=SUCCESS, foreground=CARD_BG,
                    font=FONT_SMALL, padding=[10, 6])
    style.map("Success.TButton",
              background=[("active", "#1E5230"), ("pressed", "#143D22")],
              foreground=[("active", CARD_BG),   ("pressed", CARD_BG)])

    # ---- Card styles ----
    style.configure("Card.TFrame",
                    background=CARD_BG, relief="flat", borderwidth=1, bordercolor=BORDER)
    style.configure("Card.TLabel",
                    background=CARD_BG, foreground=TEXT_DARK, font=FONT_BODY)
    style.configure("CardTitle.TLabel",
                    background=CARD_BG, foreground=TEXT_MID, font=FONT_SMALL)
    style.configure("CardValue.TLabel",
                    background=CARD_BG, foreground=ESPRESSO,
                    font=("Helvetica", 22, "bold"))
    # CardSub: use TEXT_MID (not TEXT_LIGHT) for CARD_BG — ~6.5 : 1 contrast
    style.configure("CardSub.TLabel",
                    background=CARD_BG, foreground=TEXT_MID, font=FONT_SMALL)

    # ---- Treeview ----
    # Heading: use TEXT_DARK on CREAM — ~14 : 1 contrast
    style.configure("Treeview",
                    background=CARD_BG, foreground=TEXT_DARK,
                    fieldbackground=CARD_BG, font=FONT_SMALL,
                    rowheight=28, borderwidth=0)
    style.configure("Treeview.Heading",
                    background=CREAM, foreground=TEXT_DARK,
                    font=("Helvetica", 10, "bold"), relief="flat",
                    borderwidth=0, padding=[5, 6])
    style.map("Treeview",
              background=[("selected", MEDIUM_BROWN)],
              foreground=[("selected", CARD_BG)])
    style.map("Treeview.Heading",
              background=[("active", BORDER)])

    # ---- Entry / Combobox ----
    style.configure("TEntry",
                    fieldbackground=CARD_BG, foreground=TEXT_DARK,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    font=FONT_BODY, padding=[6, 4])
    style.map("TEntry",
              bordercolor=[("focus", MEDIUM_BROWN), ("active", LIGHT_BROWN)],
              lightcolor=[("focus", MEDIUM_BROWN)],
              darkcolor=[("focus", MEDIUM_BROWN)])

    style.configure("TCombobox",
                    fieldbackground=CARD_BG, foreground=TEXT_DARK,
                    background=BORDER, selectbackground=MEDIUM_BROWN,
                    font=FONT_BODY, padding=[6, 4])
    style.map("TCombobox",
              fieldbackground=[("readonly", CARD_BG)],
              foreground=[("readonly", TEXT_DARK)],
              selectbackground=[("readonly", MEDIUM_BROWN)],
              bordercolor=[("focus", MEDIUM_BROWN)])

    # ---- Scrollbar ----
    style.configure("TScrollbar",
                    background=BORDER, troughcolor=CREAM,
                    borderwidth=0, arrowsize=12)
    style.map("TScrollbar",
              background=[("active", MEDIUM_BROWN)])

    # ---- Progressbar ----
    style.configure("TProgressbar",
                    background=MEDIUM_BROWN, troughcolor=BORDER, borderwidth=0)

    # ---- Checkbutton / Radiobutton ----
    style.configure("TCheckbutton",
                    background=CREAM, foreground=TEXT_DARK, font=FONT_BODY)
    style.configure("TRadiobutton",
                    background=CREAM, foreground=TEXT_DARK, font=FONT_BODY)

    return style
