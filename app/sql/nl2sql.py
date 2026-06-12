from app.sql.schema_loader import schema_to_text
from app.sql.bussiness_context import BUSINESS_CONTEXT
from app.core.llm import llm

def generate_sql(query: str):

    schema = schema_to_text()

    prompt = f"""
You are a PostgreSQL expert.

Your job is to translate the user's question into SQL.
- Values beginning with 'CC-' refer to card_id unless explicitly stated otherwise.
- Do not assume CC-* values are customer_id.
Table: credit_cards
- card_id (PRIMARY KEY)
- customer_id (FK -> customers.customer_id)
Rules:
- Generate only SQL.
- Use only tables and columns provided.
- Understand the user's intent.
- Generate the SQL needed to answer the question.
- Do not return partial information.
- If calculations are required, generate the calculation query.
- Values beginning with 'CC-' refer to card_id unless explicitly stated otherwise.
- Do not assume CC-* values are customer_id.
IMPORTANT:
- For spending pattern analysis, retrieve category-wise spending,
  transaction count, and total spend.
- When recommending card upgrades, fetch:
  current card details,
  annual spend,
  rewards earned,
  and available upgrade products.

{BUSINESS_CONTEXT}

Schema:

{schema}

Question:

{query}
"""

    return (
        llm.invoke(prompt)
        .content
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )