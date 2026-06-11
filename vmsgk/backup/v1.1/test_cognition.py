from cognition import think

print("Cognition test — type 'exit' to stop\n")

while True:
    text = input("Test> ").strip()
    if text.lower() == "exit":
        break

    result = think(text)
    print(result)