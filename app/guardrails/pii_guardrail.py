import re


def mask_pii(text: str) -> str:

    # Card IDs
    text = re.sub(
        r'CC-\d+',
        'CC-XXXXXX',
        text
    )

    # Customer IDs
    text = re.sub(
        r'CUST\d+',
        'CUSTXXXX',
        text
    )

    # Email
    text = re.sub(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        '[EMAIL REDACTED]',
        text
    )

    # Phone
    text = re.sub(
        r'\b\d{10}\b',
        '[PHONE REDACTED]',
        text
    )

    # Aadhaar
    text = re.sub(
        r'\b\d{4}\s?\d{4}\s?\d{4}\b',
        '[AADHAAR REDACTED]',
        text
    )

    # PAN
    text = re.sub(
        r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
        '[PAN REDACTED]',
        text
    )

    # Credit Card Number
    text = re.sub(
        r'\b(?:\d[ -]*?){13,19}\b',
        '[CARD NUMBER REDACTED]',
        text
    )

    return text