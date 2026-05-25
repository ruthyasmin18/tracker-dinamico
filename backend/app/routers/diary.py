"""Router de diario de alimentos (F3) — búsqueda híbrida, CRUD y auto-recálculo (F4).

Búsqueda híbrida (F3):
  1. Biblioteca local curada (food_library.py) — respuesta instantánea, sin red,
     alimentos peruanos/latinoamericanos con macros verificados.
  2. OpenFoodFacts filtrado por países hispanohablantes — para productos de marca.
  Los resultados locales aparecen primero; OFF complementa hasta completar el límite.

La integración F3 ↔ F4 ocurre en GET /diary: si la fecha es hoy y
la desviación calórica supera el 15% del objetivo, el motor de
recálculo se dispara automáticamente y devuelve `recalc_suggestion`
dentro de la respuesta del diario, sin que el usuario lo solicite.
"""
from collections import defaultdict
from datetime import date as _date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FoodEntry, NutritionGoal, User
from app.routers.auth import get_current_user_id
from app.schemas import (
    AutoRecalcResponse,
    DayPlan,
    DiarySummary,
    FoodEntryCreate,
    FoodEntryOut,
    FoodSearchResult,
    MacroPlan,
)
from app.services import openfoodfacts
from app.services.food_library import search_local
from app.services.recalc_engine import (
    AUTO_RECALC_THRESHOLD,
    compute_diary_deviation,
    run_recalc,
)


router = APIRouter(prefix="/api", tags=["diary"])


# ---------- Búsqueda híbrida: biblioteca local + OpenFoodFacts ----------

def _library_to_search_result(food) -> FoodSearchResult:
    """Convierte un LibraryFood al schema FoodSearchResult."""
    return FoodSearchResult(
        off_id=None,          # sin barcode — alimento de la biblioteca local
        name=food.name,
        brand="Biblioteca local",
        kcal_per_100g=food.kcal,
        protein_per_100g=food.protein_g,
        carbs_per_100g=food.carbs_g,
        fat_per_100g=food.fat_g,
    )


@router.get("/foods/search", response_model=list[FoodSearchResult])
async def search_foods(q: str = Query(min_length=2), limit: int = Query(15, ge=1, le=50)):
    """Búsqueda híbrida: local primero, OpenFoodFacts como complemento.

    - Los primeros resultados siempre son de la biblioteca curada peruana/latinoamericana.
    - Si no se alcanzan `limit` resultados locales, se llama a OpenFoodFacts filtrado
      por países hispanohablantes para completar la lista.
    - En caso de fallo de red, se devuelven solo los resultados locales.
    """
    # 1 — Biblioteca local (instantáneo, sin red)
    local = search_local(q, limit)
    results: list[FoodSearchResult] = [_library_to_search_result(f) for f in local]

    # 2 — OpenFoodFacts como complemento si no hay suficientes locales
    remaining = limit - len(results)
    if remaining > 0:
        try:
            off_results = await openfoodfacts.search_foods(q, remaining)
            # Deduplicar por nombre normalizado respecto a los ya obtenidos
            local_names = {r.name.lower() for r in results}
            for r in off_results:
                if r.name.lower() not in local_names:
                    results.append(r)
                    local_names.add(r.name.lower())
                if len(results) >= limit:
                    break
        except Exception:
            # Si OFF falla (sin internet, timeout), los resultados locales son suficientes
            pass

    return results[:limit]


@router.get("/foods/barcode/{barcode}", response_model=FoodSearchResult)
async def get_by_barcode(barcode: str):
    try:
        result = await openfoodfacts.get_food_by_barcode(barcode)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar OpenFoodFacts: {e}")
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


# ---------- Helpers ----------

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


def _build_recalc_suggestion(entries: list[FoodEntry], goal: NutritionGoal, target: _date) -> AutoRecalcResponse | None:
    """F4 ↔ F3: calcula desviación y dispara el motor si supera el umbral."""
    if target != _date.today() or not entries:
        return None

    deviation = compute_diary_deviation(entries, goal)
    if abs(deviation) / goal.kcal < AUTO_RECALC_THRESHOLD:
        return None

    event_type = "extra_calories" if deviation > 0 else "skipped_meal"
    result = run_recalc(
        daily_goal=goal,
        event_type=event_type,
        kcal_delta=deviation,
        target_date=target,
    )

    return AutoRecalcResponse(
        adjusted=True,
        message=result.message,
        days=[
            DayPlan(
                date=d.target_date,
                original=MacroPlan(**d.original.to_dict()),
                adjusted=MacroPlan(**d.adjusted.to_dict()),
                note=d.note,
            )
            for d in result.days
        ],
    )


# ---------- CRUD diario ----------

@router.post(
    "/users/{user_id}/diary",
    response_model=FoodEntryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_entry(
    user_id: str,
    payload: FoodEntryCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

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
def delete_entry(
    user_id: str,
    entry_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    entry = db.get(FoodEntry, entry_id)
    if not entry or entry.user_id != user_id:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    db.delete(entry)
    db.commit()


@router.get("/users/{user_id}/diary", response_model=DiarySummary)
def get_diary(
    user_id: str,
    on: _date | None = None,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Diario del día con totales, porcentaje vs objetivo y sugerencia de recálculo (F4)."""
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

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

    totals: dict[str, float] = {"kcal": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for e in entries:
        totals["kcal"] += e.kcal
        totals["protein_g"] += e.protein_g
        totals["carbs_g"] += e.carbs_g
        totals["fat_g"] += e.fat_g
    totals = {k: round(v, 1) for k, v in totals.items()}

    goal = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == user_id)
        .order_by(NutritionGoal.created_at.desc())
        .first()
    )

    remaining = {"kcal": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    if goal:
        remaining = {
            "kcal": round(goal.kcal - totals["kcal"], 1),
            "protein_g": round(goal.protein_g - totals["protein_g"], 1),
            "carbs_g": round(goal.carbs_g - totals["carbs_g"], 1),
            "fat_g": round(goal.fat_g - totals["fat_g"], 1),
        }

    # F4 ↔ F3: dispara auto-recálculo si hay desviación significativa
    recalc_suggestion = _build_recalc_suggestion(entries, goal, target) if goal else None

    return DiarySummary(
        consumed_on=target,
        entries=[_entry_to_out(e) for e in entries],
        totals=totals,
        goal=goal,
        remaining=remaining,
        recalc_suggestion=recalc_suggestion,
    )
