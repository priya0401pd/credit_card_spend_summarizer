from fastapi import FastAPI

from app.api.v1.routers.upload_router import router as upload_router
from app.api.v1.routers.query_router import (
    router as query_router
)
from app.api.v1.routers.history import (
    router as history_router
)
app = FastAPI(title="Credit Card Spend Summarizer")



app.include_router(
    history_router,
    prefix="/api/v1"
)
app.include_router(upload_router)

app.include_router(
    query_router,
    prefix="/api/v1"
)