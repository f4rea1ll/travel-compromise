from fastapi import APIRouter, HTTPException
from app.services.places import find_attractions, get_place_details

router = APIRouter(prefix="/places", tags=["places"])


@router.get("/{lat}/{lon}")
async def places_by_vibe(lat: float, lon: float, vibe: str = "культура"):
    try:
        data = await find_attractions(lat, lon, vibe)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenTripMap error: {e}")

    return [
        {
            "name": p["properties"]["name"],
            "xid": p["properties"]["xid"],
            "kinds": p["properties"]["kinds"],
            "rate": p["properties"]["rate"],
        }
        for p in data.get("features", [])
        if p["properties"].get("name")
    ]


@router.get("/details/{xid}")
async def place_details(xid: str):
    try:
        data = await get_place_details(xid)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenTripMap error: {e}")

    return {
        "name": data.get("name"),
        "description": data.get("wikipedia_extracts", {}).get("text"),
        "image": data.get("preview", {}).get("source"),
        "kinds": data.get("kinds"),
        "address": data.get("address"),
    }