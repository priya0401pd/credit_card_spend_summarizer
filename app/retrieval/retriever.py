import os
import cohere


from langchain_openai import (
    OpenAIEmbeddings
)

from app.core.db import (
    get_db_conn
)


class Retriever:

    def __init__(self):

        self.embeddings = (
            OpenAIEmbeddings(
                model=os.getenv(
                    "OPENAI_EMBEDDING_MODEL",
                    "text-embedding-3-small"
                ),
                api_key=os.getenv(
                    "OPENAI_API_KEY"
                )
            )
        )

        self.cohere_client = (
            cohere.ClientV2(
                api_key=os.getenv(
                    "COHERE_API_KEY"
                )
            )
        )

    # =====================================
    # RERANK
    # =====================================
    def rerank(
    self,
    query: str,
    documents: list,
    top_k: int = 10
):

        if not documents:
            return []

        print(
            f"\nBefore rerank: {len(documents)} docs"
        )

        response = self.cohere_client.rerank(
            model="rerank-v3.5",
            query=query,
            documents=[
                d["content"]
                for d in documents
            ],
            top_n=min(
                top_k,
                len(documents)
            )
        )

        print(
            f"After rerank: {len(response.results)} docs"
        )

        print("\nTop reranked results:\n")

        for idx, result in enumerate(
            response.results[:5],
            start=1
        ):
            print(
                f"Rank {idx} | "
                f"Score={result.relevance_score:.4f}"
            )

        return [
            documents[r.index]
            for r in response.results
        ]

    # def rerank(
    #     self,
    #     query: str,
    #     documents: list,
    #     top_k: int = 10
    # ):

    #     if not documents:
    #         return []

    #     response = (
    #         self.cohere_client.rerank(
    #             model="rerank-v3.5",
    #             query=query,
    #             documents=[
    #                 d["content"]
    #                 for d in documents
    #             ],
    #             top_n=min(
    #                 top_k,
    #                 len(documents)
    #             )
    #         )
    #     )

    #     return [
    #         documents[r.index]
    #         for r in response.results
    #     ]

    # =====================================
    # VECTOR TOOL
    # =====================================

    def vector_tool(
        self,
        query: str,
        top_k: int = 10
    ):

        query_embedding = (
            self.embeddings.embed_query(
                query
            )
        )

        embedding_str = (
            "["
            + ",".join(
                str(v)
                for v in query_embedding
            )
            + "]"
        )

        with get_db_conn() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        content,
                        section,
                        page_number,
                        source_file,

                        embedding <=> %s::vector
                        AS distance

                    FROM multimodal_chunks

                    ORDER BY
                        embedding <=> %s::vector

                    LIMIT 50
                    """,
                    (
                        embedding_str,
                        embedding_str
                    )
                )

                docs = cur.fetchall()

        return self.rerank(
            query=query,
            documents=docs,
            top_k=top_k
        )

    # =====================================
    # FTS TOOL
    # =====================================

    def fts_tool(
        self,
        query: str,
        top_k: int = 10
    ):

        with get_db_conn() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        content,
                        section,
                        page_number,
                        source_file,

                        ts_rank(
                            search_vector,
                            plainto_tsquery(
                                'english',
                                %s
                            )
                        ) AS score

                    FROM multimodal_chunks

                    WHERE search_vector @@
                        plainto_tsquery(
                            'english',
                            %s
                        )

                    ORDER BY score DESC

                    LIMIT 50
                    """,
                    (
                        query,
                        query
                    )
                )

                docs = cur.fetchall()

        return self.rerank(
            query=query,
            documents=docs,
            top_k=top_k
        )

    # =====================================
    # HYBRID TOOL
    # =====================================

    def hybrid_tool(
        self,
        query: str,
        top_k: int = 10
    ):

        query_embedding = (
            self.embeddings.embed_query(
                query
            )
        )

        embedding_str = (
            "["
            + ",".join(
                str(v)
                for v in query_embedding
            )
            + "]"
        )

        with get_db_conn() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        content,
                        section,
                        page_number,
                        source_file

                    FROM multimodal_chunks

                    ORDER BY
                        embedding <=> %s::vector

                    LIMIT 50
                    """,
                    (embedding_str,)
                )

                vector_docs = (
                    cur.fetchall()
                )

        try:

            with get_db_conn() as conn:

                with conn.cursor() as cur:

                    cur.execute(
                        """
                        SELECT
                            content,
                            section,
                            page_number,
                            source_file

                        FROM multimodal_chunks

                        WHERE search_vector @@
                            plainto_tsquery(
                                'english',
                                %s
                            )

                        LIMIT 50
                        """,
                        (query,)
                    )

                    keyword_docs = (
                        cur.fetchall()
                    )

        except Exception:

            keyword_docs = []

        merged = []

        seen = set()

        for doc in (
            vector_docs +
            keyword_docs
        ):

            content = doc["content"]

            if content in seen:
                continue

            seen.add(content)

            merged.append(doc)

        return self.rerank(
            query=query,
            documents=merged,
            top_k=top_k
        )


retriever = Retriever() 


