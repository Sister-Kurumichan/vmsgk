import subprocess
from memory.loader import load_memory, save_memory
from memory.normalize import normalize_memory_text
from memory.parser import parse_memory_entry
import re

# pt
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

def shorten_reply(reply, max_words=15):
    words = reply.split()
    if len(words) <= max_words:
        return reply
    trimmed = " ".join(words[:max_words])
    m = re.search(r'^(.*?[.!?])[^.!?]*$', trimmed)
    if m:
        return m.group(1)
    return trimmed + "…"

# memory_to_prompt: lightweight view
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
    if "general" in memory:
        out += "General Notes:\n"
        for key, vals in memory["general"].items():
            for item in vals:
                out += f"- {item}\n"
        out += "\n"
    return out

def ask_ollama(messages):
    prompt = ""
    memory = load_memory()
    if memory:
        prompt += memory_to_prompt(memory)

    for m in messages:
        if m["role"] == "system":
            prompt += m["content"].strip() + "\n\n"
            break
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

def add_to_memory(memory, category_tuple, text):
    who, kind = category_tuple
    memory.setdefault(who, {})
    memory[who].setdefault(kind, [])
    memory[who][kind].append(text)

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

        parsed = parse_memory_entry(user)

        if parsed:
            subject, mem_type, raw_value = parsed
            value = normalize_memory_text(raw_value)

            memory.setdefault(subject, {})
            memory[subject].setdefault(mem_type, [])
            if value not in memory[subject][mem_type]:
                memory[subject][mem_type].append(value)
                print("vmsgk: stored it, teehee~")
            else:
                print("vmsgk: I already know that, ehehe~")

        save_memory(memory)

if __name__ == "__main__":
    main()