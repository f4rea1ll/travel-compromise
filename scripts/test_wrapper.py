import asyncio
from app.mcp_client import search_multitransport

async def main():
    result = await search_multitransport("Москва", "Казань", "2026-09-01")
    print(f"Найдено вариантов: {len(result.get('variants', []))}")
    for v in result.get("variants", [])[:3]:
        print(f"— {v['transport']}: {v['price']['amount']} {v['price']['currency']}, {v['duration_min']} мин")

if __name__ == "__main__":
    asyncio.run(main())