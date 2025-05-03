import random

def build_prompt_for_all_keys(facts_list):
    """
    - Lists all facts in the prompt
    - Then lists all keys in random order, requesting the correct values
    in that same order.
    Returns:
       (prompt_str, question_keys_in_order)
    """
    # Combine fact lines in a single block
    facts_text = "\n".join(fact_line for (fact_line, _, _) in facts_list)

    # Extract keys in a random order
    all_keys = [key for (_, key, _) in facts_list]
    random.shuffle(all_keys)

    questions_text = "\n".join(k for k in all_keys)

    prompt = (
        "Below are some arbitrary assignments of Key => Value:\n\n"
        f"{facts_text}\n\n"
        "Your task is to provide the correct Values for each of the following Keys in the exact same order they are listed. Provide only the values, one per line, and do not include any other text.\n\n"
        f"{questions_text}\n\n"
        "Give only the correct answers and nothing else.\n\n"
    )
    return prompt, all_keys