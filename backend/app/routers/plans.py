"""Router de planes generados: meal plan + workout plan."""
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import NutritionGoal, User
from app.schemas import MealPlanOut, WorkoutPlanOut
from app.services.meal_planner import build_weekly_plan
from app.services.workout_planner import build_weekly_workout


router = APIRouter(prefix="/api/users", tags=["plans"])


@router.get("/{user_id}/meal-plan", response_model=MealPlanOut)
def get_meal_plan(user_id: str, db: Session = Depends(get_db)):
    """Genera el plan semanal de comidas basado en el objetivo nutricional."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    goal = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == user_id)
        .order_by(NutritionGoal.created_at.desc())
        .first()
    )
    if not goal:
        raise HTTPException(status_code=400, detail="Sin objetivo nutricional calculado")

    # Seed estable por usuario para que el plan no cambie entre cargas
    seed = abs(hash(user.id)) % (10**8)
    days = build_weekly_plan(
        daily_kcal=goal.kcal,
        daily_protein=goal.protein_g,
        daily_carbs=goal.carbs_g,
        daily_fat=goal.fat_g,
        seed=seed,
    )

    return MealPlanOut(
        target_kcal=goal.kcal,
        target_protein_g=goal.protein_g,
        target_carbs_g=goal.carbs_g,
        target_fat_g=goal.fat_g,
        days=[asdict(d) for d in days],
    )


@router.get("/{user_id}/workout-plan", response_model=WorkoutPlanOut)
def get_workout_plan(user_id: str, db: Session = Depends(get_db)):
    """Genera la rutina semanal según nivel de actividad y objetivo."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    days = build_weekly_workout(user.activity_level, user.goal)
    return WorkoutPlanOut(
        activity_level=user.activity_level,
        goal=user.goal,
        days=[asdict(d) for d in days],
    )
