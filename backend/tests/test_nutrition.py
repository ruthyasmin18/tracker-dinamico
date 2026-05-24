"""Tests del servicio de cálculo nutricional (F2)."""
import pytest

from app.services.nutrition import (
    calculate_bmr,
    calculate_nutrition_goal,
    calculate_tdee,
)


class TestMifflinStJeor:
    def test_male_baseline(self):
        # Hombre 25 años, 75 kg, 175 cm
        # 10*75 + 6.25*175 - 5*25 + 5 = 750 + 1093.75 - 125 + 5 = 1723.75
        bmr = calculate_bmr(weight_kg=75, height_cm=175, age=25, gender="male")
        assert bmr == pytest.approx(1723.75, abs=0.1)

    def test_female_baseline(self):
        # Mujer 30 años, 60 kg, 165 cm
        # 10*60 + 6.25*165 - 5*30 + (-161) = 600 + 1031.25 - 150 - 161 = 1320.25
        bmr = calculate_bmr(weight_kg=60, height_cm=165, age=30, gender="female")
        assert bmr == pytest.approx(1320.25, abs=0.1)


class TestTDEE:
    def test_sedentary_factor(self):
        assert calculate_tdee(2000, "sedentary") == 2400  # 2000 * 1.2

    def test_very_active_factor(self):
        assert calculate_tdee(2000, "very_active") == 3800  # 2000 * 1.9


class TestNutritionGoal:
    def test_maintenance_distribution(self):
        result = calculate_nutrition_goal(
            weight_kg=75, height_cm=175, age=25, gender="male",
            activity_level="moderate", goal="maintain",
        )
        # En mantenimiento, kcal == TDEE
        assert result.kcal == pytest.approx(result.tdee, abs=0.5)
        # P = 1.8 g/kg = 135 g para 75 kg
        assert result.protein_g == pytest.approx(135.0, abs=0.5)
        # Las kcal totales deben coincidir con la suma de macros
        total = result.protein_g * 4 + result.carbs_g * 4 + result.fat_g * 9
        assert abs(total - result.kcal) < 5  # margen por redondeo

    def test_lose_creates_deficit(self):
        maintain = calculate_nutrition_goal(
            75, 175, 25, "male", "moderate", "maintain",
        )
        lose = calculate_nutrition_goal(
            75, 175, 25, "male", "moderate", "lose",
        )
        # Pérdida debe ser ~20% menor
        assert lose.kcal < maintain.kcal
        assert lose.kcal == pytest.approx(maintain.tdee * 0.80, abs=1)
        # Proteína sube a 2 g/kg
        assert lose.protein_g == pytest.approx(150.0, abs=0.5)

    def test_gain_creates_surplus(self):
        maintain = calculate_nutrition_goal(
            75, 175, 25, "male", "moderate", "maintain",
        )
        gain = calculate_nutrition_goal(
            75, 175, 25, "male", "moderate", "gain",
        )
        # Ganancia debe ser ~10% mayor
        assert gain.kcal > maintain.kcal
        assert gain.kcal == pytest.approx(maintain.tdee * 1.10, abs=1)

    def test_carbs_never_negative(self):
        """Si baja mucho la proteína no debe haber carbs negativos."""
        result = calculate_nutrition_goal(
            30, 150, 14, "female", "sedentary", "lose",
        )
        assert result.carbs_g >= 0
        assert result.fat_g >= 0
        assert result.protein_g > 0
