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

    # We'll list them as "1) <key>" etc. 
    questions_text = "\n".join(f"{i+1}) {k}" for i, k in enumerate(all_keys))

    prompt = (
        "Below are some arbitrary assignments of Key => Value:\n\n"
        f"{facts_text}\n\n"
        "Your task is to provide the correct Values for each of the following Keys, "
        "in the exact same order they are listed:\n\n"
        f"{questions_text}\n\n"
        "Answer with one value per line, matching the order of the keys above."
    )
    return prompt, all_keys