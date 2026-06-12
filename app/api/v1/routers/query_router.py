from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.guardrails.domain_guardrail import (
    is_credit_card_query
)
from app.api.v1.services.query_service import (
    query_service
)
from app.api.v1.services.chat_history_service import (
    save_chat
)
from app.guardrails.pii_guardrail import (
    mask_pii
)

from app.guardrails.toxic_guardrail import (
    is_toxic
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

    if is_toxic(query):

        return {
            "answer":
            (
                "Please use respectful and "
                "professional language."
            )
        }
    
    result = query_service.ask(
        query
    )

    answer = result[
        "messages"
    ][-1].content
    answer = mask_pii(
    answer)

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