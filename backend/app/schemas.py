"""Schemas Pydantic para validación e (de)serialización."""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models import ActivityLevel, Gender, Goal, Meal


# ----- User -----
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=14, le=100)
    weight_kg: float = Field(ge=30, le=300)
    height_cm: float = Field(ge=100, le=250)
    gender: Gender
    activity_level: ActivityLevel
    goal: Goal = Goal.maintain


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    age: int
    weight_kg: float
    height_cm: float
    gender: str
    activity_level: str
    goal: str
    created_at: datetime


# ----- NutritionGoal -----
class NutritionGoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    bmr: float
    tdee: float
    formula: str
    created_at: datetime


# ----- FoodEntry -----
class FoodSearchResult(BaseModel):
    off_id: str | None
    name: str
    brand: str | None = None
    kcal_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float


class FoodEntryCreate(BaseModel):
    food_name: str
    off_id: str | None = None
    grams: float = Field(gt=0, le=5000)
    kcal_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carbs_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)
    meal: Meal
    consumed_on: date
    source: str = "manual"


class FoodEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    food_name: str
    off_id: str | None
    grams: float
    kcal_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    meal: str
    consumed_on: date
    source: str
    created_at: datetime
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float


class DiarySummary(BaseModel):
    consumed_on: date
    entries: list[FoodEntryOut]
    totals: dict[str, float]
    goal: NutritionGoalOut | None
    remaining: dict[str, float]


# ----- Recalc -----
class RecalcEventIn(BaseModel):
    user_id: str
    event_type: str = Field(description="extra_calories | skipped_meal | reduced_workout_time")
    event_description: str = Field(min_length=1, max_length=200)
    kcal_delta: float = Field(description="Positivo si excedió, negativo si déficit")
    target_date: date


class MacroPlan(BaseModel):
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float


class DayPlan(BaseModel):
    date: date
    original: MacroPlan
    adjusted: MacroPlan
    note: str


class RecalcResponse(BaseModel):
    message: str
    days: list[DayPlan]
    log_id: str


# ----- Planes generados -----
class PlannedFoodOut(BaseModel):
    name: str
    grams: float
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    kcal_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float


class PlannedMealOut(BaseModel):
    meal: str
    foods: list[PlannedFoodOut]
    total_kcal: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


class PlannedDayOut(BaseModel):
    day_label: str
    meals: list[PlannedMealOut]
    total_kcal: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


class MealPlanOut(BaseModel):
    target_kcal: float
    target_protein_g: float
    target_carbs_g: float
    target_fat_g: float
    days: list[PlannedDayOut]


class ExerciseOut(BaseModel):
    name: str
    muscle: str
    sets: int
    reps: str
    rest_seconds: int
    equipment: str


class WorkoutDayOut(BaseModel):
    day_label: str
    focus: str
    duration_min: int
    exercises: list[ExerciseOut]
    rest: bool


class WorkoutPlanOut(BaseModel):
    activity_level: str
    goal: str
    days: list[WorkoutDayOut]


class RecalcLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    event_type: str
    event_description: str
    kcal_delta: float
    target_date: date
    original_plan: dict[str, Any]
    adjusted_plan: dict[str, Any]
    propagated_days: int
    message: str
    created_at: datetime
