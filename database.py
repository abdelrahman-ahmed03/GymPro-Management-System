"""database.py — Abstraction layer over SQLite."""

import sqlite3
import hashlib
from models import Member, Trainer


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


class GymDatabase:
    def __init__(self, path="gym.db"):
        self._conn = sqlite3.connect(path)
        self._create_tables()
        self._seed_admin()

    # ── Schema ────────────────────────────────────────────────
    def _create_tables(self):
        c = self._conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role     TEXT NOT NULL DEFAULT 'Receptionist'
            );
            CREATE TABLE IF NOT EXISTS members (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT,
                age        INTEGER,
                phone      TEXT,
                plan       TEXT,
                start_date TEXT,
                expiry_date TEXT
            );
            CREATE TABLE IF NOT EXISTS trainers (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT,
                age            INTEGER,
                phone          TEXT,
                specialization TEXT,
                salary         REAL
            );
        """)
        self._conn.commit()

    def _seed_admin(self):
        """Create default admin if none exists."""
        cur = self._conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            self._conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                ("admin", _hash("admin123"), "Admin")
            )
            self._conn.commit()

    # ── Auth ──────────────────────────────────────────────────
    def login(self, username: str, password: str):
        """Returns (id, username, role) or None."""
        row = self._conn.execute(
            "SELECT id, username, role FROM users WHERE username=? AND password=?",
            (username, _hash(password))
        ).fetchone()
        return row

    def get_all_users(self):
        return self._conn.execute("SELECT id, username, role FROM users").fetchall()

    def add_user(self, username, password, role):
        try:
            self._conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                (username, _hash(password), role)
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False   # duplicate username

    def delete_user(self, id_):
        self._conn.execute("DELETE FROM users WHERE id=?", (id_,))
        self._conn.commit()

    # ── Members ───────────────────────────────────────────────
    def add_member(self, m: Member):
        # Duplicate check
        dup = self._conn.execute(
            "SELECT id FROM members WHERE name=? AND phone=?", (m.name, m.phone)
        ).fetchone()
        if dup:
            raise ValueError(f"A member named '{m.name}' with this phone already exists.")
        self._conn.execute(
            "INSERT INTO members (name,age,phone,plan,start_date,expiry_date) VALUES (?,?,?,?,?,?)",
            (m.name, m.age, m.phone, m.membership.plan,
             m.membership.start_date, m.membership.expiry_date)
        )
        self._conn.commit()

    def get_all_members(self):
        return self._conn.execute("SELECT * FROM members").fetchall()

    def search_members(self, keyword):
        k = f"%{keyword}%"
        return self._conn.execute(
            "SELECT * FROM members WHERE name LIKE ? OR phone LIKE ? OR plan LIKE ?",
            (k, k, k)
        ).fetchall()

    def update_member(self, id_, name, age, phone, plan, start_date, expiry_date):
        self._conn.execute(
            "UPDATE members SET name=?,age=?,phone=?,plan=?,start_date=?,expiry_date=? WHERE id=?",
            (name, age, phone, plan, start_date, expiry_date, id_)
        )
        self._conn.commit()

    def delete_member(self, id_):
        self._conn.execute("DELETE FROM members WHERE id=?", (id_,))
        self._conn.commit()

    # ── Trainers ──────────────────────────────────────────────
    def add_trainer(self, t: Trainer):
        dup = self._conn.execute(
            "SELECT id FROM trainers WHERE name=? AND phone=?", (t.name, t.phone)
        ).fetchone()
        if dup:
            raise ValueError(f"A trainer named '{t.name}' with this phone already exists.")
        self._conn.execute(
            "INSERT INTO trainers (name,age,phone,specialization,salary) VALUES (?,?,?,?,?)",
            (t.name, t.age, t.phone, t.specialization, t.salary)
        )
        self._conn.commit()

    def get_all_trainers(self):
        return self._conn.execute("SELECT * FROM trainers").fetchall()

    def search_trainers(self, keyword):
        k = f"%{keyword}%"
        return self._conn.execute(
            "SELECT * FROM trainers WHERE name LIKE ? OR phone LIKE ? OR specialization LIKE ?",
            (k, k, k)
        ).fetchall()

    def update_trainer(self, id_, name, age, phone, spec, salary):
        self._conn.execute(
            "UPDATE trainers SET name=?,age=?,phone=?,specialization=?,salary=? WHERE id=?",
            (name, age, phone, spec, salary, id_)
        )
        self._conn.commit()

    def delete_trainer(self, id_):
        self._conn.execute("DELETE FROM trainers WHERE id=?", (id_,))
        self._conn.commit()

    # ── Analytics ─────────────────────────────────────────────
    def get_stats(self) -> dict:
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")

        total_members  = self._conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        active_members = self._conn.execute(
            "SELECT COUNT(*) FROM members WHERE expiry_date >= ?", (today,)
        ).fetchone()[0]
        expired        = total_members - active_members
        total_trainers = self._conn.execute("SELECT COUNT(*) FROM trainers").fetchone()[0]

        # Monthly revenue = sum of plan fees for active members
        rows = self._conn.execute(
            "SELECT plan FROM members WHERE expiry_date >= ?", (today,)
        ).fetchall()
        from models import Membership
        revenue = sum(Membership.FEES.get(r[0], 0) for r in rows)

        # Highest-paid trainer
        top = self._conn.execute(
            "SELECT name, salary FROM trainers ORDER BY salary DESC LIMIT 1"
        ).fetchone()

        # Expiring soon (within 7 days)
        expiring = self._conn.execute(
            "SELECT COUNT(*) FROM members WHERE expiry_date >= ? AND expiry_date <= date(?, '+7 days')",
            (today, today)
        ).fetchone()[0]

        return {
            "total_members":  total_members,
            "active_members": active_members,
            "expired":        expired,
            "total_trainers": total_trainers,
            "revenue":        revenue,
            "top_trainer":    top,
            "expiring_soon":  expiring,
        }

    def close(self):
        self._conn.close()
