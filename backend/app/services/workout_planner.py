"""Generador de rutina semanal de gimnasio.

Reglas:
- Sedentario / light → 3 días de Full Body.
- Moderate → 4 días Upper/Lower.
- Active / very_active → 5 días Push / Pull / Legs / Push / Pull.

Cada día contiene 5-7 ejercicios apropiados, con series, repeticiones
y tiempo estimado. Se ajustan las reps/series según el objetivo:
- "lose"     → repeticiones más altas (12-15), menos descanso.
- "maintain" → rango medio (8-12).
- "gain"     → series más largas (5-8 reps, más peso).
"""
from dataclasses import dataclass


@dataclass
class Exercise:
    name: str
    muscle: str
    sets: int
    reps: str
    rest_seconds: int
    equipment: str  # "barbell" | "dumbbell" | "machine" | "bodyweight"


@dataclass
class WorkoutDay:
    day_label: str
    focus: str
    duration_min: int
    exercises: list[Exercise]
    rest: bool = False


# ===== Catálogo de ejercicios =====
EXERCISES = {
    # Pecho
    "press_banca": Exercise("Press de banca", "Pecho", 4, "8-10", 90, "barbell"),
    "press_inclinado_mancuernas": Exercise("Press inclinado con mancuernas", "Pecho", 3, "10-12", 75, "dumbbell"),
    "fondos": Exercise("Fondos en paralelas", "Pecho", 3, "8-12", 75, "bodyweight"),
    "aperturas": Exercise("Aperturas con mancuernas", "Pecho", 3, "12-15", 60, "dumbbell"),
    # Espalda
    "dominadas": Exercise("Dominadas (asistidas si hace falta)", "Espalda", 4, "6-10", 90, "bodyweight"),
    "remo_barra": Exercise("Remo con barra", "Espalda", 4, "8-10", 90, "barbell"),
    "jalon_polea": Exercise("Jalón al pecho en polea", "Espalda", 3, "10-12", 75, "machine"),
    "remo_sentado": Exercise("Remo sentado en polea", "Espalda", 3, "10-12", 75, "machine"),
    # Hombros
    "press_militar": Exercise("Press militar con barra", "Hombros", 4, "8-10", 90, "barbell"),
    "elevaciones_lat": Exercise("Elevaciones laterales", "Hombros", 4, "12-15", 60, "dumbbell"),
    "face_pull": Exercise("Face pulls", "Hombros / Espalda alta", 3, "12-15", 60, "machine"),
    # Brazos
    "curl_barra": Exercise("Curl de bíceps con barra", "Bíceps", 3, "10-12", 60, "barbell"),
    "curl_martillo": Exercise("Curl martillo con mancuernas", "Bíceps", 3, "10-12", 60, "dumbbell"),
    "extensiones_triceps": Exercise("Extensiones de tríceps en polea", "Tríceps", 3, "10-12", 60, "machine"),
    "press_frances": Exercise("Press francés con mancuerna", "Tríceps", 3, "10-12", 60, "dumbbell"),
    # Piernas
    "sentadilla": Exercise("Sentadilla con barra", "Cuádriceps / Glúteo", 4, "8-10", 120, "barbell"),
    "peso_muerto": Exercise("Peso muerto rumano", "Isquios / Glúteo", 4, "8-10", 120, "barbell"),
    "prensa": Exercise("Prensa de piernas", "Cuádriceps", 4, "10-12", 90, "machine"),
    "zancadas": Exercise("Zancadas alternas con mancuernas", "Piernas", 3, "10 c/lado", 75, "dumbbell"),
    "extension_cuadriceps": Exercise("Extensión de cuádriceps", "Cuádriceps", 3, "12-15", 60, "machine"),
    "femoral_acostado": Exercise("Femoral acostado en máquina", "Isquios", 3, "12-15", 60, "machine"),
    "gemelos": Exercise("Elevación de gemelos de pie", "Gemelos", 4, "15-20", 45, "machine"),
    # Core
    "plancha": Exercise("Plancha frontal", "Core", 3, "45 s", 45, "bodyweight"),
    "crunch_polea": Exercise("Crunch en polea alta", "Core / Abdomen", 3, "12-15", 60, "machine"),
    # Cardio
    "cardio_hiit": Exercise("HIIT en bicicleta / cinta", "Cardio", 1, "20 min", 0, "machine"),
    "cardio_liss": Exercise("Cardio LISS (ligero)", "Cardio", 1, "30 min", 0, "machine"),
}


# ===== Templates por split =====
FULL_BODY_A = ["sentadilla", "press_banca", "remo_barra", "press_militar", "plancha"]
FULL_BODY_B = ["peso_muerto", "dominadas", "press_inclinado_mancuernas", "zancadas", "curl_barra"]
FULL_BODY_C = ["prensa", "fondos", "jalon_polea", "elevaciones_lat", "crunch_polea"]

UPPER_DAY = ["press_banca", "remo_barra", "press_militar", "jalon_polea", "curl_barra", "extensiones_triceps"]
LOWER_DAY = ["sentadilla", "peso_muerto", "prensa", "femoral_acostado", "gemelos", "plancha"]

PUSH_DAY = ["press_banca", "press_inclinado_mancuernas", "press_militar", "elevaciones_lat", "extensiones_triceps", "fondos"]
PULL_DAY = ["dominadas", "remo_barra", "jalon_polea", "face_pull", "curl_barra", "curl_martillo"]
LEGS_DAY = ["sentadilla", "peso_muerto", "prensa", "zancadas", "extension_cuadriceps", "gemelos"]


DAYS_LABELS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def _adjust_for_goal(exercises: list[Exercise], goal: str) -> list[Exercise]:
    """Ajusta series/reps según objetivo del usuario."""
    result = []
    for ex in exercises:
        if goal == "lose":
            # Más reps, menos descanso
            new_reps = ex.reps
            if "-" in ex.reps:
                lo, hi = ex.reps.split("-")
                try:
                    new_reps = f"{int(lo)+2}-{int(hi)+3}"
                except ValueError:
                    pass
            result.append(Exercise(ex.name, ex.muscle, ex.sets, new_reps, max(ex.rest_seconds - 15, 30), ex.equipment))
        elif goal == "gain":
            # Menos reps, más descanso
            new_reps = ex.reps
            if "-" in ex.reps:
                lo, hi = ex.reps.split("-")
                try:
                    new_reps = f"{max(int(lo)-2, 4)}-{max(int(hi)-2, 6)}"
                except ValueError:
                    pass
            result.append(Exercise(ex.name, ex.muscle, ex.sets + 1, new_reps, ex.rest_seconds + 30, ex.equipment))
        else:
            result.append(ex)
    return result


def _build_day(label: str, focus: str, exercise_keys: list[str], goal: str, add_cardio: bool = False) -> WorkoutDay:
    exercises = [EXERCISES[k] for k in exercise_keys]
    if add_cardio:
        exercises.append(EXERCISES["cardio_hiit"] if goal == "lose" else EXERCISES["cardio_liss"])
    exercises = _adjust_for_goal(exercises, goal)
    duration = sum((ex.sets * 60) + (ex.sets * ex.rest_seconds) for ex in exercises) // 60
    return WorkoutDay(
        day_label=label,
        focus=focus,
        duration_min=min(duration, 80),
        exercises=exercises,
    )


def _rest_day(label: str) -> WorkoutDay:
    return WorkoutDay(day_label=label, focus="Descanso activo", duration_min=0, exercises=[], rest=True)


def build_weekly_workout(activity_level: str, goal: str) -> list[WorkoutDay]:
    """Genera la rutina semanal según nivel de actividad y objetivo."""
    add_cardio = goal == "lose"

    if activity_level in ("sedentary", "light"):
        # 3 días Full Body + 4 días descanso/activo
        return [
            _build_day("Lunes", "Full Body A", FULL_BODY_A, goal, add_cardio),
            _rest_day("Martes"),
            _build_day("Miércoles", "Full Body B", FULL_BODY_B, goal, add_cardio),
            _rest_day("Jueves"),
            _build_day("Viernes", "Full Body C", FULL_BODY_C, goal, add_cardio),
            _rest_day("Sábado"),
            _rest_day("Domingo"),
        ]
    elif activity_level == "moderate":
        # 4 días Upper/Lower split
        return [
            _build_day("Lunes", "Upper Body", UPPER_DAY, goal, add_cardio),
            _build_day("Martes", "Lower Body", LOWER_DAY, goal, add_cardio),
            _rest_day("Miércoles"),
            _build_day("Jueves", "Upper Body", UPPER_DAY, goal),
            _build_day("Viernes", "Lower Body", LOWER_DAY, goal),
            _rest_day("Sábado"),
            _rest_day("Domingo"),
        ]
    else:  # active / very_active → 5-6 días PPL
        return [
            _build_day("Lunes", "Push (Pecho/Hombros/Tríceps)", PUSH_DAY, goal, add_cardio),
            _build_day("Martes", "Pull (Espalda/Bíceps)", PULL_DAY, goal),
            _build_day("Miércoles", "Legs (Piernas)", LEGS_DAY, goal, add_cardio),
            _build_day("Jueves", "Push", PUSH_DAY, goal),
            _build_day("Viernes", "Pull", PULL_DAY, goal),
            _build_day("Sábado", "Legs", LEGS_DAY, goal, add_cardio),
            _rest_day("Domingo"),
        ]
