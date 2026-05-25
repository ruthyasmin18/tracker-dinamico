"""Biblioteca curada de alimentos comunes con macros típicos por 100 g.

Se usa como base para el generador de planes semanales (meal_planner) y como
fuente primaria del motor de búsqueda híbrido (F3). Al buscar un alimento,
el sistema consulta primero esta biblioteca local (respuestas instantáneas, sin
latencia de red, 100% relevantes para Perú/Latinoamérica) y complementa con
OpenFoodFacts para productos procesados o de marca.
"""
import unicodedata
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


# ---------------------------------------------------------------------------
# Función utilitaria para normalizar texto (elimina tildes, minúsculas)
# ---------------------------------------------------------------------------
def _normalize(text: str) -> str:
    return unicodedata.normalize("NFD", text.lower()).encode("ascii", "ignore").decode()


FOOD_LIBRARY: list[LibraryFood] = [
    # =====================================================================
    # PROTEÍNAS ANIMALES — bases de la dieta peruana
    # =====================================================================
    LibraryFood("Pechuga de pollo a la plancha", 165, 31.0, 0.0, 3.6, FoodRole.protein, 150),
    LibraryFood("Muslo de pollo sin piel", 177, 24.0, 0.0, 8.8, FoodRole.protein, 150),
    LibraryFood("Pollo a la brasa (pechuga, sin piel)", 170, 28.0, 0.5, 6.0, FoodRole.protein, 150),
    LibraryFood("Pollo a la brasa (muslo/pierna, sin piel)", 215, 23.0, 0.5, 13.0, FoodRole.protein, 150),
    LibraryFood("Pescado (tilapia / merluza)", 105, 22.0, 0.0, 2.2, FoodRole.protein, 150),
    LibraryFood("Trucha serrana al horno", 141, 20.0, 0.0, 6.6, FoodRole.protein, 150),
    LibraryFood("Ceviche de pescado (porción)", 90, 14.0, 5.0, 1.8, FoodRole.protein, 200),
    LibraryFood("Atún en agua", 116, 25.5, 0.0, 1.0, FoodRole.protein, 120),
    LibraryFood("Atún en aceite (escurrido)", 198, 29.0, 0.0, 9.0, FoodRole.protein, 120),
    LibraryFood("Huevo entero cocido", 155, 13.0, 1.1, 11.0, FoodRole.protein, 100),
    LibraryFood("Claras de huevo", 52, 11.0, 0.7, 0.2, FoodRole.protein, 120),
    LibraryFood("Huevo frito (aceite mínimo)", 196, 13.6, 0.4, 15.0, FoodRole.protein, 100),
    LibraryFood("Omelette de 2 huevos", 185, 14.0, 1.5, 14.0, FoodRole.protein, 120),
    LibraryFood("Carne magra de res (bistec)", 175, 26.0, 0.0, 7.0, FoodRole.protein, 120),
    LibraryFood("Lomo fino de res", 164, 27.0, 0.0, 5.8, FoodRole.protein, 120),
    LibraryFood("Carne molida de res (magra 90%)", 152, 22.0, 0.0, 7.0, FoodRole.protein, 120),
    LibraryFood("Hígado de res", 135, 20.0, 3.9, 3.6, FoodRole.protein, 100),
    LibraryFood("Hígado de pollo", 119, 17.0, 0.7, 4.8, FoodRole.protein, 100),
    LibraryFood("Anticucho (corazón de res)", 170, 21.0, 0.0, 9.0, FoodRole.protein, 100),
    LibraryFood("Chicharrón de cerdo", 544, 25.0, 0.0, 49.0, FoodRole.protein, 60),
    LibraryFood("Jamón del país / jamón serrano", 145, 18.0, 2.0, 7.0, FoodRole.protein, 60),
    LibraryFood("Pavo (pechuga, sin piel)", 135, 29.0, 0.0, 1.7, FoodRole.protein, 150),
    LibraryFood("Cerdo (lomo, magro)", 143, 26.0, 0.0, 4.0, FoodRole.protein, 120),
    LibraryFood("Cuy al horno (sin piel)", 155, 21.0, 0.0, 8.0, FoodRole.protein, 100),
    LibraryFood("Alpaca (filete)", 120, 23.0, 0.0, 3.0, FoodRole.protein, 120),
    LibraryFood("Camarones cocidos", 99, 24.0, 0.0, 0.3, FoodRole.protein, 100),
    LibraryFood("Pota / calamar cocido", 92, 15.6, 3.1, 1.4, FoodRole.protein, 120),
    LibraryFood("Caballa enlatada en agua", 168, 25.0, 0.0, 7.6, FoodRole.protein, 120),
    LibraryFood("Sardinas en aceite (escurridas)", 208, 24.0, 0.0, 12.0, FoodRole.protein, 100),
    LibraryFood("Tocino ahumado", 417, 12.5, 0.6, 42.0, FoodRole.protein, 30),

    # =====================================================================
    # LÁCTEOS Y DERIVADOS
    # =====================================================================
    LibraryFood("Leche entera (vaso 250 ml)", 61, 3.2, 4.8, 3.3, FoodRole.protein, 250),
    LibraryFood("Leche evaporada Gloria", 134, 6.8, 10.0, 7.6, FoodRole.protein, 100),
    LibraryFood("Leche descremada", 35, 3.5, 5.0, 0.1, FoodRole.protein, 250),
    LibraryFood("Yogur griego natural", 97, 9.0, 3.6, 5.0, FoodRole.protein, 150),
    LibraryFood("Yogur natural (sin azúcar)", 63, 3.5, 7.0, 1.7, FoodRole.protein, 150),
    LibraryFood("Queso cottage", 98, 11.0, 3.4, 4.3, FoodRole.protein, 120),
    LibraryFood("Queso fresco peruano", 283, 18.0, 2.0, 22.0, FoodRole.protein, 40),
    LibraryFood("Queso andino", 368, 22.0, 2.0, 30.0, FoodRole.protein, 30),
    LibraryFood("Requesón / ricotta", 174, 11.0, 3.0, 13.0, FoodRole.protein, 100),

    # =====================================================================
    # LEGUMBRES — muy consumidas en Perú
    # =====================================================================
    LibraryFood("Menestra de lentejas", 116, 9.0, 20.0, 0.4, FoodRole.protein, 150, vegan=True),
    LibraryFood("Frijol canario cocido", 153, 8.7, 27.0, 0.6, FoodRole.protein, 150, vegan=True),
    LibraryFood("Frijol negro cocido", 132, 8.9, 24.0, 0.5, FoodRole.protein, 150, vegan=True),
    LibraryFood("Pallares cocidos", 140, 9.5, 26.0, 0.4, FoodRole.protein, 150, vegan=True),
    LibraryFood("Habas cocidas", 110, 7.8, 19.0, 0.4, FoodRole.protein, 150, vegan=True),
    LibraryFood("Arvejas cocidas", 84, 5.4, 15.6, 0.2, FoodRole.protein, 150, vegan=True),
    LibraryFood("Garbanzo cocido", 164, 8.9, 27.0, 2.6, FoodRole.protein, 150, vegan=True),
    LibraryFood("Tofu firme", 144, 17.0, 3.0, 8.0, FoodRole.protein, 150, vegan=True),
    LibraryFood("Tempeh", 193, 19.0, 9.0, 11.0, FoodRole.protein, 100, vegan=True),

    # =====================================================================
    # CARBOHIDRATOS / CEREALES Y GRANOS
    # =====================================================================
    LibraryFood("Arroz blanco cocido", 130, 2.7, 28.0, 0.3, FoodRole.carb, 150, vegan=True),
    LibraryFood("Arroz integral cocido", 123, 2.7, 26.0, 1.0, FoodRole.carb, 150, vegan=True),
    LibraryFood("Arroz con leche (casero)", 143, 3.5, 26.0, 3.4, FoodRole.carb, 150),
    LibraryFood("Quinua cocida", 120, 4.4, 21.0, 1.9, FoodRole.carb, 120, vegan=True),
    LibraryFood("Quinua seca (cruda)", 368, 14.0, 64.0, 6.0, FoodRole.carb, 50, vegan=True),
    LibraryFood("Kiwicha / amaranto cocido", 102, 3.8, 19.0, 1.6, FoodRole.carb, 120, vegan=True),
    LibraryFood("Cañihua cocida", 95, 4.4, 17.0, 1.5, FoodRole.carb, 120, vegan=True),
    LibraryFood("Pasta cocida (spaghetti)", 131, 4.5, 25.0, 1.1, FoodRole.carb, 150, vegan=True),
    LibraryFood("Pasta integral cocida", 158, 5.8, 31.0, 1.4, FoodRole.carb, 150, vegan=True),
    LibraryFood("Avena en hojuelas (seco)", 389, 17.0, 66.0, 7.0, FoodRole.carb, 60, vegan=True),
    LibraryFood("Avena cocida con agua", 71, 2.5, 12.0, 1.4, FoodRole.carb, 200, vegan=True),
    LibraryFood("Mote (maíz pelado cocido)", 137, 4.0, 28.0, 1.5, FoodRole.carb, 150, vegan=True),
    LibraryFood("Choclo desgranado cocido", 108, 3.3, 23.0, 1.4, FoodRole.carb, 150, vegan=True),
    LibraryFood("Maíz morado (mazorca)", 100, 3.0, 22.0, 1.0, FoodRole.carb, 100, vegan=True),
    LibraryFood("Chuño (papa deshidratada)", 337, 4.7, 77.0, 0.5, FoodRole.carb, 30, vegan=True),
    LibraryFood("Papa seca", 331, 5.0, 76.0, 0.3, FoodRole.carb, 30, vegan=True),
    LibraryFood("Pan blanco (de molde)", 265, 9.0, 49.0, 3.2, FoodRole.carb, 60, vegan=True),
    LibraryFood("Pan integral", 247, 13.0, 41.0, 4.2, FoodRole.carb, 60, vegan=True),
    LibraryFood("Pan de yema (peruano)", 310, 9.0, 52.0, 8.0, FoodRole.carb, 50),
    LibraryFood("Galleta de soda / agua", 421, 7.5, 70.0, 12.0, FoodRole.carb, 30, vegan=True),
    LibraryFood("Granola casera", 471, 10.0, 64.0, 20.0, FoodRole.carb, 50, vegan=True),
    LibraryFood("Cereal de maíz (tipo Corn Flakes)", 357, 7.5, 84.0, 0.5, FoodRole.carb, 40, vegan=True),
    LibraryFood("Trigo sarraceno cocido", 92, 3.4, 20.0, 0.6, FoodRole.carb, 150, vegan=True),

    # =====================================================================
    # TUBÉRCULOS — esenciales en la dieta peruana
    # =====================================================================
    LibraryFood("Papa blanca cocida", 87, 1.9, 20.0, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Papa amarilla cocida", 80, 2.0, 18.0, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Papa negra cocida", 75, 1.8, 17.0, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Papa al horno con piel", 93, 2.5, 21.0, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Papa frita (casera, aceite mínimo)", 312, 3.4, 41.0, 15.0, FoodRole.carb, 100, vegan=True),
    LibraryFood("Camote / batata cocida", 86, 1.6, 20.0, 0.1, FoodRole.carb, 200, vegan=True),
    LibraryFood("Yuca cocida", 160, 1.4, 38.0, 0.3, FoodRole.carb, 150, vegan=True),
    LibraryFood("Oca cocida", 61, 1.1, 14.0, 0.2, FoodRole.carb, 150, vegan=True),

    # =====================================================================
    # GRASAS SALUDABLES
    # =====================================================================
    LibraryFood("Palta / aguacate", 160, 2.0, 9.0, 15.0, FoodRole.fat, 80, vegan=True),
    LibraryFood("Almendras tostadas", 579, 21.0, 22.0, 50.0, FoodRole.fat, 25, vegan=True),
    LibraryFood("Nueces", 654, 15.0, 14.0, 65.0, FoodRole.fat, 20, vegan=True),
    LibraryFood("Maní tostado sin sal", 567, 26.0, 16.0, 49.0, FoodRole.fat, 25, vegan=True),
    LibraryFood("Aceite de oliva extra virgen", 884, 0.0, 0.0, 100.0, FoodRole.fat, 10, vegan=True),
    LibraryFood("Aceite vegetal (girasol / soya)", 884, 0.0, 0.0, 100.0, FoodRole.fat, 10, vegan=True),
    LibraryFood("Mantequilla", 717, 0.9, 0.1, 81.0, FoodRole.fat, 10),
    LibraryFood("Mantequilla de maní natural", 588, 25.0, 20.0, 50.0, FoodRole.fat, 20, vegan=True),
    LibraryFood("Semillas de chía", 486, 17.0, 42.0, 31.0, FoodRole.fat, 15, vegan=True),
    LibraryFood("Semillas de girasol", 584, 21.0, 20.0, 51.0, FoodRole.fat, 20, vegan=True),
    LibraryFood("Sacha inchi (tostado)", 598, 27.0, 14.0, 48.0, FoodRole.fat, 20, vegan=True),
    LibraryFood("Coco rallado (sin azúcar)", 354, 3.3, 15.0, 33.0, FoodRole.fat, 20, vegan=True),
    LibraryFood("Crema de leche / nata", 340, 2.1, 2.8, 36.0, FoodRole.fat, 30),

    # =====================================================================
    # VEGETALES
    # =====================================================================
    LibraryFood("Brócoli al vapor", 35, 2.4, 7.0, 0.4, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Espinaca fresca / salteada", 23, 2.9, 3.6, 0.4, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Lechuga romana", 17, 1.2, 3.3, 0.3, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Tomate", 18, 0.9, 3.9, 0.2, FoodRole.veggie, 120, vegan=True),
    LibraryFood("Pepino", 16, 0.7, 3.6, 0.1, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Zanahoria", 41, 0.9, 10.0, 0.2, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Cebolla roja", 40, 1.1, 9.3, 0.1, FoodRole.veggie, 60, vegan=True),
    LibraryFood("Cebolla blanca", 40, 1.1, 9.3, 0.1, FoodRole.veggie, 60, vegan=True),
    LibraryFood("Ají amarillo", 40, 1.5, 8.0, 0.4, FoodRole.veggie, 20, vegan=True),
    LibraryFood("Ají panca (pasta)", 57, 1.8, 12.0, 0.6, FoodRole.veggie, 15, vegan=True),
    LibraryFood("Rocoto", 45, 1.5, 9.0, 0.5, FoodRole.veggie, 30, vegan=True),
    LibraryFood("Pimiento rojo", 31, 1.0, 6.0, 0.3, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Pimiento verde", 20, 0.9, 4.6, 0.2, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Coliflor", 25, 1.9, 5.0, 0.3, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Vainita / judía verde", 31, 1.8, 7.0, 0.2, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Zapallo macre cocido", 34, 1.0, 8.0, 0.1, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Calabaza / zapallo cocido", 26, 1.0, 6.5, 0.1, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Acelga cocida", 20, 1.9, 4.1, 0.1, FoodRole.veggie, 100, vegan=True),
    LibraryFood("Apio", 16, 0.7, 3.0, 0.2, FoodRole.veggie, 80, vegan=True),
    LibraryFood("Nabo cocido", 28, 0.9, 6.4, 0.1, FoodRole.veggie, 120, vegan=True),
    LibraryFood("Berenjena asada", 35, 0.8, 8.7, 0.2, FoodRole.veggie, 120, vegan=True),
    LibraryFood("Ensalada mixta (lechuga + tomate + pepino)", 18, 1.0, 3.6, 0.2, FoodRole.veggie, 150, vegan=True),
    LibraryFood("Ensalada de verduras con limón", 25, 1.2, 5.0, 0.3, FoodRole.veggie, 150, vegan=True),

    # =====================================================================
    # FRUTAS — peruanas y comunes en Latinoamérica
    # =====================================================================
    LibraryFood("Manzana", 52, 0.3, 14.0, 0.2, FoodRole.snack, 150, vegan=True),
    LibraryFood("Plátano / banana", 89, 1.1, 23.0, 0.3, FoodRole.carb, 120, vegan=True),
    LibraryFood("Plátano de isla / plátano verde", 122, 1.3, 31.0, 0.4, FoodRole.carb, 100, vegan=True),
    LibraryFood("Naranja (jugo natural)", 45, 0.7, 10.5, 0.2, FoodRole.snack, 200, vegan=True),
    LibraryFood("Mandarina", 53, 0.8, 13.0, 0.2, FoodRole.snack, 100, vegan=True),
    LibraryFood("Mango", 60, 0.8, 15.0, 0.4, FoodRole.snack, 150, vegan=True),
    LibraryFood("Papaya", 43, 0.5, 11.0, 0.3, FoodRole.snack, 150, vegan=True),
    LibraryFood("Piña", 50, 0.5, 13.0, 0.1, FoodRole.snack, 150, vegan=True),
    LibraryFood("Sandía", 30, 0.6, 7.6, 0.2, FoodRole.snack, 200, vegan=True),
    LibraryFood("Uvas rojas / verdes", 69, 0.7, 18.0, 0.2, FoodRole.snack, 100, vegan=True),
    LibraryFood("Fresas / frutillas", 32, 0.7, 7.7, 0.3, FoodRole.snack, 100, vegan=True),
    LibraryFood("Arándanos", 57, 0.7, 14.0, 0.3, FoodRole.snack, 100, vegan=True),
    LibraryFood("Lúcuma (fruta fresca)", 99, 1.4, 23.0, 0.5, FoodRole.snack, 100, vegan=True),
    LibraryFood("Chirimoya", 75, 1.6, 18.0, 0.7, FoodRole.snack, 150, vegan=True),
    LibraryFood("Maracuyá (pulpa)", 97, 2.2, 23.0, 0.7, FoodRole.snack, 50, vegan=True),
    LibraryFood("Granadilla", 97, 2.2, 23.0, 0.7, FoodRole.snack, 100, vegan=True),
    LibraryFood("Aguaymanto / physalis", 53, 1.9, 11.0, 0.7, FoodRole.snack, 80, vegan=True),
    LibraryFood("Guanábana", 66, 1.0, 16.8, 0.3, FoodRole.snack, 150, vegan=True),
    LibraryFood("Tumbo / curuba", 40, 1.0, 9.0, 0.2, FoodRole.snack, 100, vegan=True),
    LibraryFood("Camu camu (pulpa)", 17, 0.5, 4.7, 0.2, FoodRole.snack, 50, vegan=True),
    LibraryFood("Kiwi", 61, 1.1, 15.0, 0.5, FoodRole.snack, 100, vegan=True),
    LibraryFood("Pera", 57, 0.4, 15.0, 0.1, FoodRole.snack, 150, vegan=True),
    LibraryFood("Durazno / melocotón", 39, 0.9, 10.0, 0.3, FoodRole.snack, 120, vegan=True),

    # =====================================================================
    # PLATOS PREPARADOS PERUANOS (valores aproximados por porción estándar)
    # =====================================================================
    LibraryFood("Lomo saltado (porción)", 350, 28.0, 30.0, 12.0, FoodRole.protein, 300),
    LibraryFood("Arroz con pollo (porción)", 290, 22.0, 35.0, 7.0, FoodRole.carb, 300),
    LibraryFood("Causa limeña (porción)", 280, 10.0, 38.0, 10.0, FoodRole.carb, 200),
    LibraryFood("Papa a la huancaína (porción)", 310, 8.0, 32.0, 17.0, FoodRole.carb, 200),
    LibraryFood("Aji de gallina (porción)", 380, 24.0, 28.0, 19.0, FoodRole.protein, 300),
    LibraryFood("Sopa criolla (porción)", 270, 15.0, 30.0, 10.0, FoodRole.carb, 350),
    LibraryFood("Sopa de quinua con verduras", 130, 5.5, 22.0, 2.5, FoodRole.carb, 300, vegan=True),
    LibraryFood("Menú: sopa + segundo + arroz", 680, 38.0, 75.0, 22.0, FoodRole.protein, 500),
    LibraryFood("Tallarin saltado con pollo", 390, 25.0, 48.0, 10.0, FoodRole.carb, 300),
    LibraryFood("Estofado de pollo", 220, 20.0, 18.0, 8.0, FoodRole.protein, 250),
    LibraryFood("Pollo guisado con arroz", 310, 24.0, 34.0, 8.0, FoodRole.protein, 300),
    LibraryFood("Mazamorra morada (porción)", 188, 2.0, 46.0, 0.5, FoodRole.snack, 200, vegan=True),

    # =====================================================================
    # BEBIDAS Y OTROS
    # =====================================================================
    LibraryFood("Chicha morada (vaso 250 ml)", 70, 0.2, 17.0, 0.1, FoodRole.snack, 250, vegan=True),
    LibraryFood("Emoliente (vaso 250 ml)", 55, 0.5, 13.0, 0.1, FoodRole.snack, 250, vegan=True),
    LibraryFood("Jugo de naranja natural (vaso)", 45, 0.7, 10.5, 0.2, FoodRole.snack, 250, vegan=True),
    LibraryFood("Café negro (taza)", 2, 0.3, 0.0, 0.0, FoodRole.snack, 200, vegan=True),
    LibraryFood("Café con leche (cortado)", 47, 2.5, 4.5, 2.1, FoodRole.snack, 200),
    LibraryFood("Té / infusión sin azúcar", 2, 0.0, 0.4, 0.0, FoodRole.snack, 250, vegan=True),

    # =====================================================================
    # SNACKS Y OTROS
    # =====================================================================
    LibraryFood("Barra de proteína", 380, 30.0, 35.0, 12.0, FoodRole.snack, 60),
    LibraryFood("Galletas integrales", 432, 8.4, 67.0, 13.0, FoodRole.snack, 30, vegan=True),
    LibraryFood("Chifles (plátano frito)", 490, 2.0, 60.0, 27.0, FoodRole.snack, 30, vegan=True),
    LibraryFood("Maíz cancha tostado", 415, 8.0, 74.0, 9.0, FoodRole.snack, 30, vegan=True),
    LibraryFood("Habas tostadas saladas", 352, 21.0, 56.0, 4.0, FoodRole.snack, 30, vegan=True),
    LibraryFood("Chocolate negro 70%", 598, 7.8, 46.0, 43.0, FoodRole.snack, 20, vegan=True),
    LibraryFood("Miel de abeja", 304, 0.3, 82.0, 0.0, FoodRole.snack, 10, vegan=True),
    LibraryFood("Mermelada de frutas", 250, 0.5, 65.0, 0.1, FoodRole.snack, 20, vegan=True),
]


# ---------------------------------------------------------------------------
# Búsqueda en la biblioteca local
# ---------------------------------------------------------------------------

def search_local(query: str, limit: int = 15) -> list[LibraryFood]:
    """Busca alimentos por subcadena normalizada (sin tildes, sin mayúsculas).

    Devuelve primero los resultados donde el término aparece al inicio del
    nombre, luego los que lo contienen en cualquier posición, para que
    "huevo" devuelva "Huevo entero" antes que "Omelette de 2 huevos".
    """
    q = _normalize(query.strip())
    if not q:
        return []

    starts: list[LibraryFood] = []
    contains: list[LibraryFood] = []

    for food in FOOD_LIBRARY:
        norm_name = _normalize(food.name)
        if norm_name.startswith(q):
            starts.append(food)
        elif q in norm_name:
            contains.append(food)

    combined = starts + contains
    return combined[:limit]


def get_by_role(role: FoodRole) -> list[LibraryFood]:
    return [f for f in FOOD_LIBRARY if f.role == role]
