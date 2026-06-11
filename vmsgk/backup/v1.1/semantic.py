import re

def extract_semantics(text):
    text_low = text.lower()

    semantics = {
        "memory_type": None,
        "memory_value": None,
        "certainty": 1.0
    }

    # uncertainty markers
    if any(w in text_low for w in ["maybe", "i think", "probably", "not sure"]):
        semantics["certainty"] = 0.6

    # favorite color
    m = re.search(r"favorite color is (\w+)", text_low)
    if m:
        semantics["memory_type"] = "favorite_color"
        semantics["memory_value"] = m.group(1)
        return semantics

    # likes
    m = re.search(r"i like (\w+)", text_low)
    if m:
        semantics["memory_type"] = "likes"
        semantics["memory_value"] = m.group(1)
        return semantics

    return semantics