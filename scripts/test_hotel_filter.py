import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.mcp_client import search_hotels

async def main():
    budget = 2000
    result = await search_hotels("Ярославль", "2026-09-05", "2026-09-07", price_max=budget)
    hotels = result.get("hotels", [])
    print(f"Бюджет-фильтр: {budget} RUB")
    print(f"Найдено отелей: {len(hotels)}\n")
    for h in hotels:
        offer = h.get("best_offer", {})
        price = offer.get("price", {})
        print(f"{h.get('name')}: {price} (превышает бюджет: {price.get('amount', 0) > budget})")

if __name__ == "__main__":
    asyncio.run(main())