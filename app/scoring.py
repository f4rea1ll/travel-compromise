import asyncio
from app.mcp_client import search_multitransport, search_hotels
from app.candidates import CANDIDATE_CITIES, VIBE_CITY_MAP


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


async def get_transport_price(origin: str, destination: str, departure_date: str) -> float | None:
    """Возвращает минимальную цену транспорта до города или None, если ничего не нашлось."""
    try:
        result = await search_multitransport(origin, destination, departure_date)
        variants = result.get("variants", [])
        if not variants:
            return None
        prices = [v["price"]["amount"] for v in variants if "price" in v]
        return min(prices) if prices else None
    except Exception as e:
        print(f"Ошибка поиска транспорта {origin}→{destination}: {e}")
        return None


async def score_candidate(city: str, p1: dict, p2: dict) -> dict | None:
    """Считает совпадение города с обоими участниками. None, если транспорт не найден хотя бы для одного."""
    price_1, price_2 = await asyncio.gather(
        get_transport_price(p1["origin_city"], city, p1["departure_date"]),
        get_transport_price(p2["origin_city"], city, p2["departure_date"]),
    )

    if price_1 is None or price_2 is None:
        return None

    b1 = budget_score(price_1, p1["budget"])
    b2 = budget_score(price_2, p2["budget"])
    v1 = vibe_match_score(city, p1["vibe_tags"])
    v2 = vibe_match_score(city, p2["vibe_tags"])

    total_score = (b1 + b2) * 0.6 + (v1 + v2) * 0.4

    return {
        "city": city,
        "total_score": round(total_score, 2),
        "participant_1": {
            "transport_price": price_1,
            "within_budget": price_1 <= p1["budget"],
            "vibe_match": round(v1, 2),
        },
        "participant_2": {
            "transport_price": price_2,
            "within_budget": price_2 <= p2["budget"],
            "vibe_match": round(v2, 2),
        },
    }


async def find_best_matches(p1: dict, p2: dict, top_n: int = 3) -> list[dict]:
    """Гоняет все города-кандидаты параллельно и возвращает top_n лучших."""
    tasks = [score_candidate(city, p1, p2) for city in CANDIDATE_CITIES]
    results = await asyncio.gather(*tasks)
    valid_results = [r for r in results if r is not None]
    valid_results.sort(key=lambda r: r["total_score"], reverse=True)
    return valid_results[:top_n]