"""Router del Motor de Recálculo Dinámico (F4 / H4) — CORE."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import NutritionGoal, RecalcLog, User
from app.schemas import (
    DayPlan,
    MacroPlan,
    RecalcEventIn,
    RecalcLogOut,
    RecalcResponse,
)
from app.services.recalc_engine import run_recalc


router = APIRouter(prefix="/api/recalc", tags=["recalc"])


@router.post("/event", response_model=RecalcResponse, status_code=status.HTTP_200_OK)
def report_event(payload: RecalcEventIn, db: Session = Depends(get_db)):
    """Reporta un imprevisto y devuelve el plan recalibrado.

    Este es el endpoint estrella del producto (CORE diferencial).
    """
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
        raise HTTPException(
            status_code=400,
            detail="El usuario aún no tiene objetivo nutricional calculado",
        )

    result = run_recalc(
        daily_goal=goal,
        event_type=payload.event_type,
        kcal_delta=payload.kcal_delta,
        target_date=payload.target_date,
    )

    # Persiste auditoría (recalc_log)
    log = RecalcLog(
        user_id=payload.user_id,
        event_type=payload.event_type,
        event_description=payload.event_description,
        kcal_delta=payload.kcal_delta,
        target_date=payload.target_date,
        original_plan={
            "kcal": goal.kcal,
            "protein_g": goal.protein_g,
            "carbs_g": goal.carbs_g,
            "fat_g": goal.fat_g,
        },
        adjusted_plan={
            "days": [
                {
                    "date": d.target_date.isoformat(),
                    "adjusted": d.adjusted.to_dict(),
                }
                for d in result.days
            ]
        },
        propagated_days=result.propagated_days,
        message=result.message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return RecalcResponse(
        message=result.message,
        log_id=log.id,
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


@router.get("/users/{user_id}/logs", response_model=list[RecalcLogOut])
def list_logs(user_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Histórico de eventos de recálculo del usuario (auditoría)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    logs = (
        db.query(RecalcLog)
        .filter(RecalcLog.user_id == user_id)
        .order_by(RecalcLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return logs
