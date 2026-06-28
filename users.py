"""users.py — User management tab (theme-aware)."""

import tkinter as tk
from tkinter import ttk, messagebox

import styles
from styles import (ACCENT, ACCENT2, GREEN, FONT_TITLE, FONT_LABEL, FONT_BODY,
                    apply_treeview_style, entry_widget, pill_btn, t)


class UsersFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=t("BG"))
        self.app     = app
        self._sel_id = None
        self._build()

    def _build(self):
        apply_treeview_style()

        hdr = tk.Frame(self, bg=t("BG"))
        hdr.pack(fill="x", padx=36, pady=(24, 0))
        tk.Label(hdr, text="🔐  User Management", font=FONT_TITLE,
                 bg=t("BG"), fg=t("TEXT_DARK")).pack(side="left")
        tk.Label(hdr, text="Admin only", font=("Helvetica", 10),
                 bg=t("TIP_BG"), fg=ACCENT, padx=8, pady=4).pack(side="left", padx=12)

        fc = tk.Frame(self, bg=t("CARD"),
                      highlightthickness=1, highlightbackground=t("BORDER"))
        fc.pack(fill="x", padx=36, pady=14)
        inner = tk.Frame(fc, bg=t("CARD"), padx=16, pady=12)
        inner.pack(fill="x")

        for col, (label, attr, kw) in enumerate([
            ("Username", "e_user", {}),
            ("Password", "e_pass", {"show": "●"}),
        ]):
            tk.Label(inner, text=label, font=FONT_LABEL,
                     bg=t("CARD"), fg=t("TEXT_MUTED")).grid(
                row=0, column=col, sticky="w", padx=(0, 4), pady=(4, 2))
            e = entry_widget(inner, width=20, **kw)
            e.grid(row=1, column=col, padx=(0, 16), pady=(0, 8), sticky="w")
            setattr(self, attr, e)

        tk.Label(inner, text="Role", font=FONT_LABEL,
                 bg=t("CARD"), fg=t("TEXT_MUTED")).grid(
            row=0, column=2, sticky="w", padx=(0, 4), pady=(4, 2))
        self.role_var = tk.StringVar(value="Receptionist")
        ttk.Combobox(inner, textvariable=self.role_var,
                     values=["Admin", "Receptionist", "Manager"],
                     state="readonly", width=16, font=FONT_BODY).grid(
            row=1, column=2, padx=(0, 16), pady=(0, 8), sticky="w")

        br = tk.Frame(self, bg=t("BG"))
        br.pack(anchor="w", padx=36, pady=(0, 12))
        pill_btn(br, "➕  Add User",    self._add,    bg=GREEN).pack(side="left", padx=(0, 8))
        pill_btn(br, "🗑️  Delete User", self._delete, bg=ACCENT2).pack(side="left", padx=(0, 8))
        pill_btn(br, "✖  Clear",       self._clear,  bg=t("CARD"), fg=t("TEXT_MUTED")).pack(side="left")

        cols = ("ID", "Username", "Role")
        tf = tk.Frame(self, bg=t("BG"))
        tf.pack(fill="both", expand=True, padx=36, pady=(0, 24))

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", style="L.Treeview")
        self.tree.heading("ID",       text="ID");       self.tree.column("ID",       width=40,  anchor="center")
        self.tree.heading("Username", text="Username"); self.tree.column("Username", width=200, anchor="w")
        self.tree.heading("Role",     text="Role");     self.tree.column("Role",     width=160, anchor="center")

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        self.refresh()

    def refresh(self):
        rows = self.app.db.get_all_users()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    def _on_sel(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        self._sel_id = self.tree.item(sel[0])["values"][0]

    def _add(self):
        u, p, r = self.e_user.get().strip(), self.e_pass.get(), self.role_var.get()
        if not u or not p:
            messagebox.showwarning("Missing", "Username and password are required."); return
        if len(p) < 6:
            messagebox.showwarning("Weak", "Password must be at least 6 characters."); return
        if self.app.db.add_user(u, p, r):
            self.refresh(); self._clear()
            messagebox.showinfo("✅ Added", f"User '{u}' created.")
        else:
            messagebox.showerror("Error", f"Username '{u}' already exists.")

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("No selection", "Select a user first."); return
        if self._sel_id == self.app.current_user[0]:
            messagebox.showerror("Error", "You cannot delete your own account."); return
        if messagebox.askyesno("Confirm", "Delete this user?"):
            self.app.db.delete_user(self._sel_id)
            self.refresh(); self._clear()

    def _clear(self):
        self._sel_id = None
        self.e_user.delete(0, "end"); self.e_pass.delete(0, "end")
        self.role_var.set("Receptionist")
        self.tree.selection_remove(*self.tree.selection())

    def retheme(self):
        for w in self.winfo_children(): w.destroy()
        self.configure(bg=t("BG"))
        self._sel_id = None
        self._build()
