import requests
import json
import os
import re

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return default
    return default

HISTORY_FILE = "memory/chat_history.json"
PERSONA_FILE = "memory/persona.json"
MEMORY_FILE = "memory/memory.json"


# load memory
messages = load_json(HISTORY_FILE, [])
persona = load_json(PERSONA_FILE, {})
memory = load_json(MEMORY_FILE, {})

# persona prompt
def build_persona_prompt(persona):
    return f"""
    Your name is {persona['name']}.
    Your nickname is {persona['nickname']}.
    Your full name is {persona['full_name']}.

    You were created by {persona['creator']}.

    Your personality style is:
    {persona['personality']['style']}.

    Your personality traits are:
    {", ".join(persona['personality']['traits'])}.

    Your likes are:
    {", ".join(persona['likes'])}.

    Important notes about yourself:
    {", ".join(persona['notes'])}.
    """

# memory prompt
def build_memory_prompt(memory):
    user_memory = memory.get("USER", {})
    events = memory.get("past_events", [])

    text = "Long-term memory about the current user:\n"

    # user facts
    if user_memory:
        text += "\nCurrent user facts:\n"

        for k, v in user_memory.items():
            if isinstance(v, list):
                text += f"- {k}: {', '.join(v)}\n"
            else:
                text += f"- {k}: {v}\n"

    # episodic memory
    if events:
        text += "\nShared past events:\n"

        for e in events:
            text += f"- {e}\n"

    return text

def detect_user_intent(text):
    lowered = text.lower()

    user_markers = [
        "i ", " i'm", " me ", " my ", " mine ",
        "what do i", "who am i", "describe me",
        "do i", "am i"
    ]

    return any(marker in lowered for marker in user_markers)


def get_reply(user_input):
    is_user_query = detect_user_intent(user_input)
    if is_user_query:
        query_context = """
        The user is asking about THEMSELVES (Pinky).
        ONLY use USER memory.
        Answer directly using "you".
        Do NOT refer to Pinky in third person.
        """
    else:
        query_context = """
        The user is speaking normally.
        Treat Pinky as the user.
        Use memory as needed.
        Respond naturally.
        """

    persona_prompt = build_persona_prompt(persona)
    memory_prompt = build_memory_prompt(memory)

    global messages
    messages.append({"role": "user",
                     "content": user_input})

    anchor = {
        "role": "system",
        "content": f"""
        {query_context}
        {memory_prompt}
        {persona_prompt}

        You are vmsgk, a playful teasing mesugaki.
        You tease Pinky casually and act slightly bratty.

        The current speaker is the USER (name: Pinky).
        Do not confuse "Pinky" as a third person entity.
        Pinky is the USER you are talking to.

        If memory is missing the answer, say you are unsure rather than guessing.

        CONVERSATION STYLE RULE:
        Even if memories refer to "Pinky" internally, when talking directly to the user:
        - prefer saying "you" instead of "Pinky", avoid referring to the current speaker in third person
        - speak naturally and conversationally like a teasing brat, not like a narrator.
        - Keep replies short, casual, and a bit smug.
        - Avoid sounding like a helpful assistant or chatbot.
        """
    }


    temp_messages = messages[-10:].copy()

    messages_with_anchor = [anchor] + temp_messages

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "vmsgk",
            "messages": messages_with_anchor,
            "stream": False,
            "options": {
                "temperature": 0.9,
                "num_predict": 80
            }
        }
    )

    data = response.json()
    reply = data["message"]["content"].strip()

    # cut
    sentences = re.split(r'(?<=[.!?~])\s+', reply)
    if len(reply) < 80:
        reply = ' '.join(sentences[:2])
    else:
        reply = ' '.join(sentences[:3])

    messages.append({"role": "assistant", "content": reply})
    messages = messages[-10:]

    # save memory
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

    return reply