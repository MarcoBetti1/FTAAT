"""
Streamlit page: run one-or-many experiments.

▶ Highlights
• Multi-select providers.
• Free-form lists for num_facts and k  (e.g. “3,6,9” or “1-5”).
• Model override per provider (only shown when that provider is checked).
• Robust traceback + class sanity-check to avoid the object.__init__ trap.
"""
from __future__ import annotations
import os, re, traceback, inspect
import streamlit as st

import scripts.run_experiments as rex
from core.discover      import discover_providers
from core.json_import   import import_json_dir
from core.template_utils import generate_prompt_id_from_template

# ─────────────────────────── helpers ────────────────────────────
def parse_int_list(text: str) -> list[int]:
    """
    Accept  '1,3,5'  or  '1-5'  or '1-10:2' (start-stop[:step]).
    """
    text = text.strip()
    if not text:
        return []
    # 1-10:2  ➜ range(1,11,2)
    m = re.fullmatch(r'(\d+)\s*-\s*(\d+)(?::(\d+))?', text)
    if m:
        lo, hi, step = map(int, m.groups(default='1'))
        return list(range(lo, hi + 1, step))
    # plain CSV
    return [int(x) for x in re.split(r'[ ,]+', text) if x]

def safe_run(**kw):
    "Wrap run_experiments with class-check + full traceback on error."
    try:
        # sanity-check: dotted path must reference a *class*
        mod, cls = kw["provider_module"].rsplit(".", 1)
        obj = getattr(__import__(mod, fromlist=[cls]), cls, None)
        if not inspect.isclass(obj):
            raise TypeError(f"{kw['provider_module']} does not resolve to a class")
        return rex.run_experiments(**kw)
    except Exception as e:
        traceback.print_exc()            # to the server console
        raise e                          # surfaced in UI

# ──────────────────────────── UI ────────────────────────────────
st.title("⚡ Batch-run experiments")

providers = discover_providers()
prov_labels = st.multiselect("Providers", list(providers.keys()), default=list(providers.keys())[:1])

# Per-provider model overrides
model_overrides: dict[str,str] = {}
for label in prov_labels:
    if label == "OpenAI":
        with st.expander(f"{label} settings"):
            opt = st.text_input("Model name (OpenAI)", value=os.getenv("OPENAI_MODEL","gpt-3.5-turbo"), key=f"mdl_{label}")
            model_overrides[label] = opt
    elif label == "DeepSeek":
        with st.expander(f"{label} settings"):
            opt = st.text_input("Model name (DeepSeek)", value=os.getenv("DEEPSEEK_MODEL","deepseek-chat"), key=f"mdl_{label}")
            model_overrides[label] = opt
    else:
        model_overrides[label] = ""       # no UI yet

st.markdown("#### Experiment parameter grids")

# UI: num_facts  ------------------------------------------------------------
st.markdown("#### Parameters")

col1, col2 = st.columns(2, gap="small")

with col1:
    n_mode = st.radio(
        "N input mode",
        ["Range", "List"],
        horizontal=True,
        key="n_mode",
        help="• **Range** → '1-32[:2]' (start-stop[:step])\n"
             "• **List**  → '1,3,6,12'"
    )
    if n_mode == "Range":
        n_text = st.text_input("N range", "20-200",
            help="start-stop[:step]  →  1-8  or 1-32:4")
    else:
        n_text = st.text_input("N values", "1,2,4,8")

with col2:
    k_mode = st.radio(
        "K input mode",
        ["Range", "List"],
        horizontal=True,
        key="k_mode",
        help="Same syntax as N"
    )
    if k_mode == "Range":
        k_text = st.text_input("K range", "20-200")
    else:
        k_text = st.text_input("K values", "2,3,4")

# reuse existing helper -----------------------------------------------------
num_facts_list = parse_int_list(n_text)
k_list         = parse_int_list(k_text)

adaptive = st.checkbox(
    "Adaptive staircase search",
    value=False,
    help="Starts at (min N, min K) and doubles both until either "
         "exceeds the chosen **max** value."
)

if adaptive:
    # force both axes to “Range” mode
    if n_mode != "Range" or k_mode != "Range":
        st.warning("Staircase needs ranges. Switched both axes to Range mode.")
        st.session_state["n_mode"] = "Range"
        st.session_state["k_mode"] = "Range"

early_abort = st.checkbox(
    "Early abort on first flop",
    value=True,
    help="Stop further trials for a given (N,K) after the first "
         "major format flaw or <50 % accuracy."
)

c1, c2, c3 = st.columns([1,1,1], gap="small")
with c1:
    trials = st.number_input("Trials per experiment", 1, 50, 1)
with c2:
    timeout_sec = st.number_input(
    "LLM timeout (sec)",
    10, 300, 60,
    help="Hard wall-clock limit per API call."
)
with c3:
    max_mult = st.number_input(
    "Max-tokens multiplier",
    1, 10, 2,
    help="Completion cap = expected_tokens × this value."
)

default_id = generate_prompt_id_from_template()
prompt_id = st.text_input(
    "Prompt ID", value=default_id,
    help="Organize all runs under this experiment name."
)

if st.button("🚀  Run all"):
    if not prov_labels:
        st.warning("Pick at least one provider")
        st.stop()
    if not num_facts_list or not k_list:
        st.warning("Parameter lists are empty or malformed.")
        st.stop()

    st.info("Launching experiments … watch the terminal for progress.")
    for label in prov_labels:
        dotted = providers[label]
        # set env var so the provider picks it up
        if label == "OpenAI" and model_overrides[label]:
            os.environ["OPENAI_MODEL"] = model_overrides[label]
        if label == "DeepSeek" and model_overrides[label]:
            os.environ["DEEPSEEK_MODEL"] = model_overrides[label]

        st.write(f"➡️  **{label}**  ({model_overrides.get(label,'default')})")

        msg = safe_run(
            provider_module = dotted,
            facts_list_sizes = num_facts_list,
            token_sizes      = k_list,
            trials           = trials,
            output_root      = "results",           # top-level base
            prompt_id        = prompt_id,           
            adaptive         = adaptive,
            early_abort      = early_abort,
            timeout_sec      = timeout_sec,
            max_tok_mult     = max_mult,
        )

        st.success(msg)

    new_rows = import_json_dir()
    st.toast(f"Imported {new_rows} fresh rows into SQLite.", icon="✅")
