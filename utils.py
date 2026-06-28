"""utils.py — Utility helpers (CSV export, date helpers)."""

import csv
import os
from tkinter import filedialog, messagebox
from datetime import date, datetime


def export_to_csv(rows, columns, title="Export"):
    """Open save dialog and write rows to a CSV file."""
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title=f"Save {title} as CSV",
        initialfile=f"{title.lower().replace(' ', '_')}.csv"
    )
    if not path:
        return
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        messagebox.showinfo("✅ Exported", f"Saved to:\n{path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))


def days_until(date_str: str) -> int:
    try:
        exp = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (exp - date.today()).days
    except Exception:
        return 0


def status_tag(expiry_str: str):
    """Return ('Active'|'Expiring'|'Expired', color)."""
    d = days_until(expiry_str)
    if d < 0:
        return "Expired",  "#EF4444"
    elif d <= 7:
        return "Expiring", "#F59E0B"
    else:
        return "Active",   "#10B981"
