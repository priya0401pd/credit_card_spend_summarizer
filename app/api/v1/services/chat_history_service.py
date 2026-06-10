from app.core.db import get_db_conn


def save_chat(
    session_id: str,
    role: str,
    message: str
):

    with get_db_conn() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO chat_history
                (
                    session_id,
                    role,
                    message
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session_id,
                    role,
                    message
                )
            )

        conn.commit()


def get_chat_history(
    session_id: str
):

    print("SERVICE SESSION =", session_id)

    with get_db_conn() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM chat_history
                WHERE session_id = %s
                """,
                (session_id,)
            )

            rows = cur.fetchall()

            print("ROWS =", rows)

            return rows