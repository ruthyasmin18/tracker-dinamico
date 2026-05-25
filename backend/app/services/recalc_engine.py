"""Motor de Recálculo Dinámico (F4 / H4) — CORE del producto.

Cuando el usuario reporta un imprevisto (comer fuera del plan, saltarse una
comida, recorte de tiempo de entrenamiento), este motor:

1. Calcula la desviación respecto al plan original del día.
2. Redistribuye las kcal restantes priorizando proteína intacta:
   - Proteína: NO se reduce (mínimo nutricional no negociable).
   - Carbohidratos: primer macro a ajustar (50% del ajuste).
   - Grasa: ajusta el resto (50% del ajuste).
3. Si la desviación es severa (|delta| > 30% del objetivo diario),
   propaga parcialmente el ajuste a los próximos 2 días para
   suavizar el efecto y no proponer recomendaciones extremas.
4. Devuelve mensajes en lenguaje positivo (sin culpabilizar).

Salida: plan original vs ajustado, día por día, con mensaje accionable.
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import numpy as np


# Umbrales y constantes del algoritmo
SEVERE_DELTA_THRESHOLD = 0.30        # |delta| > 30% del objetivo = severo
MAX_PROPAGATION_DAYS = 2             # cuántos días futuros pueden absorber
CARBS_ADJUSTMENT_SHARE = 0.50        # 50% del ajuste va a carbohidratos
FAT_ADJUSTMENT_SHARE = 0.50          # 50% del ajuste va a grasa
KCAL_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}
MAX_DEFICIT_RATIO = 0.30             # nunca recomendar > 30% de déficit


@dataclass
class MacroSet:
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float

    def to_dict(self) -> dict[str, float]:
        return {
            "kcal": round(self.kcal, 1),
            "protein_g": round(self.protein_g, 1),
            "carbs_g": round(self.carbs_g, 1),
            "fat_g": round(self.fat_g, 1),
        }

    @classmethod
    def from_goal(cls, goal) -> "MacroSet":
        return cls(
            kcal=goal.kcal,
            protein_g=goal.protein_g,
            carbs_g=goal.carbs_g,
            fat_g=goal.fat_g,
        )


@dataclass
class DayAdjustment:
    target_date: date
    original: MacroSet
    adjusted: MacroSet
    note: str


@dataclass
class RecalcResult:
    days: list[DayAdjustment]
    message: str
    propagated_days: int


def _build_positive_message(event_type: str, kcal_delta: float, propagated_days: int) -> str:
    """Genera mensaje accionable y sin culpa."""
    if event_type == "skipped_meal" or kcal_delta < 0:
        if propagated_days > 0:
            return (
                "Plan actualizado: vamos a redistribuir las kcal pendientes a lo largo "
                f"de los próximos {propagated_days + 1} días para que recuperes "
                "ese déficit sin atracarte hoy."
            )
        return "Plan actualizado: tienes margen extra hoy, las comidas siguientes se ajustaron."
    elif event_type == "extra_calories" or kcal_delta > 0:
        if propagated_days > 0:
            return (
                "Plan actualizado: el ajuste se distribuye en los próximos "
                f"{propagated_days + 1} días. Sigues en ruta — sin pasarte mañana."
            )
        return "Plan actualizado: el resto del día se reorganizó para mantenerte en objetivo."
    elif event_type == "reduced_workout_time":
        return "Plan actualizado: las kcal del día se ajustaron al nuevo gasto energético."
    return "Plan actualizado, sigues en ruta."


def _adjust_macros(
    original: MacroSet,
    kcal_adjustment: float,
) -> MacroSet:
    """Aplica un ajuste de kcal preservando proteína y redistribuyendo C/G.

    kcal_adjustment > 0 → hay que sumar kcal restantes (déficit).
    kcal_adjustment < 0 → hay que recortar kcal (exceso).
    """
    new_kcal = original.kcal + kcal_adjustment

    # Proteína intacta
    new_protein = original.protein_g

    # Calcular delta en gramos para carbs y grasa
    delta_kcal_carbs = kcal_adjustment * CARBS_ADJUSTMENT_SHARE
    delta_kcal_fat = kcal_adjustment * FAT_ADJUSTMENT_SHARE

    new_carbs = max(original.carbs_g + delta_kcal_carbs / KCAL_PER_GRAM["carbs"], 0)
    new_fat = max(original.fat_g + delta_kcal_fat / KCAL_PER_GRAM["fat"], 0)

    # Recalcular kcal exacto a partir de los gramos finales
    final_kcal = (
        new_protein * KCAL_PER_GRAM["protein"]
        + new_carbs * KCAL_PER_GRAM["carbs"]
        + new_fat * KCAL_PER_GRAM["fat"]
    )

    return MacroSet(
        kcal=final_kcal,
        protein_g=new_protein,
        carbs_g=new_carbs,
        fat_g=new_fat,
    )


def _clamp_to_safe_deficit(adjusted: MacroSet, baseline: MacroSet) -> MacroSet:
    """Garantiza que el déficit propuesto no sea mayor al MAX_DEFICIT_RATIO."""
    min_kcal = baseline.kcal * (1 - MAX_DEFICIT_RATIO)
    if adjusted.kcal >= min_kcal:
        return adjusted
    # Si quedaríamos por debajo, subimos carbohidratos hasta llegar al mínimo seguro
    needed = min_kcal - adjusted.kcal
    extra_carbs = needed / KCAL_PER_GRAM["carbs"]
    return MacroSet(
        kcal=min_kcal,
        protein_g=adjusted.protein_g,
        carbs_g=adjusted.carbs_g + extra_carbs,
        fat_g=adjusted.fat_g,
    )


AUTO_RECALC_THRESHOLD = 0.15   # 15% de desviación respecto al objetivo = trigger


def compute_diary_deviation(entries: list, goal) -> float:
    """Calcula delta_kcal según la fórmula del informe (F4):

        delta_kcal = consumido_actual − kcal_objetivo_acumuladas_a_esta_hora

    Positivo → exceso calórico. Negativo → déficit.

    Usa la fracción del día transcurrida para saber cuántas kcal
    se esperaban consumir hasta este momento (distribución uniforme).
    El mínimo es 25% del día para evitar falsos positivos a primera hora.
    """
    consumed = sum(e.kcal for e in entries)
    now = datetime.now(timezone.utc)
    current_hour = now.hour + now.minute / 60
    day_fraction = max(current_hour / 24, 0.25)   # al menos 25%
    expected_by_now = goal.kcal * day_fraction
    return consumed - expected_by_now


def run_recalc(
    daily_goal,
    event_type: str,
    kcal_delta: float,
    target_date: date,
) -> RecalcResult:
    """Punto de entrada del motor de recálculo.

    Args:
        daily_goal: instancia de NutritionGoal (objetivo del día base).
        event_type: tipo del evento ("extra_calories" | "skipped_meal" | "reduced_workout_time").
        kcal_delta: kcal de desviación
                    (positivo si excedió, negativo si déficit/saltó comida).
        target_date: día en el que ocurrió el evento.

    Returns:
        RecalcResult con el plan ajustado por día.
    """
    baseline = MacroSet.from_goal(daily_goal)
    # El "ajuste a aplicar" es el opuesto del delta: si excedió +800,
    # hay que restar 800 al día (o repartir entre día + futuros)
    total_adjustment = -kcal_delta
    severity = abs(kcal_delta) / baseline.kcal if baseline.kcal > 0 else 0
    propagate = severity > SEVERE_DELTA_THRESHOLD

    days: list[DayAdjustment] = []

    if not propagate:
        # Aplica todo el ajuste al día del evento
        adjusted = _adjust_macros(baseline, total_adjustment)
        adjusted = _clamp_to_safe_deficit(adjusted, baseline)
        days.append(
            DayAdjustment(
                target_date=target_date,
                original=baseline,
                adjusted=adjusted,
                note="Ajuste aplicado al día del evento.",
            )
        )
        propagated = 0
    else:
        # Distribuye con peso decreciente: día actual lleva más peso
        # Pesos: 0.5 día actual, 0.3 día+1, 0.2 día+2 (suma 1.0)
        weights = np.array([0.5, 0.3, 0.2])
        adjustments = total_adjustment * weights
        for i, adj_kcal in enumerate(adjustments):
            day_date = target_date + timedelta(days=i)
            adjusted = _adjust_macros(baseline, float(adj_kcal))
            adjusted = _clamp_to_safe_deficit(adjusted, baseline)
            note = (
                "Día del evento — ajuste principal."
                if i == 0
                else f"Día +{i} — ajuste residual."
            )
            days.append(
                DayAdjustment(
                    target_date=day_date,
                    original=baseline,
                    adjusted=adjusted,
                    note=note,
                )
            )
        propagated = MAX_PROPAGATION_DAYS

    message = _build_positive_message(event_type, kcal_delta, propagated)
    return RecalcResult(days=days, message=message, propagated_days=propagated)
