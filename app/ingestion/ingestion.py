

import pathlib

# Import database helper functions
from app.core.db import upsert_document, store_chunks


# Import PDF parsing utility
from app.ingestion.docling_parser import parse_document


# Maximum size of each text chunk
TEXT_CHUNK_SIZE = 500

# Number of overlapping characters between chunks
# Helps preserve context across chunk boundaries
TEXT_CHUNK_OVERLAP = 100


def split_text(text: str):
    """
    Splits large text into smaller overlapping chunks.

    This improves embedding quality and retrieval accuracy
    for long documents.
    """

    chunks = []
    start = 0

    # Calculate next chunk starting position
    step = TEXT_CHUNK_SIZE - TEXT_CHUNK_OVERLAP

    while start < len(text):

        chunks.append(
            text[start:start + TEXT_CHUNK_SIZE]
        )

        start += step

    return chunks


def run_ingestion(file_path: str):
    """
    Executes the complete document ingestion workflow.

    Workflow:
    1. Register document
    2. Parse document content
    3. Split large text chunks
    4. Generate embeddings
    5. Store chunks in PGVector
    """

    # Convert relative path to absolute path
    file_path = str(
        pathlib.Path(file_path).resolve()
    )

    # Register document in documents table
    # Returns unique document identifier
    doc_id = upsert_document(
        filename=pathlib.Path(file_path).name,
        source_path=file_path
    )

    # Extract text, tables, and images from document
    parsed = parse_document(file_path)

    final_chunks = []

    # Process extracted content
    for chunk in parsed:

        # Split large text blocks into smaller chunks
        if (
            chunk["content_type"] == "text"
            and len(chunk["content"]) > TEXT_CHUNK_SIZE
        ):

            sub_chunks = split_text(
                chunk["content"]
            )

            # Preserve metadata for each generated chunk
            for text in sub_chunks:

                final_chunks.append({
                    "content": text,
                    "content_type": chunk["content_type"],
                    "metadata": chunk["metadata"]
                })

        else:

            # Store non-text content and smaller text chunks as-is
            final_chunks.append(chunk)

    # Generate embeddings and persist chunks
    count = store_chunks(
        final_chunks,
        doc_id
    )

    # Return ingestion summary
    return {
        "status": "success",
        "doc_id": doc_id,
        "chunks_ingested": count
    }