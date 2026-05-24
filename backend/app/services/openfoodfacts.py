"""Cliente para la API pública de OpenFoodFacts (F3).

Documentación: https://world.openfoodfacts.org/api/v2/
"""
import asyncio
from functools import lru_cache

import httpx

from app.config import settings
from app.schemas import FoodSearchResult


# Cache local en memoria para reducir latencia de búsquedas repetidas
_search_cache: dict[str, list[FoodSearchResult]] = {}


def _to_float(value, default: float = 0.0) -> float:
    """Convierte el valor a float; OpenFoodFacts a veces devuelve strings o None."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_product(product: dict) -> FoodSearchResult | None:
    """Convierte un producto crudo de OFF al schema interno."""
    nutriments = product.get("nutriments", {}) or {}
    name = product.get("product_name") or product.get("generic_name")
    if not name:
        return None

    # OFF expone valores por 100g normalizados
    kcal = _to_float(nutriments.get("energy-kcal_100g"))
    if kcal == 0:
        # Fallback: energy en kJ → kcal
        kj = _to_float(nutriments.get("energy_100g"))
        kcal = kj / 4.184 if kj else 0

    return FoodSearchResult(
        off_id=product.get("code") or product.get("_id"),
        name=name.strip(),
        brand=(product.get("brands") or "").split(",")[0].strip() or None,
        kcal_per_100g=round(kcal, 1),
        protein_per_100g=round(_to_float(nutriments.get("proteins_100g")), 1),
        carbs_per_100g=round(_to_float(nutriments.get("carbohydrates_100g")), 1),
        fat_per_100g=round(_to_float(nutriments.get("fat_100g")), 1),
    )


async def search_foods(query: str, limit: int = 15) -> list[FoodSearchResult]:
    """Busca alimentos en OpenFoodFacts por nombre."""
    cache_key = f"{query.lower().strip()}::{limit}"
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    url = f"{settings.openfoodfacts_base_url}/api/v2/search"
    params = {
        "search_terms": query,
        "fields": "code,product_name,generic_name,brands,nutriments",
        "page_size": limit,
        "sort_by": "popularity_key",
    }
    headers = {"User-Agent": settings.openfoodfacts_user_agent}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    products = data.get("products", []) or []
    results: list[FoodSearchResult] = []
    for product in products:
        parsed = _parse_product(product)
        if parsed and parsed.kcal_per_100g > 0:
            results.append(parsed)

    _search_cache[cache_key] = results
    return results


async def get_food_by_barcode(barcode: str) -> FoodSearchResult | None:
    """Obtiene un alimento por código de barras."""
    url = f"{settings.openfoodfacts_base_url}/api/v2/product/{barcode}"
    headers = {"User-Agent": settings.openfoodfacts_user_agent}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()

    product = data.get("product")
    if not product:
        return None
    return _parse_product(product)
