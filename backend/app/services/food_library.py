"""Biblioteca curada de alimentos comunes con macros típicos por 100 g.

Se usa como base para el generador de planes semanales (meal_planner).
Cada alimento tiene un perfil dominante (high_protein, balanced, high_carb,
high_fat) para que el armador pueda elegir según el rol de cada comida.
"""
from dataclasses import dataclass
from enum import Enum


class FoodRole(str, Enum):
    protein = "protein"      # Proteína principal de la comida
    carb = "carb"            # Base de carbohidrato
    fat = "fat"              # Aporte de grasa saludable
    veggie = "veggie"        # Vegetal (volumen, micros)
    snack = "snack"          # Snack listo para llevar


@dataclass
class LibraryFood:
    name: str
    kcal: float        # por 100 g
    protein_g: float
    carbs_g: float
    fat_g: float
    role: FoodRole
    typical_grams: int = 100  # porción base sugerida
    vegan: bool = False


FOOD_LIBRARY: list[LibraryFood] = [
    # ===== PROTEÍNAS =====
    LibraryFood("Pechuga de pollo a la plancha", 165, 31, 0, 3.6, FoodRole.protein, 150),
    LibraryFood("Pescado (tilapia / merluza)", 105, 22, 0, 2.2, FoodRole.protein, 150),
    LibraryFood("Atún en agua", 116, 25.5, 0, 1.0, FoodRole.protein, 120),
    LibraryFood("Huevo entero", 155, 13, 1.1, 11, FoodRole.protein, 100),  # ~2 huevos
    LibraryFood("Claras de huevo", 52, 11, 0.7, 0.2, FoodRole.protein, 120),
    LibraryFood("Carne magra de res", 175, 26, 0, 7, FoodRole.protein, 120),
    LibraryFood("Yogur griego natural", 97, 9, 3.6, 5, FoodRole.protein, 150),
    LibraryFood("Queso cottage", 98, 11, 3.4, 4.3, FoodRole.protein, 120),
    LibraryFood("Tofu firme", 144, 17, 3, 8, FoodRole.protein, 150, vegan=True),
    LibraryFood("Lentejas cocidas", 116, 9, 20, 0.4, FoodRole.protein, 150, vegan=True),

    # ===== CARBOHIDRATOS =====
    LibraryFood("Arroz blanco cocido", 130, 2.7, 28, 0.3, FoodRole.carb, 150, vegan=True),
    LibraryFood("Arroz integral cocido", 123, 2.7, 26, 1, FoodRole.carb, 150, vegan=True),
    LibraryFood("Quinoa cocida", 120, 4.4, 21, 1.9, FoodRole.carb, 120, vegan=True),
    LibraryFood("Pasta integral cocida", 158, 5.8, 31, 1.4, FoodRole.carb, 150, vegan=True),
    LibraryFood("Papa al horno", 93, 2.5, 21, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Camote / batata", 86, 1.6, 20, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Avena (en seco)", 389, 17, 66, 7, FoodRole.carb, 60, vegan=True),
    LibraryFood("Pan integral", 247, 13, 41, 4.2, FoodRole.carb, 60, vegan=True),
    LibraryFood("Plátano", 89, 1.1, 23, 0.3, FoodRole.carb, 120, vegan=True),

    # ===== GRASAS =====
    LibraryFood("Palta / aguacate", 160, 2, 9, 15, FoodRole.fat, 80, vegan=True),
    LibraryFood("Almendras", 579, 21, 22, 50, FoodRole.fat, 25, vegan=True),
    LibraryFood("Aceite de oliva", 884, 0, 0, 100, FoodRole.fat, 10, vegan=True),
    LibraryFood("Mantequilla de maní natural", 588, 25, 20, 50, FoodRole.fat, 20, vegan=True),
    LibraryFood("Semillas de chía", 486, 17, 42, 31, FoodRole.fat, 15, vegan=True),

    # ===== VEGETALES =====
    LibraryFood("Brócoli al vapor", 35, 2.4, 7, 0.4, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Espinaca salteada", 23, 2.9, 3.6, 0.4, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Ensalada mixta (lechuga + tomate + pepino)", 18, 1, 3.6, 0.2, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Zanahoria", 41, 0.9, 10, 0.2, FoodRole.veggie, 100, vegan=True),

    # ===== SNACKS =====
    LibraryFood("Manzana", 52, 0.3, 14, 0.2, FoodRole.snack, 150, vegan=True),
    LibraryFood("Arándanos", 57, 0.7, 14, 0.3, FoodRole.snack, 100, vegan=True),
    LibraryFood("Barra de proteína", 380, 30, 35, 12, FoodRole.snack, 60),
    LibraryFood("Galletas integrales", 432, 8.4, 67, 13, FoodRole.snack, 30, vegan=True),
]


def get_by_role(role: FoodRole) -> list[LibraryFood]:
    return [f for f in FOOD_LIBRARY if f.role == role]
