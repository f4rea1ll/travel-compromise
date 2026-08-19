from fastapi import APIRouter, HTTPException
from app.models import (
    ParticipantInput,
    SessionCreateResponse,
    SessionStatus,
    sessions,
    create_session,
)
from app.scoring import find_best_matches

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/create", response_model=SessionCreateResponse)
def create():
    session_id = create_session()
    return SessionCreateResponse(
        session_id=session_id,
        participant_1_link=f"/session/{session_id}/join/1",
        participant_2_link=f"/session/{session_id}/join/2",
    )


@router.post("/{session_id}/join/{participant_number}")
def submit_participant(session_id: str, participant_number: int, data: ParticipantInput):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    if participant_number not in (1, 2):
        raise HTTPException(status_code=400, detail="Номер участника должен быть 1 или 2")

    key = f"participant_{participant_number}"
    sessions[session_id][key] = data.model_dump()

    return {"status": "ok", "message": f"Данные участника {participant_number} сохранены"}


@router.get("/{session_id}/status", response_model=SessionStatus)
def get_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    s = sessions[session_id]
    return SessionStatus(
        session_id=session_id,
        participant_1_submitted=s["participant_1"] is not None,
        participant_2_submitted=s["participant_2"] is not None,
    )

@router.get("/{session_id}/result")
async def get_result(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    s = sessions[session_id]
    p1 = s["participant_1"]
    p2 = s["participant_2"]

    if p1 is None or p2 is None:
        raise HTTPException(
            status_code=400,
            detail="Оба участника должны заполнить анкету перед расчётом результата",
        )

    matches = await find_best_matches(p1, p2)

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="Не удалось найти подходящее направление для обоих участников",
        )

    return {"session_id": session_id, "matches": matches}