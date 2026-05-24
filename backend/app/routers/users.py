"""Router de usuarios y objetivos nutricionales (F2)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import NutritionGoal, User
from app.schemas import NutritionGoalOut, UserCreate, UserOut
from app.services.nutrition import calculate_nutrition_goal


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Crea un usuario y calcula automáticamente su objetivo nutricional inicial."""
    user = User(
        name=payload.name,
        age=payload.age,
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        gender=payload.gender.value,
        activity_level=payload.activity_level.value,
        goal=payload.goal.value,
    )
    db.add(user)
    db.flush()

    # Crea objetivo nutricional inicial automáticamente
    result = calculate_nutrition_goal(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        activity_level=user.activity_level,
        goal=user.goal,
    )
    goal = NutritionGoal(
        user_id=user.id,
        kcal=result.kcal,
        protein_g=result.protein_g,
        carbs_g=result.carbs_g,
        fat_g=result.fat_g,
        bmr=result.bmr,
        tdee=result.tdee,
        formula=result.formula,
    )
    db.add(goal)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/{user_id}/goal", response_model=NutritionGoalOut)
def get_current_goal(user_id: str, db: Session = Depends(get_db)):
    """Devuelve el objetivo nutricional más reciente del usuario."""
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
        raise HTTPException(status_code=404, detail="Sin objetivo calculado todavía")
    return goal


@router.post("/{user_id}/goal/recalculate", response_model=NutritionGoalOut)
def recalculate_goal(user_id: str, db: Session = Depends(get_db)):
    """Recalcula el objetivo nutricional usando los datos actuales del perfil."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    result = calculate_nutrition_goal(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        activity_level=user.activity_level,
        goal=user.goal,
    )
    goal = NutritionGoal(
        user_id=user.id,
        kcal=result.kcal,
        protein_g=result.protein_g,
        carbs_g=result.carbs_g,
        fat_g=result.fat_g,
        bmr=result.bmr,
        tdee=result.tdee,
        formula=result.formula,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal
