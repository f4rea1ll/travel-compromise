import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENTRIPMAP_KEY = os.getenv("OPENTRIPMAP_API_KEY")
BASE_URL = "https://api.opentripmap.com/0.1/en/places"

# Маппинг наших "вайбов" на категории OpenTripMap (kinds)
VIBE_TO_KINDS = {
    "расслабон": "beaches,natural,spas",
    "движ": "amusements,nightclubs,adult",
    "культура": "cultural,museums,architecture,historic",
    "еда": "foods,restaurants",
}


async def find_attractions(lat: float, lon: float, vibe: str, radius: int = 5000, limit: int = 10):
    """
    Ищет достопримечательности в радиусе от точки (lat, lon).
    vibe — один из ключей VIBE_TO_KINDS.
    """
    kinds = VIBE_TO_KINDS.get(vibe, "interesting_places")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/radius",
            params={
                "apikey": OPENTRIPMAP_KEY,
                "lat": lat,
                "lon": lon,
                "radius": radius,
                "kinds": kinds,
                "limit": limit,
                "format": "json",
                "rate": 2,
            },
        )
        response.raise_for_status()
        return response.json()


async def get_place_details(xid: str):
    """
    Получает подробности о конкретном месте по его xid
    (описание, фото, ссылка на wikidata и т.д.)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/xid/{xid}",
            params={"apikey": OPENTRIPMAP_KEY},
        )
        response.raise_for_status()
        return response.json()

# добавить в app/services/places.py

async def geocode_city(city_name: str) -> dict:
    """
    Получает координаты города по названию через OpenTripMap.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/geoname",
            params={
                "apikey": OPENTRIPMAP_KEY,
                "name": city_name,
            },
        )
        response.raise_for_status()
        data = response.json()
        return {"lat": data["lat"], "lon": data["lon"]}