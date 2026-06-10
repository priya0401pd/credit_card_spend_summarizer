from langchain_core.tools import tool
import json
from app.core.db import get_db_conn
from app.sql.nl2sql import generate_sql


def execute_sql(sql: str):

    sql_lower = sql.lower().strip()

    if not sql_lower.startswith("select"):
        raise ValueError(
            "Only SELECT queries allowed"
        )

    # Add LIMIT if missing
    if "limit" not in sql_lower:
        sql = sql.rstrip(";") + " LIMIT 100;"

    print("\nFinal SQL:\n")
    print(sql)

    with get_db_conn() as conn:

        with conn.cursor() as cur:

            cur.execute(sql)

            rows = cur.fetchall()

    return rows





@tool
def sql_tool(query: str):
    """
    Use for:
    customer spend,
    transactions,
    reward points,
    fee waiver status,
    account information.
    """
    print("\n SQL tool Called \n")
    sql = generate_sql(query)

    print("\nGenerated SQL:\n")
    print(sql)

    result = execute_sql(sql)

    print("\nSQL Result:\n")
    print(result)

    return json.dumps(
        result,
        default=str,
        indent=2
    )