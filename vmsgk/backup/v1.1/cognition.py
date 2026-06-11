import subprocess
import json

COGNITION_PROMPT = """
You are an internal reasoning module for an AI assistant named vmsgk.
You NEVER talk to the user.

Analyze the user's message and output ONLY valid JSON.

Decide:
- intent: "question", "statement", "correction", "command", or "chitchat"
- subject: "Pinky", "vmsgk", or "unknown"
- memory_type: "preference", "fact", "goal", or null
- memory_value: a short normalized sentence, or null
- should_store: true or false
- confidence: number from 0.0 to 1.0

Rules:
- Questions should NOT be stored.
- Speculation should NOT be stored.
- Only store stable personal information.
- If the user asks about memory, do NOT store.

Output JSON ONLY.
"""

def think(user_text):
    prompt = COGNITION_PROMPT + "\nUser: " + user_text + "\nJSON:"

    result = subprocess.run(
        ["ollama", "run", "llama3.2"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )

    try:
        return json.loads(result.stdout.strip())
    except:
        return None