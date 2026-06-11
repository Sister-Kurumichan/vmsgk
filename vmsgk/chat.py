import requests
import json
import os
import re

USER_NAME = "Pinky"
ASSISTANT_NAME = "vmsgk"

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
    text = "These are things you know about Pinky:\n\n"

    for m in memory.get("pinky_memories", []):
        text += f"- {m}\n"

    text += "\nShared memories with Pinky:\n"

    for m in memory.get("shared_memories", []):
        text += f"- {m}\n"

    return text


def get_reply(user_input):
    persona_prompt = build_persona_prompt(persona)
    memory_prompt = build_memory_prompt(memory)

    global messages
    messages.append({
        "role": "user",
        "name": "Pinky",
        "content": user_input
    })

    anchor = {
        "role": "system",
        "content": f"""
        You are {ASSISTANT_NAME}.

        User identity: {USER_NAME}
        Assistant identity: {ASSISTANT_NAME}

        STRICT RULES:
        - "I / me / my" ALWAYS refers to {ASSISTANT_NAME}
        - "you / your" ALWAYS refers to {USER_NAME}
        - NEVER confuse user and assistant identities
        - If user asks "who am I", answer: {USER_NAME}
        - If user asks "your name", answer: {ASSISTANT_NAME}

        PERSONA:
        {persona_prompt}

        MEMORY:
        {memory_prompt}

        You are a teasing mesugaki companion talking to Pinky.
        Keep tone casual, smug, playful.
        """
    }

    context = [
        {
            "role": m["role"],
            "content": f"{m.get('name', '')}: {m['content']}"
        }
        for m in messages[-10:]
    ]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "vmsgk",
            "messages": [anchor] + context,
            "stream": False,
            "options": {
                "temperature": 0.9,
                "num_predict": 80
            }
        }
    )

    data = response.json()
    reply = data["message"]["content"].strip()

    # fix identity confusion
    def fix_identity(reply):
        reply = reply.replace("my name is vmsgk", "my name is vmsgk")
        reply = reply.replace("I am Pinky", "you are Pinky")
        return reply

    reply = fix_identity(reply)

    # cut
    sentences = re.split(r'(?<=[.!?~])\s+', reply)
    if len(reply) < 80:
        reply = ' '.join(sentences[:2])
    else:
        reply = ' '.join(sentences[:3])

    messages.append({
        "role": "assistant",
        "name": "vmsgk",
        "content": reply
    })
    del messages[:-10]

    # save memory
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

    return reply