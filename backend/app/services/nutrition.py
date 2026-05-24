"""Servicio de cálculo nutricional (F2).

Implementa la fórmula Mifflin-St Jeor y la distribución de macros
según el objetivo del usuario.

Fórmula Mifflin-St Jeor:
    TMB = 10 * peso(kg) + 6.25 * altura(cm) - 5 * edad + s
    s = +5 para hombre, -161 para mujer

TDEE = TMB * factor de actividad (PAL)
"""
from dataclasses import dataclass

from app.models import ActivityLevel, Gender, Goal


PAL: dict[str, float] = {
    ActivityLevel.sedentary.value: 1.2,
    ActivityLevel.light.value: 1.375,
    ActivityLevel.moderate.value: 1.55,
    ActivityLevel.active.value: 1.725,
    ActivityLevel.very_active.value: 1.9,
}


@dataclass
class NutritionResult:
    bmr: float
    tdee: float
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    formula: str = "mifflin-st-jeor"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calcula la Tasa Metabólica Basal con Mifflin-St Jeor."""
    s = 5 if gender == Gender.male.value else -161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + s


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calcula el Gasto Energético Diario Total."""
    return bmr * PAL[activity_level]


def calculate_nutrition_goal(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str,
) -> NutritionResult:
    """Calcula objetivo nutricional completo (kcal + distribución de macros).

    Distribución según objetivo:
    - Pérdida:        déficit 20%, P=2 g/kg, G=25% kcal, C=resto
    - Mantenimiento:  TDEE,        P=1.8 g/kg, G=30% kcal, C=resto
    - Ganancia:       superávit 10%, P=2 g/kg, G=25% kcal, C=resto
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    if goal == Goal.lose.value:
        kcal = tdee * 0.80
        protein_g = 2.0 * weight_kg
        fat_pct = 0.25
    elif goal == Goal.gain.value:
        kcal = tdee * 1.10
        protein_g = 2.0 * weight_kg
        fat_pct = 0.25
    else:  # maintain
        kcal = tdee
        protein_g = 1.8 * weight_kg
        fat_pct = 0.30

    fat_g = (kcal * fat_pct) / 9  # 9 kcal/g grasa
    # Carbohidratos = kcal restantes / 4 kcal/g
    kcal_protein = protein_g * 4
    kcal_fat = fat_g * 9
    kcal_carbs = kcal - kcal_protein - kcal_fat
    carbs_g = max(kcal_carbs / 4, 0)

    return NutritionResult(
        bmr=round(bmr, 1),
        tdee=round(tdee, 1),
        kcal=round(kcal, 1),
        protein_g=round(protein_g, 1),
        carbs_g=round(carbs_g, 1),
        fat_g=round(fat_g, 1),
    )
