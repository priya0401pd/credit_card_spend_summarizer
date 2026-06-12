TOXIC_WORDS = [
    "idiot",
    "stupid",
    "hate",
    "kill",
    "damn",
    "moron"
]


def is_toxic(text: str):

    text = text.lower()

    return any(
        word in text
        for word in TOXIC_WORDS
    )