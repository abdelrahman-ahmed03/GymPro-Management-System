"""members.py — Members tab (theme-aware)."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import styles
from styles import (ACCENT, ACCENT2, GREEN, FONT_TITLE, FONT_LABEL, FONT_BODY,
                    apply_treeview_style, entry_widget, pill_btn, t, WHITE)
from models import Member
from utils import export_to_csv, days_until


class MembersFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=t("BG"))
        self.app     = app
        self._sel_id = None
        self._build()

    def _build(self):
        apply_treeview_style()

        # Header + search
        hdr = tk.Frame(self, bg=t("BG"))
        hdr.pack(fill="x", padx=36, pady=(24, 0))
        tk.Label(hdr, text="👤  Members", font=FONT_TITLE,
                 bg=t("BG"), fg=t("TEXT_DARK")).pack(side="left")

        right = tk.Frame(hdr, bg=t("BG"))
        right.pack(side="right")
        tk.Label(right, text="🔍", font=("Helvetica", 14), bg=t("BG")).pack(side="left", padx=(0, 4))
        self.sv = tk.StringVar()
        self.sv.trace("w", lambda *_: self.refresh())
        entry_widget(right, textvariable=self.sv, width=22).pack(side="left")

        # Form card
        fc = tk.Frame(self, bg=t("CARD"),
                      highlightthickness=1, highlightbackground=t("BORDER"))
        fc.pack(fill="x", padx=36, pady=14)
        inner = tk.Frame(fc, bg=t("CARD"), padx=16, pady=12)
        inner.pack(fill="x")

        self.e_name  = self._lbl_entry(inner, "Full Name",             0)
        self.e_age   = self._lbl_entry(inner, "Age",                   1)
        self.e_phone = self._lbl_entry(inner, "Phone",                 2)

        tk.Label(inner, text="Plan", font=FONT_LABEL,
                 bg=t("CARD"), fg=t("TEXT_MUTED")).grid(row=0, column=3, sticky="w", padx=(0, 4), pady=(4, 2))
        self.plan_var = tk.StringVar(value="Basic")
        ttk.Combobox(inner, textvariable=self.plan_var,
                     values=Member.PLANS, state="readonly",
                     width=12, font=FONT_BODY).grid(row=1, column=3, padx=(0, 16), pady=(0, 8), sticky="w")

        self.e_date = self._lbl_entry(inner, "Start Date (YYYY-MM-DD)", 4)
        self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Buttons
        br = tk.Frame(self, bg=t("BG"))
        br.pack(anchor="w", padx=36, pady=(0, 8))
        pill_btn(br, "✅  Add",       self._add,    bg=GREEN).pack(side="left", padx=(0, 8))
        pill_btn(br, "✏️  Update",    self._update, bg=ACCENT).pack(side="left", padx=(0, 8))
        pill_btn(br, "🗑️  Delete",    self._delete, bg=ACCENT2).pack(side="left", padx=(0, 8))
        pill_btn(br, "✖  Clear",     self._clear,  bg=t("CARD"), fg=t("TEXT_MUTED")).pack(side="left", padx=(0, 16))
        pill_btn(br, "📤  Export CSV", self._export, bg="#0EA5E9", fg=WHITE).pack(side="left")

        # Legend
        leg = tk.Frame(self, bg=t("BG"))
        leg.pack(anchor="w", padx=36, pady=(0, 4))
        for color_key, label in [("ROW_EXPIRED", "Expired"),
                                  ("ROW_EXPIRING", "Expiring ≤7 days"),
                                  ("ROW_ACTIVE",   "Active")]:
            dot = tk.Frame(leg, bg=t(color_key), width=14, height=14,
                           highlightthickness=1, highlightbackground=t("BORDER"))
            dot.pack(side="left")
            tk.Label(leg, text=label, font=("Helvetica", 9),
                     bg=t("BG"), fg=t("TEXT_MUTED")).pack(side="left", padx=(4, 12))

        # Table
        cols = ("ID", "Name", "Age", "Phone", "Plan", "Start Date", "Expiry Date")
        tf = tk.Frame(self, bg=t("BG"))
        tf.pack(fill="both", expand=True, padx=36, pady=(0, 20))

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", style="L.Treeview")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.column("ID",   width=36)
        self.tree.column("Name", width=140, anchor="w")

        self.tree.tag_configure("expired",  background=t("ROW_EXPIRED"))
        self.tree.tag_configure("expiring", background=t("ROW_EXPIRING"))
        self.tree.tag_configure("active",   background=t("ROW_ACTIVE"))

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        self.refresh()

    def _lbl_entry(self, p, text, col):
        tk.Label(p, text=text, font=FONT_LABEL,
                 bg=t("CARD"), fg=t("TEXT_MUTED")).grid(
            row=0, column=col, sticky="w", padx=(0, 4), pady=(4, 2))
        e = entry_widget(p, width=18)
        e.grid(row=1, column=col, padx=(0, 16), pady=(0, 8), sticky="w")
        return e

    def refresh(self):
        rows = (self.app.db.search_members(self.sv.get())
                if self.sv.get() else self.app.db.get_all_members())
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            expiry = r[6] if len(r) > 6 else ""
            d   = days_until(expiry) if expiry else 1
            tag = "expired" if d < 0 else ("expiring" if d <= 7 else "active")
            self.tree.insert("", "end", values=r, tags=(tag,))

    def _on_sel(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        row = self.tree.item(sel[0])["values"]
        self._sel_id = row[0]
        self._clear_form()
        self.e_name.insert(0, row[1]); self.e_age.insert(0, row[2])
        self.e_phone.insert(0, row[3]); self.plan_var.set(row[4])
        self.e_date.insert(0, row[5])

    def _form_vals(self):
        return (self.e_name.get(), self.e_age.get(), self.e_phone.get(),
                self.plan_var.get(), self.e_date.get())

    def _add(self):
        try:
            n, a, ph, pl, sd = self._form_vals()
            m = Member(n, a, ph, pl, sd)
            self.app.db.add_member(m)
            self.refresh(); self._clear()
            messagebox.showinfo("✅ Added", "Member added successfully!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("No selection", "Select a member first."); return
        try:
            n, a, ph, pl, sd = self._form_vals()
            m = Member(n, a, ph, pl, sd)
            self.app.db.update_member(self._sel_id, n, a, ph, pl, sd, m.membership.expiry_date)
            self.refresh(); self._clear()
            messagebox.showinfo("✅ Updated", "Member updated!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("No selection", "Select a member first."); return
        if messagebox.askyesno("Confirm", "Delete this member?"):
            self.app.db.delete_member(self._sel_id)
            self.refresh(); self._clear()

    def _export(self):
        rows = self.app.db.get_all_members()
        export_to_csv(rows, ("ID","Name","Age","Phone","Plan","Start Date","Expiry Date"), "Members")

    def _clear(self):
        self._sel_id = None
        self.tree.selection_remove(*self.tree.selection())
        self._clear_form()

    def _clear_form(self):
        for e in [self.e_name, self.e_age, self.e_phone, self.e_date]:
            e.delete(0, "end")
        self.plan_var.set("Basic")

    def retheme(self):
        for w in self.winfo_children(): w.destroy()
        self.configure(bg=t("BG"))
        self._sel_id = None
        self._build()
