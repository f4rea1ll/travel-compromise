from pydantic import BaseModel
from typing import Optional
from enum import Enum
import uuid
from pydantic import BaseModel, field_validator
from datetime import date

class VibeTag(str, Enum):
    CHILL = "chill"
    ADVENTURE = "adventure"
    CULTURE = "culture"
    FOOD = "food"
    NATURE = "nature"
    BUDGET = "budget"


class MustHave(str, Enum):
    NO_TRANSFERS = "no_transfers"
    BUDGET_STAY = "budget_stay"
    FOOD_NEARBY = "food_nearby"


class ParticipantInput(BaseModel):
    origin_city: str
    budget: float
    vibe_tags: list[VibeTag]
    must_haves: list[MustHave] = []
    departure_date: str
    return_date: str

    @field_validator("departure_date", "return_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Дата должна быть в формате YYYY-MM-DD, получено: {v}")
        return v


class SessionCreateResponse(BaseModel):
    session_id: str
    participant_1_link: str
    participant_2_link: str


class SessionStatus(BaseModel):
    session_id: str
    participant_1_submitted: bool
    participant_2_submitted: bool


# In-memory хранилище — этого достаточно для хакатона,
# но обнулится при перезапуске сервера. Для продакшена нужна БД.
sessions: dict[str, dict] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {
        "participant_1": None,
        "participant_2": None,
    }
    return session_id