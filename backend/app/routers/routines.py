"""Router de Generador de Rutinas Express (F5).

POST /api/routines/quick  → rutina adaptada al tiempo y equipo disponibles.
"""
from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.schemas import ExpressRoutineRequest, WorkoutDayOut
from app.services.workout_planner import generate_express_routine

router = APIRouter(prefix="/api/routines", tags=["routines"])

VALID_EQUIPMENT = {"bodyweight", "dumbbell", "full"}
VALID_MUSCLES   = {"all", "chest", "back", "legs", "arms", "shoulders", "core"}


@router.post("/quick", response_model=WorkoutDayOut)
def quick_routine(payload: ExpressRoutineRequest):
    """Genera una rutina Express en < 800 ms.

    - `available_time_min`: ventana de tiempo en minutos (10-120).
    - `equipment`: equipo disponible (`bodyweight` / `dumbbell` / `full`).
    - `target_muscle`: grupo muscular objetivo (`all` / `chest` / `back` /
      `legs` / `arms` / `shoulders` / `core`).
    - `goal`: objetivo del usuario (`lose` / `maintain` / `gain`).

    Garantiza ≥ 4 ejercicios, sin exceder el tiempo indicado (+20% buffer).
    """
    if payload.equipment not in VALID_EQUIPMENT:
        raise HTTPException(
            status_code=422,
            detail=f"equipment debe ser uno de: {', '.join(sorted(VALID_EQUIPMENT))}",
        )
    if payload.target_muscle not in VALID_MUSCLES:
        raise HTTPException(
            status_code=422,
            detail=f"target_muscle debe ser uno de: {', '.join(sorted(VALID_MUSCLES))}",
        )

    day = generate_express_routine(
        available_time_min=payload.available_time_min,
        equipment=payload.equipment,
        target_muscle=payload.target_muscle,
        goal=payload.goal,
    )
    return asdict(day)
