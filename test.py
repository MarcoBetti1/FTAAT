import tiktoken
import itertools
import random
import json

def generate_alpha_tokens(N: int, model: str = "gpt-3.5-turbo", alphabet: str = "abcdefghijklmnopqrstuvwxyz") -> set:
    """Generate N tokens composed only of `alphabet` characters."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = set()

    # Brute-force short tokens first (lengths 1-3)
    for length in range(1, 6):
        for chars in itertools.product(alphabet, repeat=length):
            candidate = "".join(chars)
            token_ids = encoding.encode(candidate)
            if len(token_ids) == 1:
                token_str = encoding.decode_single_token_bytes(token_ids[0]).decode("utf-8", errors="ignore")
                if token_str.isalpha() and token_str == candidate:
                    tokens.add(token_str)
                    if len(tokens) >= N:
                        return tokens

    # Random sampling if more tokens needed
    while len(tokens) < N:
        length = random.randint(1, 8)
        candidate = "".join(random.choice(alphabet) for _ in range(length))
        token_ids = encoding.encode(candidate)
        if len(token_ids) == 1:
            token_str = encoding.decode_single_token_bytes(token_ids[0]).decode("utf-8", errors="ignore")
            if token_str.isalpha() and token_str == candidate:
                tokens.add(token_str)
    
    return tokens

def save_tokens(tokens: set, filename: str = "tokens.json"):
    """Save tokens to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(list(tokens), f)  # Convert set to list for JSON

# Example: Generate 100 tokens and save
if __name__ == "__main__":
    tokens = generate_alpha_tokens(N=10000)
    save_tokens(tokens, "data/tokens/alpha_tokens.json")
    print(f"Saved {len(tokens)} tokens to alpha_tokens.json")