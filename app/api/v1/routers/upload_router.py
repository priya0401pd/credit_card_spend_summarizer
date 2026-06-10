from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from app.api.v1.services.upload_service import (
    upload_service
)

router = APIRouter(
    prefix="/upload",
    tags=["Document Upload"]
)

UPLOAD_DIR = "uploaded_docs"


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    result = (
        upload_service.upload_and_ingest(
            file=file,
            upload_dir=UPLOAD_DIR
        )
    )

    return result