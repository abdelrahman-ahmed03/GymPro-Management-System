"""main.py — GymPro entry point with Login + Light/Dark toggle."""

import tkinter as tk
from tkinter import messagebox
import styles
from styles import (ACCENT, ACCENT2, GREEN, SIDEBAR_BG, SIDEBAR_ACT,
                    FONT_LABEL, FONT_BODY, WHITE, entry_widget, pill_btn, t, toggle_theme)
from database import GymDatabase
from dashboard import DashboardFrame
from members   import MembersFrame
from trainers  import TrainersFrame
from users     import UsersFrame


# ──────────────────────────────────────────────────────────────
#  LOGIN WINDOW
# ──────────────────────────────────────────────────────────────
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db           = GymDatabase()
        self.result_user  = None
        self.title("GymPro — Login")
        self.configure(bg=t("BG"))
        self.resizable(False, False)
        self._build()
        self.eval("tk::PlaceWindow . center")

    def _build(self):
        # Card
        card = tk.Frame(self, bg=t("CARD"), padx=48, pady=40,
                        highlightthickness=1, highlightbackground=t("BORDER"))
        card.pack(padx=40, pady=40)

        tk.Label(card, text="💪", font=("Helvetica", 44),
                 bg=t("CARD"), fg=ACCENT).pack()
        tk.Label(card, text="GymPro", font=("Helvetica", 22, "bold"),
                 bg=t("CARD"), fg=t("TEXT_DARK")).pack()
        tk.Label(card, text="Sign in to continue",
                 font=FONT_BODY, bg=t("CARD"), fg=t("TEXT_MUTED")).pack(pady=(4, 24))

        tk.Label(card, text="Username", font=FONT_LABEL,
                 bg=t("CARD"), fg=t("TEXT_MUTED")).pack(anchor="w")
        self.e_user = entry_widget(card, width=28)
        self.e_user.pack(fill="x", pady=(2, 12))

        tk.Label(card, text="Password", font=FONT_LABEL,
                 bg=t("CARD"), fg=t("TEXT_MUTED")).pack(anchor="w")
        self.e_pass = entry_widget(card, width=28, show="●")
        self.e_pass.pack(fill="x", pady=(2, 20))
        self.e_pass.bind("<Return>", lambda _: self._login())

        pill_btn(card, "Sign In →", self._login).pack(fill="x", ipady=4)

        tk.Label(card, text="Default: admin / admin123",
                 font=("Helvetica", 8), bg=t("CARD"), fg=t("TEXT_MUTED")).pack(pady=(12, 0))

    def _login(self):
        user = self.db.login(self.e_user.get().strip(), self.e_pass.get())
        if user:
            self.result_user = user
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            self.e_pass.delete(0, "end")


# ──────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ──────────────────────────────────────────────────────────────
class GymApp(tk.Tk):
    def __init__(self, db: GymDatabase, user: tuple):
        super().__init__()
        self.db           = db
        self.current_user = user   # (id, username, role)
        self.title("🏋️  GymPro — Management System")
        self.configure(bg=t("BG"))
        self.geometry("1150x730")
        self.minsize(960, 620)
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._quit)

    def _quit(self):
        self.db.close()
        self.destroy()

    # ── Build sidebar + content area ──────────────────────────
    def _build(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=215)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="💪", font=("Helvetica", 36),
                 bg=SIDEBAR_BG, fg=WHITE).pack(pady=(26, 0))
        tk.Label(self.sidebar, text="GymPro",
                 font=("Helvetica", 18, "bold"), bg=SIDEBAR_BG, fg=WHITE).pack()
        tk.Label(self.sidebar, text="Management System",
                 font=("Helvetica", 8), bg=SIDEBAR_BG, fg="#C4B5FD").pack(pady=(0, 4))

        # Logged-in user badge
        role_color = {"Admin": "#FCD34D", "Manager": "#6EE7B7"}.get(
            self.current_user[2], "#C4B5FD")
        tk.Label(self.sidebar,
                 text=f"  👤 {self.current_user[1]}  [{self.current_user[2]}]  ",
                 font=("Helvetica", 8, "bold"), bg=SIDEBAR_ACT,
                 fg=role_color, pady=4).pack(fill="x", padx=14, pady=(4, 16))

        tk.Frame(self.sidebar, bg="#5B21B6", height=1).pack(fill="x", padx=14)

        # Nav buttons
        self._nav = {}
        tabs = [("Dashboard", "🏠"), ("Members", "👤"),
                ("Trainers", "🏋️"), ("Users", "🔐")]
        for name, icon in tabs:
            if name == "Users" and self.current_user[2] != "Admin":
                continue   # hide Users tab for non-admins
            btn = tk.Button(self.sidebar,
                            text=f"  {icon}   {name}", anchor="w",
                            bg=SIDEBAR_BG, fg="#DDD6FE",
                            font=("Helvetica", 12), relief="flat",
                            cursor="hand2", pady=13,
                            activebackground=SIDEBAR_ACT, activeforeground=WHITE,
                            command=lambda n=name: self._switch(n))
            btn.pack(fill="x", padx=10, pady=2)
            self._nav[name] = btn

        # ── Theme toggle button ────────────────────────────────
        tk.Frame(self.sidebar, bg="#5B21B6", height=1).pack(fill="x", padx=14, pady=(16, 8))

        self.theme_btn = tk.Button(
            self.sidebar,
            text=t("TOGGLE_ICO"),
            bg="#5B21B6", fg=WHITE,
            font=("Helvetica", 10, "bold"), relief="flat",
            cursor="hand2", pady=10,
            activebackground=SIDEBAR_ACT, activeforeground=WHITE,
            command=self._toggle_theme
        )
        self.theme_btn.pack(fill="x", padx=10, pady=2)

        # Logout
        tk.Frame(self.sidebar, bg="#5B21B6", height=1).pack(fill="x", padx=14, pady=(8, 8))
        tk.Button(self.sidebar, text="  🚪   Logout", anchor="w",
                  bg=SIDEBAR_BG, fg="#FCA5A5", font=("Helvetica", 11),
                  relief="flat", cursor="hand2", pady=10,
                  activebackground="#7F1D1D", activeforeground=WHITE,
                  command=self._logout).pack(fill="x", padx=10, pady=2)

        tk.Label(self.sidebar, text="v2.0.0", font=("Helvetica", 8),
                 bg=SIDEBAR_BG, fg="#6D28D9").pack(side="bottom", pady=10)

        # Content
        self.content = tk.Frame(self, bg=t("BG"))
        self.content.pack(side="left", fill="both", expand=True)

        self.frames = {
            "Dashboard": DashboardFrame(self.content, self),
            "Members":   MembersFrame(self.content, self),
            "Trainers":  TrainersFrame(self.content, self),
            "Users":     UsersFrame(self.content, self),
        }
        for f in self.frames.values():
            f.place(relwidth=1, relheight=1)

        self._switch("Dashboard")

    # ── Navigation ────────────────────────────────────────────
    def _switch(self, name):
        for n, b in self._nav.items():
            b.config(bg=SIDEBAR_ACT if n == name else SIDEBAR_BG,
                     fg=WHITE if n == name else "#DDD6FE")
        self.frames[name].tkraise()
        if hasattr(self.frames[name], "refresh"):
            self.frames[name].refresh()

    # ── Theme toggle ──────────────────────────────────────────
    def _toggle_theme(self):
        toggle_theme()                          # flip the palette
        styles.apply_treeview_style()           # update ttk style

        # Re-theme the content background
        self.content.configure(bg=t("BG"))
        self.configure(bg=t("BG"))

        # Ask every frame to rebuild itself with new colors
        for f in self.frames.values():
            if hasattr(f, "retheme"):
                f.retheme()

        # Update toggle button label
        self.theme_btn.config(text=t("TOGGLE_ICO"))

        # Re-raise current tab
        for name, btn in self._nav.items():
            if btn.cget("bg") == SIDEBAR_ACT:
                self.frames[name].tkraise()
                break

    # ── Logout ────────────────────────────────────────────────
    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.close()
            self.destroy()
            main()   # restart from login


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────
def main():
    login = LoginWindow()
    login.mainloop()
    if login.result_user:
        app = GymApp(login.db, login.result_user)
        app.mainloop()


if __name__ == "__main__":
    main()
