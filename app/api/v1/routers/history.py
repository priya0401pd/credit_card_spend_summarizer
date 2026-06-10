from fastapi import APIRouter

from app.api.v1.services.chat_history_service import (
    get_chat_history
)

router = APIRouter(
    tags=["Chat History"]
)


@router.get("/history/{session_id}")
def history(session_id: str):

    print("HISTORY REQUEST =", session_id)

    result = get_chat_history(
        session_id
    )

    print("RESULT =", result)

    return result