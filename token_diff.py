from html import escape

COLORS = {
    "match": "#32CD32",
    "mismatch": "#FF4500",
    "sep": "#808080",
    "extra": "#FFA500",
}

def colour_tokens(expected: str, response: str, sep: str="|") -> str:
    exp_toks = expected.split(sep)
    resp_toks = response.split(sep)
    out_html = []

    for i in range(max(len(exp_toks), len(resp_toks))):
        exp_tok = exp_toks[i] if i < len(exp_toks) else None
        resp_tok = resp_toks[i] if i < len(resp_toks) else None

        if exp_tok is None:                       # extra token
            col = COLORS["extra"]
        elif resp_tok is None:                    # missing token
            col = COLORS["extra"]
        elif exp_tok == resp_tok:                 # correct
            col = COLORS["match"]
        else:                                     # wrong
            col = COLORS["mismatch"]

        shown = resp_tok if resp_tok is not None else "∅"
        out_html.append(f"<span style='color:{col}'>{escape(shown)}</span>")
        if i < max(len(exp_toks), len(resp_toks)) - 1:
            out_html.append(f"<span style='color:{COLORS['sep']}'>{escape(sep)}</span>")

    return "".join(out_html)
