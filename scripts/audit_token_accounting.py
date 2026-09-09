"""Reproduce the local inventory measurement used in the video; no API calls."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import tiktoken


def audit(samples=1000, seed=1701):
    path = Path(__file__).resolve().parents[1] / 'tokens/gpt4o_tokens_clean.json'
    vocab = json.loads(path.read_text())
    model = 'gpt-4o-mini-2024-07-18'
    enc = tiktoken.encoding_for_model(model)
    rng = random.Random(seed)
    counts = Counter()
    examples = []
    for _ in range(samples):
        symbols = rng.sample(vocab,4)
        joined = '|'.join(symbols)
        encoded = enc.encode(joined)
        counts[len(encoded)] += 1
        if len(examples)<3:
            examples.append(dict(symbols=symbols,joined=joined,actual_text_tokens=len(encoded),
                                 token_ids=encoded,decoded_pieces=[enc.decode([t]) for t in encoded]))
    return dict(kind='local_tokenizer_measurement_not_model_inference',seed=seed,model=model,
                encoding=enc.name,tiktoken_version=importlib.metadata.version('tiktoken'),
                inventory_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),K_symbols=4,
                samples=samples,full_sequence_token_histogram=dict(counts),examples=examples)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',default='artifacts/token-accounting.json')
    args=parser.parse_args(); out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(audit(),indent=2)+'\n')
    print(out)
