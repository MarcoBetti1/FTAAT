def grade_response(response_text: str, question_keys_in_order: list, key_value_dict: dict):
    """
    Parses the GPT response line-by-line. We expect it to list the values
    in the same order as question_keys_in_order.

    Returns:
      accuracy: fraction of lines that match exactly
      num_matches: how many lines matched 
      total: how many lines we expected
      mismatch_details: list of (expected, got) for each mismatch
    """
    # Split lines, strip whitespace
    lines = [l.strip() for l in response_text.split("\n") if l.strip()]
    # lines now might contain numbering, e.g. "1) Pk am ub" or just "Pk am ub".

    expected_count = len(question_keys_in_order)
    num_matches = 0
    mismatch_details = []

    # We'll iterate over min(len(lines), expected_count) 
    for i in range(expected_count):
        expected_value = key_value_dict[question_keys_in_order[i]]

        if i < len(lines):

            maybe_split = lines[i].split(")", 1)
            if len(maybe_split) == 2 and maybe_split[0].isdigit():
                candidate_answer = maybe_split[1].strip()  # e.g. "Pk am ub"
            else:
                candidate_answer = lines[i]

            if candidate_answer == expected_value:
                num_matches += 1
            else:
                mismatch_details.append((expected_value, candidate_answer))
        else:
            # We have fewer lines in the response than we expected
            mismatch_details.append((expected_value, "MISSING_LINE"))

    accuracy = num_matches / expected_count

    return accuracy, num_matches, expected_count, mismatch_details
