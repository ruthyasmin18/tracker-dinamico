"""Cliente para la API pública de OpenFoodFacts (F3).

Documentación: https://world.openfoodfacts.org/api/v2/

Se usa como fuente COMPLEMENTARIA al buscador híbrido definido en diary.py.
La biblioteca local (food_library.py) tiene prioridad porque sus datos son
curados, en español y relevantes para Perú/Latinoamérica. OpenFoodFacts
aporta productos procesados de marca que no están en la biblioteca local.
"""
import asyncio
from functools import lru_cache

import httpx

from app.config import settings
from app.schemas import FoodSearchResult


# Cache local en memoria para reducir latencia de búsquedas repetidas.
# Se limpia al reiniciar el servidor.
_search_cache: dict[str, list[FoodSearchResult]] = {}

# Países hispanohablantes en formato de etiqueta OpenFoodFacts.
# Prioriza Perú, luego el resto de Latinoamérica y España.
_HISPANIC_COUNTRIES = (
    "en:peru,en:mexico,en:colombia,en:argentina,en:chile,"
    "en:ecuador,en:bolivia,en:venezuela,en:spain"
)


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

    # Preferir nombre en español si está disponible
    name = (
        product.get("product_name_es")
        or product.get("product_name")
        or product.get("generic_name_es")
        or product.get("generic_name")
    )
    if not name or len(name.strip()) < 2:
        return None

    # OFF expone valores por 100g normalizados
    kcal = _to_float(nutriments.get("energy-kcal_100g"))
    if kcal == 0:
        # Fallback: energy en kJ → kcal
        kj = _to_float(nutriments.get("energy_100g"))
        kcal = kj / 4.184 if kj else 0

    if kcal == 0:
        return None  # sin datos calóricos, no sirve

    return FoodSearchResult(
        off_id=product.get("code") or product.get("_id"),
        name=name.strip(),
        brand=(product.get("brands") or "").split(",")[0].strip() or None,
        kcal_per_100g=round(kcal, 1),
        protein_per_100g=round(_to_float(nutriments.get("proteins_100g")), 1),
        carbs_per_100g=round(_to_float(nutriments.get("carbohydrates_100g")), 1),
        fat_per_100g=round(_to_float(nutriments.get("fat_100g")), 1),
    )


async def _fetch_off(query: str, limit: int, countries: str | None = None) -> list[FoodSearchResult]:
    """Realiza una búsqueda en OpenFoodFacts con los parámetros dados."""
    url = f"{settings.openfoodfacts_base_url}/api/v2/search"
    params: dict = {
        "search_terms": query,
        "fields": "code,product_name,product_name_es,generic_name,generic_name_es,brands,nutriments",
        "page_size": limit * 4,        # pedimos más para tener margen al filtrar
        "sort_by": "unique_scans_n",   # popularidad real de escaneos
        "lc": "es",                    # language code: traducciones al español
        "lang": "es",                  # prioriza índice de nombres en español
    }
    if countries:
        params["countries_tags"] = countries

    headers = {"User-Agent": settings.openfoodfacts_user_agent}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    products = data.get("products", []) or []
    results: list[FoodSearchResult] = []
    for product in products:
        parsed = _parse_product(product)
        if parsed:
            results.append(parsed)
        if len(results) >= limit:
            break

    return results


async def search_foods(query: str, limit: int = 15) -> list[FoodSearchResult]:
    """Busca alimentos en OpenFoodFacts.

    Estrategia de dos pasadas:
    1. Busca primero filtrado por países hispanohablantes (más relevante).
    2. Si no alcanza el mínimo (≥3 resultados), hace una búsqueda global
       para no dejar al usuario con resultados vacíos.
    """
    cache_key = f"{query.lower().strip()}::{limit}"
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    # Pasada 1 — países hispanohablantes
    results = await _fetch_off(query, limit, countries=_HISPANIC_COUNTRIES)

    # Pasada 2 — global si no hay suficientes resultados
    if len(results) < 3:
        global_results = await _fetch_off(query, limit, countries=None)
        # Agregar solo los que no están ya en results (deduplicar por off_id)
        existing_ids = {r.off_id for r in results}
        for r in global_results:
            if r.off_id not in existing_ids:
                results.append(r)
            if len(results) >= limit:
                break

    _search_cache[cache_key] = results
    return results


async def get_food_by_barcode(barcode: str) -> FoodSearchResult | None:
    """Obtiene un alimento por código de barras."""
    url = f"{settings.openfoodfacts_base_url}/api/v2/product/{barcode}"
    params = {"lc": "es"}
    headers = {"User-Agent": settings.openfoodfacts_user_agent}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()

    product = data.get("product")
    if not product:
        return None
    return _parse_product(product)
