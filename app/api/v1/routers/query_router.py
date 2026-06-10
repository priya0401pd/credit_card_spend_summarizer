from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.api.v1.services.query_service import (
    query_service
)
from app.api.v1.services.chat_history_service import (
    save_chat
)

router = APIRouter(
    tags=["insert query"]
)


@router.post("/query")
def query(request: dict):

    query = request["query"]
    

    session_id = request["session_id"]

    save_chat(
        session_id,
        "user",
        query
    )

    result = query_service.ask(
        query
    )

    answer = result[
        "messages"
    ][-1].content

    save_chat(
        session_id,
        "assistant",
        answer
    )
    citations = result.get(
    "citations",
    []
)

    return {
        "answer": answer,
        "citations": citations
    }

@router.post("/query/stream")
def query_stream(request: dict):

    query = request["query"]

    def generate():

        for token in query_service.stream(
            query
        ):
            yield token

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )  