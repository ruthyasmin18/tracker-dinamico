"""Modelos SQLAlchemy del dominio."""
from datetime import date, datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import String, Integer, Float, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Gender(str, Enum):
    male = "male"
    female = "female"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"        # 1.2
    light = "light"                # 1.375
    moderate = "moderate"          # 1.55
    active = "active"              # 1.725
    very_active = "very_active"    # 1.9


class Goal(str, Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


class Meal(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)
    activity_level: Mapped[str] = mapped_column(String, nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False, default=Goal.maintain.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    nutrition_goals: Mapped[list["NutritionGoal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    food_entries: Mapped[list["FoodEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    recalc_logs: Mapped[list["RecalcLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    bmr: Mapped[float] = mapped_column(Float, nullable=False)
    tdee: Mapped[float] = mapped_column(Float, nullable=False)
    formula: Mapped[str] = mapped_column(String, default="mifflin-st-jeor")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    user: Mapped[User] = relationship(back_populates="nutrition_goals")


class FoodEntry(Base):
    __tablename__ = "food_entries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    food_name: Mapped[str] = mapped_column(String, nullable=False)
    off_id: Mapped[str | None] = mapped_column(String, nullable=True)
    grams: Mapped[float] = mapped_column(Float, nullable=False)
    kcal_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    protein_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    meal: Mapped[str] = mapped_column(String, nullable=False)
    consumed_on: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    user: Mapped[User] = relationship(back_populates="food_entries")

    @property
    def kcal(self) -> float:
        return self.kcal_per_100g * self.grams / 100

    @property
    def protein_g(self) -> float:
        return self.protein_per_100g * self.grams / 100

    @property
    def carbs_g(self) -> float:
        return self.carbs_per_100g * self.grams / 100

    @property
    def fat_g(self) -> float:
        return self.fat_per_100g * self.grams / 100


class RecalcLog(Base):
    """Auditoría de eventos de recálculo dinámico (F4)."""
    __tablename__ = "recalc_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_description: Mapped[str] = mapped_column(String, nullable=False)
    kcal_delta: Mapped[float] = mapped_column(Float, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    original_plan: Mapped[dict] = mapped_column(JSON, nullable=False)
    adjusted_plan: Mapped[dict] = mapped_column(JSON, nullable=False)
    propagated_days: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    user: Mapped[User] = relationship(back_populates="recalc_logs")
