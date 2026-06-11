def store_memory(memory, subject, mem_type, value):
    memory.setdefault(subject, {})
    memory[subject].setdefault(mem_type, [])

    if value not in memory[subject][mem_type]:
        memory[subject][mem_type].append(value)
        return True

    return False


def update_memory(memory, subject, mem_type, old_value, new_value):
    if subject not in memory:
        return False

    if mem_type not in memory[subject]:
        return False

    try:
        idx = memory[subject][mem_type].index(old_value)
        memory[subject][mem_type][idx] = new_value
        return True
    except ValueError:
        return False