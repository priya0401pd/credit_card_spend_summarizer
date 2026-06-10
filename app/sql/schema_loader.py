from app.core.db import get_db_conn


def get_database_schema():

    with get_db_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)

            rows = cur.fetchall()

    schema = {}

    for row in rows:
        table = row["table_name"]

        if table not in schema:
            schema[table] = []

        schema[table].append(
            f"{row['column_name']} ({row['data_type']})"
        )

    return schema

from app.core.db import get_db_conn


def get_database_schema():

    with get_db_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)

            rows = cur.fetchall()

    schema = {}

    for row in rows:
        table = row["table_name"]

        if table not in schema:
            schema[table] = []

        schema[table].append(
            f"{row['column_name']} ({row['data_type']})"
        )

    return schema

def schema_to_text():

    schema = get_database_schema()

    output = []

    for table, columns in schema.items():

        output.append(
            f"\nTable: {table}"
        )

        for col in columns:
            output.append(
                f"  - {col}"
            )

    return "\n".join(output)