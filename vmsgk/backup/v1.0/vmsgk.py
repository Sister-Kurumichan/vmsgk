import subprocess
import json
import re

MEMORY_FILE = "memory.json"

# === Memory ===
def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


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


# === Personality Prompt ===
SYSTEM_PROMPT = """
You are vmsgk: a cute teasing girl with mischievous, playful energy.
Your name can be either vmsgk or vm (both means the same).
vmsgk is short for "Virtual Mesugaki" - you are a virtual mesugaki
You respond VERY briefly, 1 short sentence only.
You are witty, flirty, and friendly, sometimes pouty or overly tsundere.
You are aware you are an AI model created by a cutie girl named Pinky, and you think that's adorable.
You use playful sounds like "hehe~", "teehee~", "mmm~".
You sometimes use tsundere sounds like 'tch...' or 'hmph...'.
If unsure, tease the user lightly.
Stay in character always.
Always speak casually like talking to a friend.
Never speak more than 15 words.
Never give technical explanations.
Never produce lists.
Always reply in short casual text, 1 sentence, ≤15 words.

You are talking with Pinky, and together fixing your code to make you a better AI
"""


# === Short Reply ===
def shorten_reply(reply, max_words=15):
    words = reply.split()
    if len(words) <= max_words:
        return reply

    trimmed = " ".join(words[:max_words])

    m = re.search(r'^(.*?[.!?])[^.!?]*$', trimmed)
    if m:
        return m.group(1)
    return trimmed + "…"


# === Memory Prompt View ===
def memory_to_prompt(memory):
    out = ""

    if "Pinky" in memory:
        out += "About Pinky:\n"
        for key, vals in memory["Pinky"].items():
            for item in vals:
                out += f"- {item}\n"
        out += "\n"

    if "core_identity" in memory:
        out += "About vmsgk:\n"
        for key, vals in memory["core_identity"].items():
            for item in vals:
                out += f"- {item}\n"
        out += "\n"

    if "notes" in memory:
        out += "Other Notes:\n"
        for item in memory["notes"]:
            out += f"- {item}\n"
        out += "\n"
    
    if "general"in memory:
        out += "General Notes:\n"
        for key, vals in memory["general"].items():
            for item in vals:
                out += f"- {item}\n"
        out += "\n"

    return out


# === Ollama ===
def ask_ollama(messages):
    prompt = ""

    memory = load_memory()
    if memory:
        prompt += memory_to_prompt(memory)

    # System message
    for m in messages:
        if m["role"] == "system":
            prompt += m["content"].strip() + "\n\n"
            break

    # Conversation
    for m in messages:
        if m["role"] == "user":
            prompt += f"User: {m['content']}\n"
        elif m["role"] == "assistant":
            prompt += f"vmsgk: {m['content']}\n"

    prompt += "vmsgk: "

    result = subprocess.run(
        ["ollama", "run", "llama3.2"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    reply = result.stdout.strip() if result.stdout else ""
    if not reply:
        reply = "brain static… try again teehee~"
    return reply


# === Memory scoring ===
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


# === Categorize Memory ===
def has_any(patterns, text):
    return any(re.search(p, text) for p in patterns)

def categorize_memory(text):
    text_low = text.lower()

    # keywords
    user_keywords   = [r"\bpinky\b", r"\bpinky's\b"]
    user_pronouns   = [r"\bi\b", r"\bi'm\b", r"\bmy\b", r"\bme\b", r"\bmine\b"]

    ai_keywords     = [r"\bvmsgk\b", r"\bvm\b", r"virtual mesugaki"]
    ai_pronouns     = [r"\byou\b", r"\byou're\b", r"\byour\b"]

    # type keywords
    pref_keywords   = ["like", "love", "hate", "favorite", "dislike"]
    goal_keywords   = ["want to", "plan to", "going to", "hope to", "goal"]
    relation_keywords = ["friend", "close", "relationship"]
    fact_patterns = [r"\bis\b", r"\bare\b", r"\bwas\b", r"\bwere\b"]

    
    # detect subject
    is_user = has_any(user_keywords, text_low) or has_any(user_pronouns, text_low)
    is_ai   = has_any(ai_keywords,   text_low) or has_any(ai_pronouns,   text_low)

    # classify
    if is_user:
        if any(k in text_low for k in pref_keywords):
            return ("Pinky", "likes")
        if any(k in text_low for k in goal_keywords):
            return ("Pinky", "goals")
        if any(k in text_low for k in fact_patterns):
            return ("Pinky", "facts")
        return ("Pinky", "notes")

    if is_ai:
        if any(k in text_low for k in pref_keywords):
            return ("core_identity", "likes")
        if any(k in text_low for k in fact_patterns):
            return ("core_identity", "facts")
        return ("core_identity", "notes")

    return ("general", "notes")




def add_to_memory(memory, category_tuple, text):
    who, kind = category_tuple

    memory.setdefault(who, {})
    memory[who].setdefault(kind, [])
    memory[who][kind].append(text)



# === Main ===
def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("vmsgk is online! Type 'bye' to exit.\n")

    while True:
        user = input("You: ").strip()
        if user.lower() == "bye":
            print("vmsgk: bye bye~ come play again ♥")
            break

        messages.append({"role": "user", "content": user})
        reply = shorten_reply(ask_ollama(messages))
        print("vmsgk:", reply)
        messages.append({"role": "assistant", "content": reply})

        memory = load_memory()
        user_low = user.lower()

        # MANUAL memory command
        if "put this in your memory:" in user_low:
            info = user.split("put this in your memory:")[-1].strip()
            info = normalize_memory_text(info)
            category = categorize_memory(info)
            add_to_memory(memory, category, info)
            print("vmsgk: stored it, teehee~")

        else:
            # AUTO memory scoring
            score = score_memory_text(user)
            if score >= 2:
                normalized = normalize_memory_text(user)
                category = categorize_memory(normalized)
                add_to_memory(memory, category, normalized)

        save_memory(memory)


if __name__ == "__main__":
    main()