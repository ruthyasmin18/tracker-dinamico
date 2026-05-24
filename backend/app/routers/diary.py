"""Router de diario de alimentos (F3): búsqueda y CRUD de FoodEntry."""
from collections import defaultdict
from datetime import date as _date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FoodEntry, NutritionGoal, User
from app.schemas import (
    DiarySummary,
    FoodEntryCreate,
    FoodEntryOut,
    FoodSearchResult,
)
from app.services import openfoodfacts


router = APIRouter(prefix="/api", tags=["diary"])


# ---------- Búsqueda en OpenFoodFacts ----------
@router.get("/foods/search", response_model=list[FoodSearchResult])
async def search_foods(q: str = Query(min_length=2), limit: int = Query(15, ge=1, le=50)):
    try:
        return await openfoodfacts.search_foods(q, limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar OpenFoodFacts: {e}")


@router.get("/foods/barcode/{barcode}", response_model=FoodSearchResult)
async def get_by_barcode(barcode: str):
    try:
        result = await openfoodfacts.get_food_by_barcode(barcode)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar OpenFoodFacts: {e}")
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


# ---------- CRUD diario ----------
def _entry_to_out(entry: FoodEntry) -> FoodEntryOut:
    return FoodEntryOut(
        id=entry.id,
        user_id=entry.user_id,
        food_name=entry.food_name,
        off_id=entry.off_id,
        grams=entry.grams,
        kcal_per_100g=entry.kcal_per_100g,
        protein_per_100g=entry.protein_per_100g,
        carbs_per_100g=entry.carbs_per_100g,
        fat_per_100g=entry.fat_per_100g,
        meal=entry.meal,
        consumed_on=entry.consumed_on,
        source=entry.source,
        created_at=entry.created_at,
        kcal=round(entry.kcal, 1),
        protein_g=round(entry.protein_g, 1),
        carbs_g=round(entry.carbs_g, 1),
        fat_g=round(entry.fat_g, 1),
    )


@router.post("/users/{user_id}/diary", response_model=FoodEntryOut, status_code=status.HTTP_201_CREATED)
def create_entry(user_id: str, payload: FoodEntryCreate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    entry = FoodEntry(
        user_id=user_id,
        food_name=payload.food_name,
        off_id=payload.off_id,
        grams=payload.grams,
        kcal_per_100g=payload.kcal_per_100g,
        protein_per_100g=payload.protein_per_100g,
        carbs_per_100g=payload.carbs_per_100g,
        fat_per_100g=payload.fat_per_100g,
        meal=payload.meal.value,
        consumed_on=payload.consumed_on,
        source=payload.source,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _entry_to_out(entry)


@router.delete("/users/{user_id}/diary/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(user_id: str, entry_id: str, db: Session = Depends(get_db)):
    entry = db.get(FoodEntry, entry_id)
    if not entry or entry.user_id != user_id:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    db.delete(entry)
    db.commit()


@router.get("/users/{user_id}/diary", response_model=DiarySummary)
def get_diary(user_id: str, on: _date | None = None, db: Session = Depends(get_db)):
    """Diario del día con totales y porcentaje vs objetivo."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    target = on or _date.today()
    entries = (
        db.query(FoodEntry)
        .filter(FoodEntry.user_id == user_id, FoodEntry.consumed_on == target)
        .order_by(FoodEntry.created_at.asc())
        .all()
    )

    totals = defaultdict(float)
    for e in entries:
        totals["kcal"] += e.kcal
        totals["protein_g"] += e.protein_g
        totals["carbs_g"] += e.carbs_g
        totals["fat_g"] += e.fat_g

    totals = {k: round(v, 1) for k, v in totals.items()} or {
        "kcal": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
    }

    goal = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == user_id)
        .order_by(NutritionGoal.created_at.desc())
        .first()
    )

    remaining = {"kcal": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    if goal:
        remaining = {
            "kcal": round(goal.kcal - totals.get("kcal", 0), 1),
            "protein_g": round(goal.protein_g - totals.get("protein_g", 0), 1),
            "carbs_g": round(goal.carbs_g - totals.get("carbs_g", 0), 1),
            "fat_g": round(goal.fat_g - totals.get("fat_g", 0), 1),
        }

    return DiarySummary(
        consumed_on=target,
        entries=[_entry_to_out(e) for e in entries],
        totals=totals,
        goal=goal,
        remaining=remaining,
    )
