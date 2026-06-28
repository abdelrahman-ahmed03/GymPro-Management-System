"""dashboard.py — Enhanced Dashboard (theme-aware)."""

import tkinter as tk
from datetime import datetime
import styles
from styles import (ACCENT, ACCENT2, GREEN, RED,
                    FONT_LABEL, FONT_BODY, pill_btn, divider, t)


class DashboardFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=t("BG"))
        self.app = app
        self._widgets = []   # track for re-theming
        self._build()

    def _build(self):
        # Greeting
        self.top = tk.Frame(self, bg=t("BG"))
        self.top.pack(fill="x", padx=36, pady=(28, 4))
        tk.Label(self.top, text="Good day! 👋",
                 font=("Helvetica", 26, "bold"),
                 bg=t("BG"), fg=t("TEXT_DARK")).pack(anchor="w")
        tk.Label(self.top, text=datetime.now().strftime("%A, %d %B %Y"),
                 font=FONT_BODY, bg=t("BG"), fg=t("TEXT_MUTED")).pack(anchor="w")

        # Stat cards
        self.cards_row = tk.Frame(self, bg=t("BG"))
        self.cards_row.pack(fill="x", padx=36, pady=(18, 0))

        self._vars = {}
        stats = [
            ("total_members",  "Total Members",  "👤", ACCENT),
            ("active_members", "Active Members", "✅", GREEN),
            ("expired",        "Expired",        "⚠️",  RED),
            ("total_trainers", "Trainers",       "🏋️", ACCENT2),
        ]
        for key, label, icon, color in stats:
            var = tk.StringVar(value="0")
            self._vars[key] = var
            card = tk.Frame(self.cards_row, bg=t("CARD"),
                            highlightthickness=1, highlightbackground=t("BORDER"))
            card.pack(side="left", padx=(0, 12), ipadx=14, ipady=6)
            tk.Label(card, text=icon, font=("Helvetica", 24),
                     bg=t("CARD"), fg=color).pack(anchor="w", padx=14, pady=(14, 2))
            tk.Label(card, textvariable=var,
                     font=("Helvetica", 36, "bold"),
                     bg=t("CARD"), fg=color).pack(anchor="w", padx=14)
            tk.Label(card, text=label, font=FONT_BODY,
                     bg=t("CARD"), fg=t("TEXT_MUTED")).pack(anchor="w", padx=14, pady=(0, 14))

        divider(self)

        # Revenue / Top Trainer / Expiring
        info_row = tk.Frame(self, bg=t("BG"))
        info_row.pack(fill="x", padx=36, pady=(0, 8))

        def info_card(parent, bg, border, icon_text, icon_color, label_text, var_font=30):
            card = tk.Frame(parent, bg=bg,
                            highlightthickness=1, highlightbackground=border)
            card.pack(side="left", padx=(0, 16), ipadx=20, ipady=12)
            tk.Label(card, text=icon_text, font=FONT_LABEL,
                     bg=bg, fg=icon_color).pack(anchor="w", padx=16, pady=(12, 4))
            v = tk.StringVar(value="—")
            tk.Label(card, textvariable=v,
                     font=("Helvetica", var_font, "bold"),
                     bg=bg, fg=icon_color).pack(anchor="w", padx=16, pady=(0, 12))
            return v

        self.rev_var = info_card(info_row,
            t("REV_BG"), t("REV_BORDER"), "💰", GREEN, "Monthly Revenue")
        
        self.top_var = info_card(info_row,
            t("TOP_BG"), t("TOP_BORDER"), "🏆", ACCENT2, "Highest-Paid Trainer", var_font=13)
        
        self.exp_var = info_card(info_row,
            t("EXP_BG"), t("EXP_BORDER"), "⏰", "#B45309", "Expiring in 7 Days")

        divider(self)

        # Quick actions
        tk.Label(self, text="Quick actions",
                 font=("Helvetica", 13, "bold"),
                 bg=t("BG"), fg=t("TEXT_DARK")).pack(anchor="w", padx=36, pady=(0, 10))
        act = tk.Frame(self, bg=t("BG"))
        act.pack(anchor="w", padx=36)
        pill_btn(act, "➕  Add Member",   lambda: self.app._switch("Members")).pack(side="left", padx=(0, 10))
        pill_btn(act, "➕  Add Trainer",  lambda: self.app._switch("Trainers"), bg=ACCENT2).pack(side="left", padx=(0, 10))
        pill_btn(act, "👥  Manage Users", lambda: self.app._switch("Users"),
                 bg=t("CARD"), fg=t("TEXT_DARK")).pack(side="left")

        # Tip banner
        banner = tk.Frame(self, bg=t("TIP_BG"),
                          highlightthickness=1, highlightbackground=t("TIP_BORDER"))
        banner.pack(fill="x", padx=36, pady=20)
        tk.Label(banner,
                 text="  💡  Tip: Expired memberships are highlighted in red in the Members tab.",
                 font=FONT_BODY, bg=t("TIP_BG"), fg=ACCENT, pady=10).pack(anchor="w")

    def tkraise(self):
        super().tkraise()
        self.refresh()

    def refresh(self):
        s = self.app.db.get_stats()
        for key, var in self._vars.items():
            var.set(str(s.get(key, 0)))
        self.rev_var.set(f"${s['revenue']:,.0f}")
        top = s.get("top_trainer")
        self.top_var.set(f"{top[0]}  (${top[1]:,.0f})" if top else "No trainers yet")
        self.exp_var.set(str(s.get("expiring_soon", 0)))

    def retheme(self):
        self._destroy_children()
        self.configure(bg=t("BG"))
        self._build()
        self.refresh()

    def _destroy_children(self):
        for w in self.winfo_children():
            w.destroy()
