import json, functools
from typing import Callable, Set

# Cache prevents re-reading JSON every call
@functools.lru_cache(maxsize=None)
def load_token_set(path: str) -> Set[str]:
    with open(path, "r") as f:
        return set(json.load(f))

def build_single_token_vocab(provider) -> list[str]:
    """
    Returns a *list* (not set) of tokens guaranteed to be single tokens
    for this provider. You said you'll keep these files in sync.
    """
    token_set = load_token_set(provider.token_set_path)
    good = [tok for tok in token_set if provider.count_tokens(tok) == 1]
    if len(good) != len(token_set):
        bad = set(token_set) - set(good)
        raise ValueError(
            f"{provider.provider_id}: {len(bad)} entries are not single tokens"
        )
    return good
