import re

def normalize_value(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    # remove filler phrases
    text = re.sub(
        r"\b(i like|i love|my favorite|my fave|i am|i'm|it is|it's)\b",
        "",
        text
    )

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()