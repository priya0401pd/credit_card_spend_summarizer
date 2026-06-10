import base64
import hashlib
import json
import os
import pathlib

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from langchain_openai import OpenAIEmbeddings


load_dotenv()

# ---------------------------------------------------------------------------
# Connection setup
# ---------------------------------------------------------------------------

_PG_CONNECTION = os.getenv("PG_CONNECTION_STRING", "")
_PG_DSN = _PG_CONNECTION.replace(
    "postgresql+psycopg://",
    "postgresql://"
)

# ---------------------------------------------------------------------------
# OpenAI Embeddings
# ---------------------------------------------------------------------------

_EMBED_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small"
)

_embeddings = OpenAIEmbeddings(
    model=_EMBED_MODEL,
    api_key=os.getenv("OPENAI_API_KEY"),
)

def _embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of text strings using OpenAI embeddings.
    """
    return _embeddings.embed_documents(texts)

# ---------------------------------------------------------------------------
# Connection Pool
# ---------------------------------------------------------------------------

_pool: ConnectionPool | None = None

def _get_pool() -> ConnectionPool:
    """
    Return module-level connection pool.
    Creates the pool lazily on first use.
    """
    global _pool

    if _pool is None:
        _pool = ConnectionPool(
            _PG_DSN,
            min_size=2,
            max_size=10,
            kwargs={"row_factory": dict_row},
        )

    return _pool

def get_db_conn():
    """
    Return pooled DB connection.
    """
    return _get_pool().connection()

# ---------------------------------------------------------------------------
# Document Registry
# ---------------------------------------------------------------------------

def upsert_document(filename: str, source_path: str) -> str:
    """
    Insert document metadata.
    If filename already exists, update path and timestamp.
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents
                (
                    filename,
                    source_path
                )
                VALUES (%s, %s)

                ON CONFLICT (filename)
                DO UPDATE
                SET
                    source_path = EXCLUDED.source_path,
                    ingested_at = NOW()

                RETURNING id
                """,
                (
                    filename,
                    source_path,
                ),
            )

            row = cur.fetchone()

        conn.commit()

    return str(row["id"])

# ---------------------------------------------------------------------------
# Chunk Storage
# ---------------------------------------------------------------------------

def store_chunks(chunks: list[dict], doc_id: str) -> int:
    """
    Store text/table/image chunks with embeddings.
    """

    if not chunks:
        return 0

    all_embeddings = _embed_texts(
        [chunk["content"] for chunk in chunks]
    )

    _DEDICATED_COLUMNS = {
        "content_type",
        "element_type",
        "section",
        "page_number",
        "source_file",
        "position",
        "image_base64",
    }

    rows_inserted = 0

    with get_db_conn() as conn:
        with conn.cursor() as cur:

            # Delete old chunks before re-ingestion
            cur.execute(
                """
                DELETE FROM multimodal_chunks
                WHERE doc_id = %s::uuid
                """,
                (doc_id,),
            )

            for chunk, embedding in zip(
                chunks,
                all_embeddings,
            ):
                meta = chunk["metadata"]

                # ---------------------------------------------------------
                # Save image to filesystem
                # ---------------------------------------------------------

                img_b64 = meta.get("image_base64")

                image_path: str | None = None
                mime_type = "image/png" if img_b64 else None

                if img_b64:
                    image_bytes = base64.b64decode(img_b64)

                    img_dir = pathlib.Path(
                        "data/images"
                    )
                    img_dir.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    img_hash = hashlib.sha256(
                        image_bytes
                    ).hexdigest()[:16]

                    img_file = (
                        img_dir /
                        f"{doc_id}_{img_hash}.png"
                    )

                    img_file.write_bytes(
                        image_bytes
                    )

                    image_path = str(img_file)

                # ---------------------------------------------------------
                # Vector String
                # ---------------------------------------------------------

                embedding_str = (
                    "["
                    + ",".join(
                        str(v)
                        for v in embedding
                    )
                    + "]"
                )

                # ---------------------------------------------------------
                # Remove duplicate metadata fields
                # ---------------------------------------------------------

                clean_meta = {
                    k: v
                    for k, v in meta.items()
                    if k not in _DEDICATED_COLUMNS
                }

                cur.execute(
                    """
                    INSERT INTO multimodal_chunks
                    (
                        doc_id,
                        chunk_type,
                        element_type,
                        content,

                        image_path,
                        mime_type,

                        page_number,
                        section,
                        source_file,

                        position,
                        embedding,
                        metadata
                    )
                    VALUES
                    (
                        %s::uuid,
                        %s,
                        %s,
                        %s,

                        %s,
                        %s,

                        %s,
                        %s,
                        %s,

                        %s::jsonb,
                        %s::vector,
                        %s::jsonb
                    )
                    """,
                    (
                        doc_id,
                        chunk["content_type"],
                        meta.get("element_type"),
                        chunk["content"],

                        image_path,
                        mime_type,

                        meta.get("page_number"),
                        meta.get("section"),
                        meta.get("source_file"),

                        json.dumps(
                            meta.get("position")
                        )
                        if meta.get("position")
                        else None,

                        embedding_str,

                        json.dumps(clean_meta),
                    ),
                )

                rows_inserted += 1

        conn.commit()

    return rows_inserted



