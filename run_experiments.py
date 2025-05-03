"""
Run the benchmark with any provider that implements llm_providers.base.LLMProvider.
"""
from datetime import datetime
from pathlib import Path
import json, importlib

from scripts.fact_gen       import generate_facts_k_tokens
from scripts.build_prompt   import build_prompt_for_all_keys
from scripts.eval           import evaluate_token_sequences
from token_utils            import build_single_token_vocab

# -------------- generic grading, unchanged except for tokenizer inject ------
def grade_response(response_text, question_keys_in_order, key_value_dict, *,
                   tokenizer):
    major_format_flaw = response_text[0].isalpha() and not response_text[-1].isalpha()
    
    # expected + student answers
    correct_seqs = [key_value_dict[k] for k in question_keys_in_order]
    response_seqs = [ln.strip() for ln in response_text.splitlines() if ln.strip()]

    expected_tokens = sum(tokenizer(seq) for seq in correct_seqs)
    response_tokens = sum(tokenizer(seq) for seq in response_seqs)

    seq_acc, tok_acc = evaluate_token_sequences(response_seqs, correct_seqs)
    return (seq_acc, tok_acc), major_format_flaw, expected_tokens, response_tokens
# ---------------------------------------------------------------------------

def run_experiments(provider_module: str|None = None,
                    facts_list_sizes=[3, 6],
                    token_sizes=[2, 3],
                    trials=1,
                    output_root="results"):
    """
    provider_module – dotted import path, e.g. 'llm_providers.deepseek_llm.DeepSeekProvider'
    """
    # instantiate backend
    mod_path, cls_name = provider_module.rsplit(".", 1)
    ProviderClass = getattr(importlib.import_module(mod_path), cls_name)
    llm = ProviderClass()

    vocab = build_single_token_vocab(llm)
    Path(output_root).mkdir(parents=True, exist_ok=True)

    for num_facts in facts_list_sizes:
        for k in token_sizes:
            timestamp   = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
            file_id     = f"{llm.provider_id}_{num_facts}f_{k}t_{timestamp}"
            out_file    = Path(output_root) / f"{file_id}.json"

            result_group = {
                "id": file_id,
                "provider": llm.provider_id,
                "model": llm.model_name,
                "num_facts": num_facts,
                "k": k,
                "trials": []
            }

            for trial in range(trials):
                facts, kv = generate_facts_k_tokens(num_facts, k, vocab)
                prompt, keys = build_prompt_for_all_keys(facts, k=k)

                try:
                    answer = llm.query(prompt, temperature=0.0)
                except Exception as e:
                    answer = f"ERROR: {e}"

                correct_text = "\n".join(kv[k] for k in keys)

                (seq_acc, tok_acc), flaw, exp_tok, resp_tok = grade_response(
                    answer, keys, kv, tokenizer=llm.count_tokens
                )

                result_group["trials"].append({
                    "trial": trial,
                    "sequence_accuracy": seq_acc,
                    "token_accuracy": tok_acc,
                    "major_format_flaw": flaw,
                    "prompt_text": prompt,
                    "response_text": answer,
                    "response_token_count": resp_tok,
                    "expected_response_text": correct_text,
                    "expected_token_count": exp_tok,
                })

            with out_file.open("w", encoding="utf-8") as f:
                json.dump(result_group, f, indent=2)

    return f"✅ Finished. Results saved under {output_root}/"
