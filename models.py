"""models.py — OOP classes: Person (abstract), Member, Trainer, Membership."""

from abc import ABC, abstractmethod
import re
from datetime import datetime, date


def _validate_phone(phone: str):
    """Allow digits, spaces, +, -, (). Min 7 digits."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        raise ValueError("Phone number must contain at least 7 digits.")


def _validate_date(d: str):
    try:
        datetime.strptime(d, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Date '{d}' must be in YYYY-MM-DD format.")


# ── Abstract Base ──────────────────────────────────────────────
class Person(ABC):
    """Abstraction + Encapsulation base."""

    def __init__(self, name: str, age, phone: str):
        self.name  = name
        self.age   = age
        self.phone = phone

    @property
    def name(self): return self.__name
    @name.setter
    def name(self, v):
        if not str(v).strip(): raise ValueError("Name cannot be empty.")
        self.__name = str(v).strip()

    @property
    def age(self): return self.__age
    @age.setter
    def age(self, v):
        try:
            v = int(v)
        except (ValueError, TypeError):
            raise ValueError("Age must be a number.")
        if not (5 <= v <= 120): raise ValueError("Age must be between 5 and 120.")
        self.__age = v

    @property
    def phone(self): return self.__phone
    @phone.setter
    def phone(self, v):
        _validate_phone(str(v))
        self.__phone = str(v).strip()

    @abstractmethod
    def get_info(self) -> dict: pass

    @abstractmethod
    def role(self) -> str: pass


# ── Membership (Encapsulation) ─────────────────────────────────
class Membership:
    FEES = {"Basic": 30, "Standard": 60, "Premium": 100}
    DURATION_MONTHS = {"Basic": 1, "Standard": 3, "Premium": 12}

    def __init__(self, plan: str, start_date: str):
        _validate_date(start_date)
        self.__plan       = plan
        self.__start_date = start_date

    @property
    def plan(self): return self.__plan

    @property
    def fee(self): return self.FEES.get(self.__plan, 0)

    @property
    def start_date(self): return self.__start_date

    @property
    def expiry_date(self) -> str:
        from dateutil.relativedelta import relativedelta
        months = self.DURATION_MONTHS.get(self.__plan, 1)
        start  = datetime.strptime(self.__start_date, "%Y-%m-%d").date()
        expiry = start + relativedelta(months=months)
        return expiry.strftime("%Y-%m-%d")

    @property
    def is_expired(self) -> bool:
        return date.today() > datetime.strptime(self.expiry_date, "%Y-%m-%d").date()

    @property
    def days_until_expiry(self) -> int:
        exp = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        return (exp - date.today()).days


# ── Member (Inheritance) ───────────────────────────────────────
class Member(Person):
    PLANS = list(Membership.FEES.keys())

    def __init__(self, name, age, phone, plan, start_date):
        super().__init__(name, age, phone)
        self.__membership = Membership(plan, start_date)

    @property
    def membership(self): return self.__membership

    def role(self) -> str: return "Member"

    def get_info(self) -> dict:          # Polymorphism
        return {
            "Name":        self.name,
            "Age":         self.age,
            "Phone":       self.phone,
            "Role":        self.role(),
            "Plan":        self.__membership.plan,
            "Fee":         f"${self.__membership.fee}",
            "Start":       self.__membership.start_date,
            "Expiry":      self.__membership.expiry_date,
            "Status":      "Expired" if self.__membership.is_expired else "Active",
        }


# ── Trainer (Inheritance) ──────────────────────────────────────
class Trainer(Person):
    SPECIALIZATIONS = ["Cardio", "Weightlifting", "Yoga", "CrossFit", "Boxing"]

    def __init__(self, name, age, phone, specialization, salary):
        super().__init__(name, age, phone)
        try:
            salary = float(salary)
        except (ValueError, TypeError):
            raise ValueError("Salary must be a number.")
        if salary < 0: raise ValueError("Salary cannot be negative.")
        self.__specialization = specialization
        self.__salary         = salary

    @property
    def specialization(self): return self.__specialization

    @property
    def salary(self): return self.__salary

    def role(self) -> str: return "Trainer"

    def get_info(self) -> dict:          # Polymorphism
        return {
            "Name":           self.name,
            "Age":            self.age,
            "Phone":          self.phone,
            "Role":           self.role(),
            "Specialization": self.__specialization,
            "Salary":         f"${self.__salary:,.2f}",
        }
