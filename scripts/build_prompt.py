"""
Prompt builder – Jinja2 powered.

Any {{variable}} in prompt_template.j2 can be filled via `context` below.
"""
from pathlib import Path
import random
from jinja2 import Template

TPL = Template(Path("prompt_template.j2").read_text())

def build_prompt_for_all_keys(facts_list, *, k: int | None = None):
    """
    facts_list : [(fact_line, key, value), ...]
    k          : tokens per fact (passed in run_experiments)
    Returns (prompt_str, keys_in_order)
    """
    facts_block = "\n".join(f for (f,_,_) in facts_list)

    keys = [k for (_,k,_) in facts_list]
    random.shuffle(keys)
    questions_block = "\n".join(keys)

    prompt = TPL.render(
        facts_block     = facts_block,
        questions_block = questions_block,
        n               = len(facts_list),
        k               = k,
    ).strip() + "\n\n"

    return prompt, keys
