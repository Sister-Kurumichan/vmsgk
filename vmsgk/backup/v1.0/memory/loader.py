import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # default structure if file missing/invalid
        return {
            "Pinky": {"likes": [], "goals": [], "facts": [], "notes": []},
            "core_identity": {"likes": [], "facts": [], "notes": []},
            "general": {"notes": []}
        }

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)