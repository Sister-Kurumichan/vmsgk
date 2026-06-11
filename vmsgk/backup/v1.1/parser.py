from semantic import extract_semantics
from cognition import analyze_intent

def parse_memory_entry(text):
    cognition = analyze_intent(text)

    # Never store questions
    if cognition["intent"] != "statement":
        return None

    semantics = extract_semantics(text)

    # No meaningful memory found
    if not semantics["memory_type"]:
        return None

    return {
        "subject": cognition["subject"],
        "memory_type": semantics["memory_type"],
        "memory_value": semantics["memory_value"],
        "certainty": semantics["certainty"],
        "should_store": semantics["certainty"] >= 0.85
    }