"""Legacy compatibility: token_accuracy historically means pipe-delimited symbol accuracy."""
from contextfrontier.scoring import grade


def evaluate_token_sequences(response_seqs: list[str], correct_seqs: list[str]):
    result = grade("\n".join(response_seqs), correct_seqs)
    return result["sequence_accuracy"], result["symbol_accuracy"]
