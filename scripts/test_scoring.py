import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.scoring import find_best_matches


async def main():
    participant_1 = {
        "origin_city": "Москва",
        "budget": 5000,
        "vibe_tags": ["culture", "food"],
        "departure_date": "2026-09-05",
    }
    participant_2 = {
        "origin_city": "Санкт-Петербург",
        "budget": 5000,
        "vibe_tags": ["chill", "culture"],
        "departure_date": "2026-09-05",
    }

    results = await find_best_matches(participant_1, participant_2)

    print(f"\nНайдено {len(results)} подходящих направлений:\n")
    for r in results:
        print(f"{r['city']} — score {r['total_score']}")
        print(f"  Участник 1: {r['participant_1']['transport_price']} RUB, вайб {r['participant_1']['vibe_match']}")
        print(f"  Участник 2: {r['participant_2']['transport_price']} RUB, вайб {r['participant_2']['vibe_match']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())