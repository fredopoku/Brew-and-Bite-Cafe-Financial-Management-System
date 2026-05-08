"""Canvas-based chart widgets — no external library dependencies required."""
import tkinter as tk

try:
    from src.gui.styles import (CARD_BG, BORDER, TEXT_DARK, TEXT_MID,
                                 MEDIUM_BROWN, DARK_BROWN, CREAM,
                                 SUCCESS, WARNING, DANGER)
    _HAS_STYLES = True
except ImportError:
    _HAS_STYLES = False
    CARD_BG = "white"; BORDER = "#d4b896"; TEXT_DARK = "#2D1B0E"
    TEXT_MID = "#5C3B24"; MEDIUM_BROWN = "#8B5E3C"; DARK_BROWN = "#4A2C17"
    CREAM = "#F5EFE7"; SUCCESS = "#2E6B40"; WARNING = "#7A5200"; DANGER = "#8B1F1F"


class BarChart(tk.Canvas):
    """Vertical bar chart drawn with the Tk Canvas — no matplotlib required."""

    _PAD_LEFT   = 58
    _PAD_RIGHT  = 14
    _PAD_TOP    = 32
    _PAD_BOTTOM = 46

    def __init__(self, parent, title: str = "", bar_color: str = None,
                 value_prefix: str = "$", bg: str = None, **kwargs):
        super().__init__(
            parent,
            bg=bg or CARD_BG,
            highlightthickness=0,
            **kwargs
        )
        self._title  = title
        self._color  = bar_color or MEDIUM_BROWN
        self._prefix = value_prefix
        self._data: list = []          # list of (label, value) tuples
        self.bind("<Configure>", lambda _: self.after(20, self._draw))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_data(self, data: list):
        """Replace chart data and redraw. data = [(label, value), ...]"""
        self._data = list(data)
        self._draw()

    # ------------------------------------------------------------------
    # Internal drawing
    # ------------------------------------------------------------------
    def _draw(self):
        self.delete("all")
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 80 or H < 80:
            return

        PL = self._PAD_LEFT
        PR = self._PAD_RIGHT
        PT = self._PAD_TOP
        PB = self._PAD_BOTTOM
        cw = W - PL - PR
        ch = H - PT - PB

        # Title
        if self._title:
            self.create_text(
                PL + cw // 2, PT // 2,
                text=self._title,
                fill=TEXT_DARK,
                font=("Helvetica", 10, "bold"),
                anchor="center",
            )

        if not self._data:
            self.create_text(
                W // 2, H // 2,
                text="No data available yet",
                fill=TEXT_MID,
                font=("Helvetica", 10, "italic"),
            )
            return

        values = [max(0.0, v) for _, v in self._data]
        max_v  = max(values) if any(v > 0 for v in values) else 1.0

        # Horizontal gridlines + Y-axis labels
        for i in range(5):
            frac = i / 4
            y    = PT + ch - frac * ch
            self.create_line(PL, y, W - PR, y, fill=BORDER, dash=(2, 5))
            self.create_text(
                PL - 5, y,
                text=self._fmt(max_v * frac),
                anchor="e",
                fill=TEXT_MID,
                font=("Helvetica", 8),
            )

        # Bars
        n      = len(self._data)
        slot_w = cw / n
        bar_w  = max(8.0, min(slot_w * 0.60, 64.0))

        for i, (label, value) in enumerate(self._data):
            cx    = PL + slot_w * i + slot_w / 2
            bar_h = (value / max_v) * ch
            x0    = cx - bar_w / 2
            x1    = cx + bar_w / 2
            y0    = PT + ch - bar_h
            y1    = PT + ch

            if bar_h >= 1:
                self.create_rectangle(x0, y0, x1, y1,
                                      fill=self._color, outline="", width=0)
                cap_h = min(bar_h * 0.12, 5)
                if cap_h >= 1:
                    self.create_rectangle(x0, y0, x1, y0 + cap_h,
                                          fill=DARK_BROWN, outline="", width=0)

            if bar_h > 22:
                self.create_text(
                    cx, y0 + 11,
                    text=self._fmt(value),
                    fill="white",
                    font=("Helvetica", 7, "bold"),
                )

            # X-axis label (max 7 chars to avoid overlap)
            lbl_text = str(label)
            if len(lbl_text) > 7:
                lbl_text = lbl_text[:7]
            self.create_text(
                cx, H - PB + 13,
                text=lbl_text,
                fill=TEXT_MID,
                font=("Helvetica", 8),
            )

        # Axis lines
        self.create_line(PL, PT,      PL,      PT + ch, fill=TEXT_MID, width=1)
        self.create_line(PL, PT + ch, W - PR,  PT + ch, fill=TEXT_MID, width=1)

    def _fmt(self, v: float) -> str:
        if self._prefix == "$":
            return f"${v:,.0f}" if v >= 1 else f"${v:.2f}"
        return f"{self._prefix}{v:,.0f}"


class DonutChart(tk.Canvas):
    """Simple donut / pie chart for up to 8 slices."""

    _COLORS = [MEDIUM_BROWN, SUCCESS, WARNING, DANGER, DARK_BROWN,
               "#1A5C8E", "#6B3A7D", "#2E7D7D"]

    def __init__(self, parent, title: str = "", bg: str = None, **kwargs):
        super().__init__(parent, bg=bg or CARD_BG,
                         highlightthickness=0, **kwargs)
        self._title = title
        self._data: list = []
        self.bind("<Configure>", lambda _: self.after(20, self._draw))

    def set_data(self, data: list):
        """data = [(label, value), ...] — up to 8 slices."""
        self._data = list(data[:8])
        self._draw()

    def _draw(self):
        self.delete("all")
        W, H = self.winfo_width(), self.winfo_height()
        if W < 60 or H < 60:
            return

        if self._title:
            self.create_text(W // 2, 14, text=self._title,
                             fill=TEXT_DARK, font=("Helvetica", 10, "bold"))

        if not self._data:
            self.create_text(W // 2, H // 2, text="No data",
                             fill=TEXT_MID, font=("Helvetica", 10, "italic"))
            return

        total = sum(v for _, v in self._data)
        if total <= 0:
            return

        # Chart occupies left 60%, legend right 40%
        cx  = W * 0.30
        cy  = H * 0.50
        r   = min(cx - 10, cy - 26)
        ri  = r * 0.55     # inner radius (donut hole)

        angle = -90.0
        for idx, (label, value) in enumerate(self._data):
            sweep = (value / total) * 360.0
            color = self._COLORS[idx % len(self._COLORS)]
            self.create_arc(cx - r, cy - r, cx + r, cy + r,
                            start=angle, extent=sweep,
                            fill=color, outline=CARD_BG, width=2,
                            style="pieslice")
            angle += sweep

        # Donut hole
        self.create_oval(cx - ri, cy - ri, cx + ri, cy + ri,
                         fill=CARD_BG, outline="")
        self.create_text(cx, cy, text=f"${total:,.0f}",
                         fill=TEXT_DARK, font=("Helvetica", 9, "bold"))

        # Legend
        lx = W * 0.62
        ly = H * 0.12
        row_h = min(22, (H - 24) / max(len(self._data), 1))

        for idx, (label, value) in enumerate(self._data):
            color = self._COLORS[idx % len(self._COLORS)]
            y = ly + idx * row_h
            self.create_rectangle(lx, y + 2, lx + 10, y + 12,
                                  fill=color, outline="")
            pct = (value / total) * 100
            self.create_text(lx + 14, y + 7,
                             text=f"{label[:14]} ({pct:.0f}%)",
                             anchor="w", fill=TEXT_DARK,
                             font=("Helvetica", 8))
