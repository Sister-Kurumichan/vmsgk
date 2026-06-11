# parser.py
# Smart memory extraction system — replacing categorize_memory()

import re

"""
parse_memory_entry(text) analyzes a sentence and returns:
    (who, category)
or
    None          if the sentence contains no stable memory.

who:
    "Pinky", "core_identity", or "general"

category:
    "facts", "likes", "goals", "notes"
"""

# --- Helper matchers ---------------------------------------------------------

def contains(pattern, text):
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def startswith_any(prefixes, text):
    text_low = text.lower().strip()
    return any(text_low.startswith(p) for p in prefixes)

# --- Pronoun detection --------------------------------------------------------

def is_about_user(text):
    return any([
        contains(r"\bi\b", text),
        contains(r"\bmy\b", text),
        contains(r"\bme\b", text),
        contains(r"\bpinky\b", text),
    ])

def is_about_ai(text):
    return any([
        contains(r"\byou\b", text),
        contains(r"\byour\b", text),
        contains(r"\byou're\b", text),
        contains(r"\bvmsgk\b", text),
        contains(r"\bvm\b", text),
        contains(r"virtual mesugaki", text),
    ])

# --- Category detection -------------------------------------------------------

def detect_preference(text):
    return contains(r"\blike\b", text) or contains(r"\blove\b", text) or contains(r"favorite", text)

def detect_fact(text):
    return contains(r"\bis\b", text) or contains(r"\bare\b", text)

def detect_goal(text):
    return any([
        contains("want to", text),
        contains("plan to", text),
        contains("going to", text),
        contains("hope to", text),
        contains("goal", text),
    ])


# --- Main parser -------------------------------------------------------------

def parse_memory_entry(text):
    text = text.strip()
    if not text:
        return None

    # 1 — Decide WHO the memory refers to
    about_user = is_about_user(text)
    about_ai   = is_about_ai(text)

    if about_user:
        who = "Pinky"
    elif about_ai:
        who = "core_identity"
    else:
        who = "general"

    # 2 — Determine category
    if detect_preference(text):
        return (who, "likes", text)

    if detect_goal(text):
        return (who, "goals", text)

    if detect_fact(text):
        return (who, "facts", text)

    # 3 — fallback
    return None