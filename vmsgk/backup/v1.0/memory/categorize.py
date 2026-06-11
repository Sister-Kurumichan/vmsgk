import re

def has_any(patterns, text):
    return any(re.search(p, text) for p in patterns)

def score_memory_text(text):
    text_low = text.lower()
    score = 0

    if any(x in text_low for x in ["i like", "i love", "favorite", "you like"]):
        score += 2

    if any(x in text_low for x in ["you're", "you are"]):
        score += 2

    if any(x in text_low for x in ["my name is", "call me", "i am"]):
        score += 2

    if any(x in text_low for x in ["working on", "my project", "goal", "currently making"]):
        score += 3

    if "remember" in text_low:
        score += 2

    if any(x in text_low for x in ["important", "very important"]):
        score += 1

    return score

def categorize_memory(text):
    text_low = text.lower()

    # keywords
    user_keywords   = [r"\bpinky\b", r"\bpinky's\b"]
    user_pronouns   = [r"\bi\b", r"\bi'm\b", r"\bmy\b", r"\bme\b", r"\bmine\b"]

    ai_keywords     = [r"\bvmsgk\b", r"\bvm\b", r"virtual mesugaki"]
    ai_pronouns     = [r"\byou\b", r"\byou're\b", r"\byour\b"]

    # type keywords (regex-friendly)
    pref_patterns = [r"\blike\b", r"\bloves?\b", r"\bhate\b", r"\bfavorite\b", r"\bdislike\b"]
    goal_patterns = [r"\bwant to\b", r"\bplan to\b", r"\bgoing to\b", r"\bhope to\b", r"\bgoal\b"]
    fact_patterns = [r"\bis\b", r"\bare\b", r"\bwas\b", r"\bwere\b"]

    is_user = has_any(user_keywords, text_low) or has_any(user_pronouns, text_low)
    is_ai   = has_any(ai_keywords, text_low)   or has_any(ai_pronouns, text_low)

    if is_user:
        if any(re.search(p, text_low) for p in pref_patterns):
            return ("Pinky", "likes")
        if any(re.search(p, text_low) for p in goal_patterns):
            return ("Pinky", "goals")
        if any(re.search(p, text_low) for p in fact_patterns):
            return ("Pinky", "facts")
        return ("Pinky", "notes")

    if is_ai:
        if any(re.search(p, text_low) for p in pref_patterns):
            return ("core_identity", "likes")
        if any(re.search(p, text_low) for p in fact_patterns):
            return ("core_identity", "facts")
        return ("core_identity", "notes")

    return ("general", "notes")