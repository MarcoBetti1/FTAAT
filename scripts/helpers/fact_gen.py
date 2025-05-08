import random


def generate_unique_sequence(k: int, single_token_pool, used_sequences: set) -> str:
    """
    Randomly pick `k` single tokens from `single_token_pool`,
    join them with '|', and ensure it's never been used.
    """
    max_tries = 5000
    for _ in range(max_tries):
        chosen_tokens = random.sample(single_token_pool, k=k)
        seq = "|".join(chosen_tokens)
        if seq not in used_sequences:
            used_sequences.add(seq)
            return seq
    raise ValueError(f"Could not find a new {k}-token sequence after {max_tries} attempts.")

def generate_facts_k_tokens(num_facts: int, k: int, single_token_pool):
    """
    Generate `num_facts` lines, each of form:
        "Key: <k-token-seq> => Value: <k-token-seq>"
    where no key or value is repeated.
    Returns:
      facts_list: list of (fact_line, key_string, value_string)
      key_value_dict: mapping key_string -> value_string
    """
    used_sequences = set()
    facts_list = []
    key_value_dict = {}

    for _ in range(num_facts):
        key_seq = generate_unique_sequence(k, single_token_pool, used_sequences)
        val_seq = generate_unique_sequence(k, single_token_pool, used_sequences)
        fact_line = f"{key_seq} => {val_seq}"
        facts_list.append((fact_line, key_seq, val_seq))
        key_value_dict[key_seq] = val_seq

    return facts_list, key_value_dict