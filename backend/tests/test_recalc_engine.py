"""Tests del Motor de Recálculo Dinámico (F4 / H4) — CORE.

Cubre los escenarios clave:
- Desviación menor: aplica todo al día del evento.
- Desviación severa (>30% del objetivo): propaga a próximos 2 días.
- Proteína se mantiene intacta.
- Nunca sugiere déficit > 30% (seguridad nutricional).
"""
from dataclasses import dataclass
from datetime import date

import pytest

from app.services.recalc_engine import (
    MacroSet,
    MAX_DEFICIT_RATIO,
    run_recalc,
)


@dataclass
class FakeGoal:
    """Stub de NutritionGoal para tests aislados del ORM."""
    kcal: float = 2400
    protein_g: float = 150
    carbs_g: float = 270
    fat_g: float = 80


class TestRecalcLightDeviation:
    """Desviación menor — no se propaga a otros días."""

    def test_extra_calories_minor(self):
        goal = FakeGoal()
        result = run_recalc(
            daily_goal=goal,
            event_type="extra_calories",
            kcal_delta=200,           # ~8% del objetivo, no severo
            target_date=date(2026, 5, 1),
        )
        assert len(result.days) == 1
        assert result.propagated_days == 0
        # Total recomendado debe bajar respecto al baseline
        assert result.days[0].adjusted.kcal < goal.kcal
        # Proteína intacta
        assert result.days[0].adjusted.protein_g == goal.protein_g

    def test_skipped_meal_minor(self):
        goal = FakeGoal()
        result = run_recalc(
            daily_goal=goal,
            event_type="skipped_meal",
            kcal_delta=-150,
            target_date=date(2026, 5, 1),
        )
        assert len(result.days) == 1
        # Al saltar comida, el plan ajustado debe subir kcal restantes
        assert result.days[0].adjusted.kcal > goal.kcal
        assert result.days[0].adjusted.protein_g == goal.protein_g


class TestRecalcSevereDeviation:
    """Desviación severa (>30%) — se propaga a 2 días futuros."""

    def test_extra_calories_severe_propagates(self):
        goal = FakeGoal()
        result = run_recalc(
            daily_goal=goal,
            event_type="extra_calories",
            kcal_delta=1000,    # ~42% del objetivo, severo
            target_date=date(2026, 5, 1),
        )
        assert len(result.days) == 3
        assert result.propagated_days == 2
        # Fechas consecutivas
        assert result.days[0].target_date == date(2026, 5, 1)
        assert result.days[1].target_date == date(2026, 5, 2)
        assert result.days[2].target_date == date(2026, 5, 3)
        # El día del evento absorbe el mayor ajuste
        diff_day_0 = goal.kcal - result.days[0].adjusted.kcal
        diff_day_1 = goal.kcal - result.days[1].adjusted.kcal
        assert diff_day_0 > diff_day_1


class TestSafetyConstraints:
    """Garantías de seguridad nutricional."""

    def test_never_exceeds_max_deficit(self):
        """Aunque el delta sea masivo, no debe proponer déficit > 30%."""
        goal = FakeGoal()
        result = run_recalc(
            daily_goal=goal,
            event_type="extra_calories",
            kcal_delta=5000,  # exceso masivo
            target_date=date(2026, 5, 1),
        )
        min_allowed = goal.kcal * (1 - MAX_DEFICIT_RATIO)
        for day in result.days:
            assert day.adjusted.kcal >= min_allowed - 0.5, (
                f"Día {day.target_date} con {day.adjusted.kcal} kcal "
                f"viola déficit máximo (mín permitido: {min_allowed})"
            )

    def test_protein_always_preserved(self):
        """Proteína nunca debe reducirse en ningún día ajustado."""
        goal = FakeGoal()
        for delta in [-2000, -500, 100, 500, 2000]:
            result = run_recalc(
                daily_goal=goal,
                event_type="extra_calories" if delta > 0 else "skipped_meal",
                kcal_delta=delta,
                target_date=date(2026, 5, 1),
            )
            for day in result.days:
                assert day.adjusted.protein_g == goal.protein_g

    def test_carbs_and_fat_never_negative(self):
        goal = FakeGoal()
        result = run_recalc(
            daily_goal=goal,
            event_type="extra_calories",
            kcal_delta=10000,
            target_date=date(2026, 5, 1),
        )
        for day in result.days:
            assert day.adjusted.carbs_g >= 0
            assert day.adjusted.fat_g >= 0


class TestPositiveMessaging:
    """El motor debe comunicar en lenguaje positivo."""

    def test_message_no_culpa(self):
        goal = FakeGoal()
        result = run_recalc(
            daily_goal=goal,
            event_type="extra_calories",
            kcal_delta=600,
            target_date=date(2026, 5, 1),
        )
        msg = result.message.lower()
        for forbidden in ["culpa", "fallaste", "error", "mal"]:
            assert forbidden not in msg
        # Debe sentirse accionable
        assert "actualizado" in msg or "ruta" in msg
