import re

def normalize_memory_text(text, username="Pinky", ai_name="vmsgk"):
    rules = {
        r"\bi like\b": f"{username} likes",
        r"\bi love\b": f"{username} loves",
        r"\bi am\b": f"{username} is",
        r"\bi'm\b": f"{username} is",
        r"\bmy\b": f"{username}'s",
        r"\bi\b": f"{username}",
        r"\bme\b": f"{username}",
        r"\bmine\b": f"{username}'s",

        r"\byou like\b": f"{ai_name} likes",
        r"\byou love\b": f"{ai_name} loves",
        r"\byou are\b": f"{ai_name} is",
        r"\byou're\b": f"{ai_name} is",
        r"\byour\b": f"{ai_name}'s",
        r"\byou\b": f"{ai_name}",
    }

    new_text = text
    for pattern, repl in rules.items():
        new_text = re.sub(pattern, repl, new_text, flags=re.IGNORECASE)

    return new_text
