"""styles.py — Theme system with Light / Dark mode toggle."""

import tkinter as tk
from tkinter import ttk

# ── Shared / accent colors (same in both modes) ────────────────
ACCENT      = "#7C3AED"
ACCENT2     = "#F97316"
GREEN       = "#10B981"
RED         = "#EF4444"
YELLOW      = "#F59E0B"
SIDEBAR_BG  = "#7C3AED"
SIDEBAR_ACT = "#6D28D9"
WHITE       = "#FFFFFF"

# ── Fonts ──────────────────────────────────────────────────────
FONT_TITLE = ("Helvetica", 22, "bold")
FONT_LABEL = ("Helvetica", 10, "bold")
FONT_BODY  = ("Helvetica", 10)
FONT_SMALL = ("Helvetica", 9)

# ── Theme palettes ─────────────────────────────────────────────
THEMES = {
    "light": {
        "BG":        "#F5F6FA",
        "CARD":      "#FFFFFF",
        "TEXT_DARK": "#1E1B4B",
        "TEXT_MUTED":"#6B7280",
        "BORDER":    "#E5E7EB",
        "ENTRY_BG":  "#FFFFFF",
        "ENTRY_FG":  "#1E1B4B",
        "TREE_BG":   "#FFFFFF",
        "TREE_FG":   "#1E1B4B",
        "TREE_HEAD": "#F3F4F6",
        "TREE_SEL":  "#EDE9FE",
        "TOGGLE_ICO":"🌙  Dark Mode",
        # row highlight
        "ROW_EXPIRED":  "#FECACA",
        "ROW_EXPIRING": "#FEF3C7",
        "ROW_ACTIVE":   "#D1FAE5",
        # info cards
        "REV_BG":   "#F0FDF4", "REV_BORDER": "#BBF7D0",
        "TOP_BG":   "#FFF7ED", "TOP_BORDER": "#FED7AA",
        "EXP_BG":   "#FFFBEB", "EXP_BORDER": "#FDE68A",
        "TIP_BG":   "#EDE9FE", "TIP_BORDER": "#C4B5FD",
    },
    "dark": {
        "BG":        "#0F0F0F",
        "CARD":      "#1A1A1A",
        "TEXT_DARK": "#F0F0F0",
        "TEXT_MUTED":"#9CA3AF",
        "BORDER":    "#2D2D2D",
        "ENTRY_BG":  "#242424",
        "ENTRY_FG":  "#F0F0F0",
        "TREE_BG":   "#1A1A1A",
        "TREE_FG":   "#F0F0F0",
        "TREE_HEAD": "#242424",
        "TREE_SEL":  "#2E1A6E",
        "TOGGLE_ICO":"☀️  Light Mode",
        # row highlight
        "ROW_EXPIRED":  "#4C1C1C",
        "ROW_EXPIRING": "#4C3A00",
        "ROW_ACTIVE":   "#0D3325",
        # info cards
        "REV_BG":   "#0D2B1E", "REV_BORDER": "#14532D",
        "TOP_BG":   "#2C1A0A", "TOP_BORDER": "#7C2D12",
        "EXP_BG":   "#2C2000", "EXP_BORDER": "#78350F",
        "TIP_BG":   "#1E1040", "TIP_BORDER": "#4C1D95",
    },
}

# ── Active theme state (mutable dict) ─────────────────────────
_T = dict(THEMES["light"])   # starts in light mode
_mode = ["light"]            # track current mode name


def current_mode() -> str:
    return _mode[0]


def toggle_theme():
    new = "dark" if _mode[0] == "light" else "light"
    _mode[0] = new
    _T.clear()
    _T.update(THEMES[new])


def t(key: str) -> str:
    """Get a theme color by key."""
    return _T.get(key, "#FF00FF")   # hot-pink fallback = bug indicator


# ── Treeview style (call after every theme switch) ────────────
def apply_treeview_style():
    sty = ttk.Style()
    sty.theme_use("clam")
    sty.configure("L.Treeview",
                  background=t("TREE_BG"), foreground=t("TREE_FG"),
                  fieldbackground=t("TREE_BG"), rowheight=32,
                  font=FONT_BODY, borderwidth=0)
    sty.configure("L.Treeview.Heading",
                  background=t("TREE_HEAD"), foreground=ACCENT,
                  font=FONT_LABEL, relief="flat")
    sty.map("L.Treeview",
            background=[("selected", t("TREE_SEL"))],
            foreground=[("selected", ACCENT)])


# ── Widget helpers (use theme colors) ─────────────────────────
def entry_widget(parent, **kw):
    return tk.Entry(
        parent, bg=t("ENTRY_BG"), fg=t("ENTRY_FG"), relief="solid", bd=1,
        font=FONT_BODY, insertbackground=ACCENT,
        highlightthickness=2, highlightbackground=t("BORDER"),
        highlightcolor=ACCENT, **kw
    )


def pill_btn(parent, text, cmd, bg=ACCENT, fg=WHITE, **kw):
    return tk.Button(
        parent, text=text, command=cmd, bg=bg, fg=fg,
        font=("Helvetica", 10, "bold"), relief="flat",
        cursor="hand2", padx=14, pady=7,
        activebackground=ACCENT2, activeforeground=WHITE, **kw
    )


def divider(parent):
    tk.Frame(parent, bg=t("BORDER"), height=1).pack(fill="x", padx=36, pady=16)
