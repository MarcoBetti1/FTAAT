import json, importlib
from datetime import datetime
from pathlib import Path
from time import perf_counter
import os
import uuid
import time

from .build_prompt           import build_prompt_for_all_keys
from .helpers.eval           import evaluate_token_sequences
from .helpers.token_utils    import build_single_token_vocab
from .helpers.fact_gen       import generate_facts_k_tokens

def staircase_schedule(n0: int, k0: int,
                       n_max: int, k_max: int,
                       factor: int = 2):
    """Yield (N,K): (n0,k0) → (2n0,2k0) → ... until bounds exceeded."""
    n, k = n0, k0
    while n <= n_max and k <= k_max:
        yield n, k
        n *= factor
        k *= factor

def grade_response(response_text, question_keys_in_order, key_value_dict, *, tokenizer):
    ### 
    correct_seqs = [key_value_dict[k] for k in question_keys_in_order]
    response_seqs = [ln.strip() for ln in response_text.splitlines() if ln.strip()]

    seen = set()
    for seq in response_seqs:
        if seq in seen:
            print(f"repeated sequence detected: {seq!r}")
            major_format_flaw = True
            break
        seen.add(seq)

    expected_tokens = sum(tokenizer(seq) for seq in correct_seqs)
    response_tokens = sum(tokenizer(seq) for seq in response_seqs)

    major_format_flaw = False

    diff = expected_tokens - response_tokens
    if diff > max(3, expected_tokens * 0.25):
        major_format_flaw = True

    if not response_text[0].isalpha() or not (response_text[-1].isalpha() or response_text[-1] == '|'):
        print("first or last char not a-z or | at end")
        major_format_flaw = True

    if not major_format_flaw:
        seq_acc, tok_acc = evaluate_token_sequences(response_seqs, correct_seqs)
    else:
        print("major format flaw skipping eval")
        seq_acc, tok_acc = 0.0, 0.0
    return (seq_acc, tok_acc), major_format_flaw, expected_tokens, response_tokens

def run_experiments(
    provider_module: str,
    facts_list_sizes=[3, 6],
    token_sizes=[2, 3],
    trials=1,
    output_root="results",
    prompt_id="default_prompt",  
    verbose=True,
    adaptive=False,
    early_abort=False,
    timeout_sec=60,
    max_tok_mult=2,
    batch_size=20
):
    mod_path, cls_name = provider_module.rsplit(".", 1)
    ProviderClass      = getattr(importlib.import_module(mod_path), cls_name)
    llm                = ProviderClass()
    vocab              = build_single_token_vocab(llm)

    safe_prompt_id = prompt_id.replace(" ", "_").replace("/", "_")
    base_dir = Path(output_root) / llm.provider_id
    base_dir.mkdir(parents=True, exist_ok=True)

    existing_pairs = set()
    for f in base_dir.glob(f"{llm.model_name}_*N_*K_*.json"):
        try:
            parts = f.stem.split('_')
            n = int(parts[1][:-1])
            k = int(parts[2][:-1])
            existing_pairs.add((n, k))
        except (IndexError, ValueError):
            continue

    if adaptive:
        n0, k0  = min(facts_list_sizes), min(token_sizes)
        pairs   = staircase_schedule(n0, k0, max(facts_list_sizes), max(token_sizes))
    else:
        all_pairs = [(n, k) for n in facts_list_sizes for k in token_sizes]
        pairs     = [p for p in all_pairs if p not in existing_pairs]

    if not pairs:
        print(f"✅ All experiments already completed in {base_dir}/")
        return

    use_batch = hasattr(llm, "queue_batch_request") and hasattr(llm, "submit_batch")
    pending_batch = []  # store (n, k, t, prompt, meta) until we flush

    for n, k in pairs:
        for t in range(trials):
            facts, kv    = generate_facts_k_tokens(n, k, vocab)
            prompt, keys = build_prompt_for_all_keys(facts, k=k)
            cap_tok      = min(n * k + 100, llm.max_tokens)

            if use_batch:
                meta = {
                    "trial": t,
                    "num_facts": n,
                    "k": k,
                    "keys": keys,
                    "expected": kv,
                    "prompt": prompt,
                }
                llm.queue_batch_request(prompt, meta, max_tokens=cap_tok)
                pending_batch.append((n, k, t, prompt, meta))

                # Flush if batch limit reached
                if len(pending_batch) >= batch_size:
                    flush_batch(llm, pending_batch, base_dir, prompt_id)
                    pending_batch.clear()

            else:
                if verbose:
                    print(f"[N={n} K={k} trial={t}]")

                prompt_tok   = llm.count_tokens(prompt)
                expected_tok = n * k

                try:
                    t0 = perf_counter()
                    answer = llm.query(
                        prompt,
                        temperature=0.0,
                        max_tokens=cap_tok,
                        timeout=timeout_sec
                    )
                    latency_ms = (perf_counter() - t0) * 1_000
                except Exception as e:
                    answer, latency_ms = f"ERROR: {e}", None
                    if verbose: print("⚠️", e)

                answer = "\n".join(line.strip() for line in answer.splitlines() if line.strip())
                correct_text = "\n".join(kv[k] for k in keys)

                (seq_acc, tok_acc), flaw, exp_ct, resp_ct = grade_response(
                    answer, keys, kv, tokenizer=llm.count_tokens
                )

                file_id = f"{llm.model_name}_{n}N_{k}K_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
                out_f   = base_dir / f"{file_id}.json"
                grp = {
                    "id": file_id,
                    "prompt_id": prompt_id,
                    "provider": llm.provider_id,
                    "model": llm.model_name,
                    "num_facts": n,
                    "k": k,
                    "trials": [{
                        "trial": t,
                        "sequence_accuracy": seq_acc,
                        "token_accuracy": tok_acc,
                        "major_format_flaw": flaw,
                        "response_time_ms": latency_ms,
                        "prompt_tokens": prompt_tok,
                        "prompt_text": prompt,
                        "response_text": answer,
                        "response_token_count": resp_ct,
                        "expected_response_text": correct_text,
                        "expected_token_count": exp_ct,
                    }]
                }
                with out_f.open("w", encoding="utf-8") as f:
                    json.dump(grp, f, indent=2)

                if early_abort and (seq_acc < 0.5 or flaw):
                    if verbose: print("⏹️ early abort for this (N,K)")
                    break

    # Final batch flush
    if use_batch and pending_batch:
        flush_batch(llm, pending_batch, base_dir, prompt_id)
        pending_batch.clear()

    return f"✅ Finished. Results saved to {base_dir}/"

MAX_MB = 100
MAX_BYTES = MAX_MB * 1024 * 1024   # 100 MB hard limit (OpenAI batch)

def flush_batch(llm, batch_items, base_dir, prompt_id):
    """
    Write `batch_items` (list of tuples) to a JSONL file, ensuring the file
    is ≤100 MB.  If it would be larger, recursively split the list and submit
    smaller batches.
    """
    # --- helper to write a temp JSONL and return byte size ----------
    def _write_jsonl(path, items):
        with open(path, "w", encoding="utf-8") as f:
            for (_, _, _, prompt, meta) in items:
                f.write(json.dumps({
                    "custom_id": str(uuid.uuid4()),
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": llm.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0,
                        "max_tokens": min(meta["num_facts"]*meta["k"] + 100,
                                          llm.max_tokens)
                    }
                }) + "\n")
        return os.path.getsize(path)

    # ----------------------------------------------------------------
    if not batch_items:
        return

    tmp_path = os.path.join(base_dir, "_tmp_batch_input.jsonl")
    byte_size = _write_jsonl(tmp_path, batch_items)

    if byte_size > MAX_BYTES:
        mid = len(batch_items) // 2
        print(f"⚠️ Batch {byte_size/1e6:.1f} MB exceeds {MAX_MB} MB – splitting")
        flush_batch(llm, batch_items[:mid], base_dir, prompt_id)
        flush_batch(llm, batch_items[mid:], base_dir, prompt_id)
        os.remove(tmp_path)
        return

    # ---------- safe to submit --------------------------------------
    # upload the temp file
    input_file = llm._client.files.create(file=open(tmp_path, "rb"),
                                          purpose="batch")
    batch = llm._client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    print(f"🔁 Batch ID {batch.id}  ({byte_size/1e6:.1f} MB) submitted")
    os.remove(tmp_path)  # local temp no longer needed

    # ---------- wait -------------------------------------------------
    start = time.time()
    while batch.status not in {"completed", "failed", "cancelled"}:
        if time.time() - start > 3600:         # 1 h guard
            raise TimeoutError("Batch polling timed-out")
        time.sleep(10)
        batch = llm._client.batches.retrieve(batch.id)

    if batch.status != "completed":
        reason = getattr(batch, "failed_reason", None)
        if reason:
            raise RuntimeError(f"Batch failed early: {reason}")
        if getattr(batch, "error_file_id", None):
            err_path = os.path.join(base_dir, f"errors_{batch.id}.jsonl")
            with open(err_path, "wb") as fh:
                fh.write(llm._client.files.content(batch.error_file_id).read())
            raise RuntimeError(
                f"Batch failed during execution. "
                f"Error file saved → {err_path}")
        raise RuntimeError("Batch failed for unknown reason")



    # ---------- download & grade ------------------------------------
    output_file_id = batch.output_file_id
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    result_path = os.path.join(base_dir, f"batch_output_{stamp}.jsonl")
    with open(result_path, "wb") as f_out:
        f_out.write(llm._client.files.content(output_file_id).read())

    # parse & record (same logic as before) ---------------------------
    with open(result_path, "r", encoding="utf-8") as f_in:
        responses = [json.loads(l) for l in f_in]

    assert len(responses) == len(batch_items)
    grouped = {}
    for (n, k, t, prompt, meta), response in zip(batch_items, responses):
        answer = _extract_answer(response)
        correct_text = "\n".join(meta["expected"][k] for k in meta["keys"])
        (seq_acc, tok_acc), flaw, exp_ct, resp_ct = grade_response(
            answer, meta["keys"], meta["expected"],
            tokenizer=llm.count_tokens
        )
        key = (n, k)
        grouped.setdefault(key, {
            "id": f"{llm.model_name}_{n}N_{k}K_{stamp}",
            "prompt_id": prompt_id,
            "provider": llm.provider_id,
            "model": llm.model_name,
            "num_facts": n,
            "k": k,
            "trials": []
        })["trials"].append({
            "trial": t,
            "sequence_accuracy": seq_acc,
            "token_accuracy": tok_acc,
            "major_format_flaw": flaw,
            "response_time_ms": None,
            "prompt_tokens": llm.count_tokens(prompt),
            "prompt_text": prompt,
            "response_text": answer,
            "response_token_count": resp_ct,
            "expected_response_text": correct_text,
            "expected_token_count": exp_ct,
        })

    for (n, k), grp in grouped.items():
        out_f = base_dir / f"{grp['id']}.json"
        with out_f.open("w", encoding="utf-8") as fh:
            json.dump(grp, fh, indent=2)
        print(f"📦 Saved batch results to {out_f}")


def _extract_answer(resp_obj):
    """
    Extract assistant text or an error string from one Batch-API
    output line (already json-loaded).
    """
    # Hard error at top level
    if resp_obj.get("error"):
        return f"ERROR: {resp_obj['error']}"

    resp = resp_obj.get("response", {})
    if resp.get("status_code") != 200:
        return f"ERROR: status {resp.get('status_code')} – {resp.get('body')}"

    try:
        return resp["body"]["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERROR: malformed completion – {e}"
