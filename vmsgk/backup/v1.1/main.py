# main.py — cognition test loop

from cognition import think
from semantic import extract_semantics
from memory.loader import load_memory, save_memory
from memory.guard import memory_guard
from memory.store import store_memory

def main():
    print("vmsgk cognition test online. Type 'bye' to exit.\n")

    memory = load_memory()

    while True:
        user = input("You: ").strip()
        if user.lower() == "bye":
            break

        # 1. Cognition pass
        cog = think(user)

        print("DEBUG cognition:", cog)

        # 2. Decide memory storage
        if memory_guard(cog):
            subject = extract_semantics(cog)
            store_memory(memory, subject, cog)
            save_memory(memory)
            print("DEBUG memory: stored")

        else:
            print("DEBUG memory: ignored")

        # 3. Placeholder reply (NO personality yet)
        print("vmsgk: ...thinking...")

    print("\nTest ended.")

if __name__ == "__main__":
    main()
