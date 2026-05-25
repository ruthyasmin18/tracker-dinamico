"""Router de Dashboard de Progreso y Analítica (F6).

GET /api/users/{user_id}/dashboard/weekly → estadísticas de los últimos 7 días.
"""
from datetime import date as _date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FoodEntry, NutritionGoal, User
from app.routers.auth import get_current_user_id
from app.schemas import DailyStats, WeeklyDashboard

router = APIRouter(prefix="/api/users", tags=["dashboard"])


@router.get("/{user_id}/dashboard/weekly", response_model=WeeklyDashboard)
def weekly_dashboard(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Dashboard semanal: adherencia, kcal promedio, racha y distribución de macros.

    Calcula métricas de los últimos 7 días (incluyendo hoy) y las devuelve
    listas para graficar en el frontend.
    """
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    goal = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == user_id)
        .order_by(NutritionGoal.created_at.desc())
        .first()
    )
    kcal_objetivo = goal.kcal if goal else 0.0

    today = _date.today()
    period_start = today - timedelta(days=6)  # últimos 7 días

    # Todas las entradas del período
    entries = (
        db.query(FoodEntry)
        .filter(
            FoodEntry.user_id == user_id,
            FoodEntry.consumed_on >= period_start,
            FoodEntry.consumed_on <= today,
        )
        .all()
    )

    # Agrupar por fecha
    from collections import defaultdict
    by_date: dict[_date, list[FoodEntry]] = defaultdict(list)
    for e in entries:
        by_date[e.consumed_on].append(e)

    # Construir daily_stats para los 7 días
    daily_stats: list[DailyStats] = []
    for i in range(7):
        day = period_start + timedelta(days=i)
        day_entries = by_date.get(day, [])
        kcal = sum(e.kcal for e in day_entries)
        prot = sum(e.protein_g for e in day_entries)
        carbs = sum(e.carbs_g for e in day_entries)
        fat = sum(e.fat_g for e in day_entries)
        adh = round(min(kcal / kcal_objetivo * 100, 100), 1) if kcal_objetivo > 0 else 0.0
        daily_stats.append(DailyStats(
            date=day,
            kcal_consumed=round(kcal, 1),
            kcal_goal=round(kcal_objetivo, 1),
            protein_g=round(prot, 1),
            carbs_g=round(carbs, 1),
            fat_g=round(fat, 1),
            adherence_pct=adh,
        ))

    # Métricas agregadas
    dias_con_datos = sum(1 for d in daily_stats if d.kcal_consumed > 0)
    active_days = [d for d in daily_stats if d.kcal_consumed > 0]

    adherence_pct = round(
        sum(d.adherence_pct for d in daily_stats) / 7, 1
    )
    kcal_promedio = round(
        sum(d.kcal_consumed for d in active_days) / max(dias_con_datos, 1), 1
    )
    macro_avg = {
        "protein_g": round(sum(d.protein_g for d in active_days) / max(dias_con_datos, 1), 1),
        "carbs_g":   round(sum(d.carbs_g   for d in active_days) / max(dias_con_datos, 1), 1),
        "fat_g":     round(sum(d.fat_g     for d in active_days) / max(dias_con_datos, 1), 1),
    }

    # Racha: días consecutivos desde hoy hacia atrás con al menos 1 entrada
    racha = 0
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        if by_date.get(day):
            racha += 1
        else:
            if i < 6:  # solo rompe racha si no es el primer día al contar
                break

    # Racha real: contar desde HOY hacia atrás
    racha = 0
    check = today
    while True:
        if by_date.get(check):
            racha += 1
            check -= timedelta(days=1)
            if check < period_start:
                break
        else:
            break

    return WeeklyDashboard(
        user_id=user_id,
        period_start=period_start,
        period_end=today,
        adherence_pct=adherence_pct,
        kcal_promedio=kcal_promedio,
        kcal_objetivo=round(kcal_objetivo, 1),
        racha_actual=racha,
        dias_con_datos=dias_con_datos,
        macro_avg=macro_avg,
        daily_stats=daily_stats,
    )
