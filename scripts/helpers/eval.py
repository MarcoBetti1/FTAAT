def evaluate_token_sequences(response_seqs: list[str], correct_seqs: list[str]):
    """
    Compares tokenized sequences using '|' separator.

    Returns:
        sequence_accuracy: % of full sequences that match exactly
        token_accuracy: % of individual tokens that match
    """
    total_sequences = min(len(response_seqs), len(correct_seqs))
    total_tokens = 0
    matched_tokens = 0
    matched_sequences = 0

    for resp_line, corr_line in zip(response_seqs, correct_seqs):
        resp_tokens = resp_line.strip().split("|")
        corr_tokens = corr_line.strip().split("|")

        if resp_tokens == corr_tokens:
            matched_sequences += 1

        for r, c in zip(resp_tokens, corr_tokens):
            if r == c:
                matched_tokens += 1

        total_tokens += min(len(resp_tokens), len(corr_tokens))

    sequence_accuracy = matched_sequences / total_sequences if total_sequences else 0
    token_accuracy = matched_tokens / total_tokens if total_tokens else 0

    return sequence_accuracy, token_accuracy