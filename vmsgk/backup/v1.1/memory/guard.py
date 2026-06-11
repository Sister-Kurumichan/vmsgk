def memory_guard(entry, memory):
    """
    entry is expected to contain:
        subject
        memory_type
        memory_value
        confidence
        intent
        should_store
    """

    # Hard stop: questions never store memory
    if entry.get("intent") == "question":
        return "ignore"

    # Confidence too low
    if entry.get("confidence", 0) < 0.6:
        return "ignore"

    subject = entry["subject"]
    mem_type = entry["memory_type"]
    value = entry["memory_value"]

    existing = memory.get(subject, {}).get(mem_type, [])

    # Already known
    if value in existing:
        return "ignore"

    # Possible contradiction
    if existing and mem_type == "facts":
        return "update"

    return "store"