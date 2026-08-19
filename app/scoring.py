import asyncio
from app.mcp_client import search_multitransport, search_hotels
from app.candidates import CANDIDATE_CITIES, VIBE_CITY_MAP
from app.services.places import geocode_city, find_attractions

def vibe_match_score(city: str, vibe_tags: list[str]) -> float:
    """Доля вайб-тегов участника, под которые подходит город. От 0 до 1."""
    if not vibe_tags:
        return 0.5  # нейтрально, если тегов нет
    matches = sum(1 for tag in vibe_tags if city in VIBE_CITY_MAP.get(tag, []))
    return matches / len(vibe_tags)


def budget_score(price: float, budget: float) -> float:
    """1.0 если укладывается с запасом, 0.5 впритык, 0.0 если превышен."""
    if price > budget:
        return 0.0
    ratio = price / budget
    if ratio <= 0.7:
        return 1.0
    return 0.5


async def get_best_transport_offer(origin: str, destination: str, departure_date: str) -> dict | None:
    """Возвращает лучший (самый дешёвый) вариант транспорта целиком — цену, тип, ссылку на покупку.
    None, если ничего не нашлось."""
    try:
        result = await search_multitransport(origin, destination, departure_date)
        variants = result.get("variants", [])
        if not variants:
            return None

        priced = [v for v in variants if "price" in v]
        if not priced:
            return None

        cheapest = min(priced, key=lambda v: v["price"]["amount"])

        return {
            "price": cheapest["price"]["amount"],
            "currency": cheapest["price"].get("currency", "RUB"),
            "transport_type": cheapest.get("transport"),
            "duration_min": cheapest.get("duration_min"),
            "checkout_url": cheapest.get("checkout_url"),
            "search_results_url": cheapest.get("search_results_url"),
        }
    except Exception as e:
        print(f"Ошибка поиска транспорта {origin}→{destination}: {e}")
        return None


async def score_candidate(city: str, p1: dict, p2: dict) -> dict | None:
    offer_1, offer_2 = await asyncio.gather(
        get_best_transport_offer(p1["origin_city"], city, p1["departure_date"]),
        get_best_transport_offer(p2["origin_city"], city, p2["departure_date"]),
    )

    if offer_1 is None or offer_2 is None:
        return None

    price_1, price_2 = offer_1["price"], offer_2["price"]

    b1 = budget_score(price_1, p1["budget"])
    b2 = budget_score(price_2, p2["budget"])
    v1 = vibe_match_score(city, p1["vibe_tags"])
    v2 = vibe_match_score(city, p2["vibe_tags"])

    total_score = ((b1 + b2) / 2) * 0.6 + ((v1 + v2) / 2) * 0.4

    return {
        "city": city,
        "total_score": round(total_score, 2),
        "participant_1": {
            "transport_price": price_1,
            "transport_type": offer_1["transport_type"],
            "transport_checkout_url": offer_1["checkout_url"],
            "within_budget": price_1 <= p1["budget"],
            "vibe_match": round(v1, 2),
        },
        "participant_2": {
            "transport_price": price_2,
            "transport_type": offer_2["transport_type"],
            "transport_checkout_url": offer_2["checkout_url"],
            "within_budget": price_2 <= p2["budget"],
            "vibe_match": round(v2, 2),
        },
    }

async def get_best_hotel(city: str, check_in: str, check_out: str, budget: float) -> dict | None:
    """Ищет лучший отель в городе в рамках бюджета. None, если ничего не нашлось."""
    try:
        result = await search_hotels(city, check_in, check_out, price_max=budget)
        hotels = result.get("hotels", [])
        if not hotels:
            return None

        affordable = [
            h for h in hotels
            if h.get("best_offer", {}).get("price", {}).get("amount", float("inf")) <= budget
        ]

        if not affordable:
            return None

        affordable.sort(key=lambda h: h.get("rating") or 0, reverse=True)
        top = affordable[0]
        best_offer = top.get("best_offer", {})

        return {
            "name": top.get("name"),
            "stars": top.get("stars"),
            "rating": top.get("rating"),
            "price": best_offer.get("price", {}).get("amount"),
            "currency": best_offer.get("price", {}).get("currency"),
            "breakfast_included": best_offer.get("breakfast_included"),
            "checkout_url": best_offer.get("checkout_url"),
        }
    except Exception as e:
        print(f"Ошибка поиска отеля в {city}: {e}")
        return None

async def get_city_attractions(city: str, vibe_tags: list[str], limit: int = 3) -> list[dict]:
    """
    Ищет топ-достопримечательности города под общие вайбы обоих участников.
    Возвращает [] если ничего не нашлось — это не критичная ошибка,
    результат матча всё равно валиден без 'why'.
    """
    try:
        coords = await geocode_city(city)
    except Exception as e:
        print(f"Ошибка геокодинга {city}: {e}")
        return []

    # если тегов нет — просто берём культурные места как дефолт
    tags_to_query = vibe_tags or ["культура"]

    tasks = [
        find_attractions(coords["lat"], coords["lon"], vibe, limit=limit)
        for vibe in tags_to_query
    ]

    try:
        results = await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Ошибка поиска мест в {city}: {e}")
        return []

    seen_names = set()
    attractions = []
    for data in results:
        for feature in data.get("features", []):
            props = feature["properties"]
            name = props.get("name")
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            attractions.append({
                "name": name,
                "kinds": props.get("kinds"),
                "rate": props.get("rate"),
            })

    attractions.sort(key=lambda a: a.get("rate") or 0, reverse=True)
    return attractions[:limit]

async def find_best_matches(p1: dict, p2: dict, top_n: int = 3) -> list[dict]:
    """Гоняет все города-кандидаты параллельно, возвращает top_n лучших с отелями."""
    tasks = [score_candidate(city, p1, p2) for city in CANDIDATE_CITIES]
    results = await asyncio.gather(*tasks)
    valid_results = [r for r in results if r is not None]
    valid_results.sort(key=lambda r: r["total_score"], reverse=True)
    top_matches = valid_results[:top_n]

    # Отель ищем только для финалистов — не для всех 15 кандидатов
    remaining_budget = min(p1["budget"], p2["budget"]) * 0.4  # ориентир: ~40% бюджета на жильё
    hotel_tasks = [
        get_best_hotel(m["city"], p1["departure_date"], p1["return_date"], remaining_budget)
        for m in top_matches
    ]
    hotels = await asyncio.gather(*hotel_tasks)

    for match, hotel in zip(top_matches, hotels):
        match["hotel"] = hotel

    # Общие вайбы обоих участников — это и есть "компромисс" в достопримечательностях.
    # Если пересечения нет, берём объединение (лучше показать что-то, чем ничего).
    common_vibes = list(set(p1["vibe_tags"]) & set(p2["vibe_tags"]))
    if not common_vibes:
        common_vibes = list(set(p1["vibe_tags"]) | set(p2["vibe_tags"]))

    attraction_tasks = [
        get_city_attractions(m["city"], common_vibes)
        for m in top_matches
    ]
    attractions_results = await asyncio.gather(*attraction_tasks)

    for match, attractions in zip(top_matches, attractions_results):
        match["why"] = attractions

    return top_matches