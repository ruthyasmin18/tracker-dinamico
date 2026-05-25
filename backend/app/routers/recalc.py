"""Router del Motor de Recálculo Dinámico (F4 / H4) — CORE del producto.

Endpoints:
- POST /api/recalc/event         — trigger manual (el usuario reporta el imprevisto).
- POST /api/recalc/auto          — trigger automático desde el diario (F4 ↔ F3).
- GET  /api/recalc/users/{id}/logs — historial de ajustes del usuario.
"""
from datetime import date as _date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FoodEntry, NutritionGoal, RecalcLog, User
from app.routers.auth import get_current_user_id
from app.schemas import (
    AutoRecalcRequest,
    AutoRecalcResponse,
    DayPlan,
    MacroPlan,
    RecalcEventIn,
    RecalcLogOut,
    RecalcResponse,
)
from app.services.recalc_engine import (
    AUTO_RECALC_THRESHOLD,
    compute_diary_deviation,
    run_recalc,
)


router = APIRouter(prefix="/api/recalc", tags=["recalc"])


def _persist_log(db: Session, user_id: str, payload_event_type: str,
                 payload_description: str, payload_kcal_delta: float,
                 payload_target_date: _date, goal: NutritionGoal, result) -> RecalcLog:
    log = RecalcLog(
        user_id=user_id,
        event_type=payload_event_type,
        event_description=payload_description,
        kcal_delta=payload_kcal_delta,
        target_date=payload_target_date,
        original_plan={"kcal": goal.kcal, "protein_g": goal.protein_g,
                       "carbs_g": goal.carbs_g, "fat_g": goal.fat_g},
        adjusted_plan={"days": [
            {"date": d.target_date.isoformat(), "adjusted": d.adjusted.to_dict()}
            for d in result.days
        ]},
        propagated_days=result.propagated_days,
        message=result.message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def _to_day_plans(result) -> list[DayPlan]:
    return [
        DayPlan(
            date=d.target_date,
            original=MacroPlan(**d.original.to_dict()),
            adjusted=MacroPlan(**d.adjusted.to_dict()),
            note=d.note,
        )
        for d in result.days
    ]


# ---------- Trigger manual ----------

@router.post("/event", response_model=RecalcResponse, status_code=status.HTTP_200_OK)
def report_event(
    payload: RecalcEventIn,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Reporta un imprevisto manualmente y devuelve el plan recalibrado."""
    if current_user_id != payload.user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    goal = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == payload.user_id)
        .order_by(NutritionGoal.created_at.desc())
        .first()
    )
    if not goal:
        raise HTTPException(status_code=400, detail="El usuario aún no tiene objetivo nutricional")

    result = run_recalc(
        daily_goal=goal,
        event_type=payload.event_type,
        kcal_delta=payload.kcal_delta,
        target_date=payload.target_date,
    )
    log = _persist_log(db, payload.user_id, payload.event_type, payload.event_description,
                       payload.kcal_delta, payload.target_date, goal, result)

    return RecalcResponse(message=result.message, log_id=log.id, days=_to_day_plans(result))


# ---------- Trigger automático desde diario ----------

@router.post("/auto", response_model=AutoRecalcResponse)
def auto_recalc(
    payload: AutoRecalcRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Detecta automáticamente la desviación calórica del diario de hoy y recalibra.

    Implementa la fórmula del informe:
        delta_kcal = consumido_actual − kcal_objetivo_acumuladas_a_esta_hora

    Retorna adjusted=False si el plan está en ruta (desviación < 15%).
    """
    if current_user_id != payload.user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    goal = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == payload.user_id)
        .order_by(NutritionGoal.created_at.desc())
        .first()
    )
    if not goal:
        raise HTTPException(status_code=400, detail="Sin objetivo nutricional calculado")

    entries = (
        db.query(FoodEntry)
        .filter(FoodEntry.user_id == payload.user_id,
                FoodEntry.consumed_on == payload.target_date)
        .all()
    )

    if not entries:
        return AutoRecalcResponse(adjusted=False, message="Aún no hay registros para hoy — añade comidas al diario.")

    deviation = compute_diary_deviation(entries, goal)
    severity = abs(deviation) / goal.kcal if goal.kcal > 0 else 0

    if severity < AUTO_RECALC_THRESHOLD:
        return AutoRecalcResponse(adjusted=False, message="Tu plan está en ruta 👍 — sigue así.")

    event_type = "extra_calories" if deviation > 0 else "skipped_meal"
    result = run_recalc(
        daily_goal=goal,
        event_type=event_type,
        kcal_delta=deviation,
        target_date=payload.target_date,
    )
    # Persiste en el log de auditoría
    log = _persist_log(
        db, payload.user_id, event_type,
        f"Auto-detección: {'exceso' if deviation > 0 else 'déficit'} de {abs(deviation):.0f} kcal",
        deviation, payload.target_date, goal, result,
    )

    return AutoRecalcResponse(
        adjusted=True,
        message=result.message,
        days=_to_day_plans(result),
        log_id=log.id,
    )


# ---------- Historial ----------

@router.get("/users/{user_id}/logs", response_model=list[RecalcLogOut])
def list_logs(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return (
        db.query(RecalcLog)
        .filter(RecalcLog.user_id == user_id)
        .order_by(RecalcLog.created_at.desc())
        .limit(limit)
        .all()
    )
