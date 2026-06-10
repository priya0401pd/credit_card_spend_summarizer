import os

from app.ingestion.ingestion import run_ingestion


class UploadService:

    def upload_and_ingest(
        self,
        file,
        upload_dir: str
    ):

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(file.file.read())

        inserted_count = (
            run_ingestion(
                file_path
            )
        )

        return {
            "filename": file.filename,
            "inserted_chunks": inserted_count,
            "status": "success"
        }


upload_service = UploadService()