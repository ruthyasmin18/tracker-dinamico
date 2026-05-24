"""Generador de plan semanal de comidas.

Algoritmo:
1. Distribuye las kcal del día en 4 comidas según porcentajes fijos.
2. Para cada comida elige una proteína, un carbohidrato y un acompañante.
3. Calcula los gramos exactos para que la suma de macros se acerque al
   objetivo de la comida (priorizando proteína).
4. Tras armar la comida, si quedó déficit > 100 kcal, escala el carb
   para llenar el gap.
"""
from dataclasses import dataclass
import random

from app.services.food_library import FoodRole, LibraryFood, get_by_role


MEAL_DISTRIBUTION: dict[str, float] = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.30,
    "snack": 0.10,
}
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


@dataclass
class PlannedFood:
    name: str
    grams: float
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    kcal_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float


@dataclass
class PlannedMeal:
    meal: str
    foods: list[PlannedFood]
    total_kcal: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


@dataclass
class PlannedDay:
    day_label: str
    meals: list[PlannedMeal]
    total_kcal: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


def _scale_food(food: LibraryFood, grams: float) -> PlannedFood:
    factor = grams / 100
    return PlannedFood(
        name=food.name,
        grams=round(grams),
        kcal=round(food.kcal * factor, 1),
        protein_g=round(food.protein_g * factor, 1),
        carbs_g=round(food.carbs_g * factor, 1),
        fat_g=round(food.fat_g * factor, 1),
        kcal_per_100g=food.kcal,
        protein_per_100g=food.protein_g,
        carbs_per_100g=food.carbs_g,
        fat_per_100g=food.fat_g,
    )


def _grams_to_kcal(food: LibraryFood, grams: float) -> float:
    return food.kcal * grams / 100


def _build_snack(target_kcal: float, rng: random.Random) -> PlannedMeal:
    snack = rng.choice(get_by_role(FoodRole.snack))
    grams = max(30, min(180, (target_kcal / max(snack.kcal, 1)) * 100))
    grams = round(grams / 5) * 5
    food = _scale_food(snack, grams)
    return PlannedMeal(
        meal="snack",
        foods=[food],
        total_kcal=food.kcal,
        total_protein_g=food.protein_g,
        total_carbs_g=food.carbs_g,
        total_fat_g=food.fat_g,
    )


def _build_main_meal(
    meal_name: str,
    target_kcal: float,
    target_protein: float,
    rng: random.Random,
) -> PlannedMeal:
    """Arma desayuno / almuerzo / cena con proteína + carb + acompañante."""
    if meal_name == "breakfast":
        protein_pool = [
            f for f in get_by_role(FoodRole.protein)
            if f.name in {"Huevo entero", "Claras de huevo", "Yogur griego natural", "Queso cottage"}
        ]
        carb_pool = [
            f for f in get_by_role(FoodRole.carb)
            if f.name in {"Avena (en seco)", "Pan integral", "Plátano"}
        ]
        accomp_pool = get_by_role(FoodRole.fat)
    else:
        # En almuerzo/cena evitamos proteínas muy bajas en kcal (claras, lentejas vegetales)
        # porque obligan a porciones de carb demasiado grandes
        protein_pool = [
            f for f in get_by_role(FoodRole.protein)
            if f.name not in {"Claras de huevo"}
        ]
        carb_pool = get_by_role(FoodRole.carb)
        accomp_pool = get_by_role(FoodRole.veggie)

    protein = rng.choice(protein_pool)
    carb = rng.choice(carb_pool)
    accomp = rng.choice(accomp_pool)

    # 1) Proteína: gramos para llegar al objetivo de proteína de la comida (capado)
    protein_g_objective = max(20, target_protein * 1.0)  # apunta al 100% del objetivo
    needed_grams_for_protein = (protein_g_objective / max(protein.protein_g, 1)) * 100
    protein_grams = max(80, min(needed_grams_for_protein, 250))
    protein_grams = round(protein_grams / 10) * 10

    # 2) Acompañante: porción fija típica (palta 80g, espinaca 100g, etc.)
    accomp_grams = accomp.typical_grams

    # 3) Carb: ajusta para que la suma kcal alcance el objetivo
    consumed_kcal = _grams_to_kcal(protein, protein_grams) + _grams_to_kcal(accomp, accomp_grams)
    deficit_kcal = max(target_kcal - consumed_kcal, 80)  # mínimo 80 kcal de carb
    carb_grams = (deficit_kcal / max(carb.kcal, 1)) * 100
    # Cap razonable según densidad: avena densa (60g típico) vs arroz (300g)
    max_carb_grams = 80 if carb.kcal > 350 else 350
    carb_grams = max(40, min(carb_grams, max_carb_grams))
    carb_grams = round(carb_grams / 10) * 10

    foods = [
        _scale_food(protein, protein_grams),
        _scale_food(carb, carb_grams),
        _scale_food(accomp, accomp_grams),
    ]

    # 4) Si tras todo aún hay déficit > 100 kcal, agrega un poco de grasa saludable
    current_kcal = sum(f.kcal for f in foods)
    if target_kcal - current_kcal > 100 and meal_name in ("lunch", "dinner"):
        extra_fat = next((f for f in get_by_role(FoodRole.fat) if f.name == "Aceite de oliva"), None)
        if extra_fat:
            needed_kcal = target_kcal - current_kcal
            extra_grams = min((needed_kcal / extra_fat.kcal) * 100, 25)
            extra_grams = round(extra_grams)
            if extra_grams >= 5:
                foods.append(_scale_food(extra_fat, extra_grams))

    return PlannedMeal(
        meal=meal_name,
        foods=foods,
        total_kcal=round(sum(f.kcal for f in foods), 1),
        total_protein_g=round(sum(f.protein_g for f in foods), 1),
        total_carbs_g=round(sum(f.carbs_g for f in foods), 1),
        total_fat_g=round(sum(f.fat_g for f in foods), 1),
    )


def build_weekly_plan(
    daily_kcal: float,
    daily_protein: float,
    daily_carbs: float,
    daily_fat: float,
    seed: int = 42,
) -> list[PlannedDay]:
    rng = random.Random(seed)
    plan: list[PlannedDay] = []

    for day in DAYS:
        meals: list[PlannedMeal] = []
        for meal_name, share in MEAL_DISTRIBUTION.items():
            target_kcal = daily_kcal * share
            target_protein = daily_protein * share
            if meal_name == "snack":
                meals.append(_build_snack(target_kcal, rng))
            else:
                meals.append(_build_main_meal(meal_name, target_kcal, target_protein, rng))

        plan.append(PlannedDay(
            day_label=day,
            meals=meals,
            total_kcal=round(sum(m.total_kcal for m in meals), 1),
            total_protein_g=round(sum(m.total_protein_g for m in meals), 1),
            total_carbs_g=round(sum(m.total_carbs_g for m in meals), 1),
            total_fat_g=round(sum(m.total_fat_g for m in meals), 1),
        ))

    return plan
