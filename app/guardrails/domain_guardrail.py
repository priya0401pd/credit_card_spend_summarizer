# from app.core.llm import llm


# def is_credit_card_query(query: str):

#     response = llm.invoke(
#         f"""
# You are a classifier.

# Determine whether the user query is entirely related to:

# - credit cards
# - spending
# - billing
# - rewards
# - transactions
# - statements
# - card policies
# -Hi
# -hello
# Query:
# {query}

# Rules:
# - If any part of the query is outside this domain, return NO.
# - Otherwise return YES.

# Return only YES or NO.
# """
#     )

#     return (
#         response.content.strip()
#         .upper()
#         == "YES"
#     )


CREDIT_CARD_KEYWORDS = [
    "card",
    "credit",
    "spend",
    "transaction",
    "reward",
    "statement",
    "billing",
    "limit",
    "forex",
    "fee",
    "waiver",
    "customer",
    "merchant",
    "lounge",
    "emi",
    "cashback",
    "points",
    "northstar"
    "Hi"
    "Hello"
    "bye"
]


def is_credit_card_query(
    query: str
) -> bool:

    query = query.lower()

    return any(
        keyword in query
        for keyword in CREDIT_CARD_KEYWORDS
    )