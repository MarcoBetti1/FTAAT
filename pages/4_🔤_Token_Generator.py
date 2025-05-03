"""
Streamlit page: Token Generator & Cleaner
"""

import os, json, pkgutil, importlib, inspect
import streamlit as st
import pandas as pd

from scripts.token_generation import (
    generate_alpha_tokens, alpha_tokens_from_vocab, save_tokens
)
from scripts.token_trim import trim_token_set, DEFAULT_SEP

# Optional heavy dependencies
try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None


TOKENS_DIR = "tokens"
LLM_ROOT   = "llm_providers"
os.makedirs(TOKENS_DIR, exist_ok=True)


# ───────── provider discovery ─────────
@st.cache_data(show_spinner=False)
def discover_providers() -> dict[str, str]:
    providers: dict[str, str] = {}
    for mod in pkgutil.iter_modules([LLM_ROOT]):
        if not mod.name.endswith("_llm"):
            continue
        module = importlib.import_module(f"{LLM_ROOT}.{mod.name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.lower().endswith("provider"):
                providers[name.replace("Provider", "")] = f"{LLM_ROOT}.{mod.name}.{name}"
    return providers


# ───────── UI ─────────
st.set_page_config(layout="wide")
st.title("🔤 Token Generator & Cleaner")

tab_browse, tab_generate = st.tabs(["📂 Browse / Search", "⚙️ Generate new tokens"])


# -------------------------------------------------------
#  TAB 1 — browse existing vocab files
# -------------------------------------------------------
with tab_browse:
    files = sorted(f for f in os.listdir(TOKENS_DIR) if f.endswith(".json"))
    if not files:
        st.info("`tokens/` folder is empty.")
    else:
        file_sel = st.selectbox("Token file", files)
        with open(os.path.join(TOKENS_DIR, file_sel)) as f:
            vocab = json.load(f)
        st.write(f"Total tokens: **{len(vocab):,}**")

        query = st.text_input("Search substring")
        preview = [t for t in vocab if query in t][:500]
        st.dataframe(pd.DataFrame({"token": preview}), use_container_width=True, height=400)
        st.download_button("⬇️ Download JSON", json.dumps(vocab), file_sel)


# -------------------------------------------------------
#  TAB 2 — generate / clean
# -------------------------------------------------------
with tab_generate:
    providers = discover_providers()
    prov = st.selectbox("Provider", sorted(providers))

    if prov.lower() == "openai":
        model_name = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4o-mini", "custom…"])
    elif prov.lower() == "deepseek":
        model_name = st.selectbox("Model", ["deepseek-chat", "deepseek-llama3", "custom…"])
    else:
        model_name = st.text_input("Model name (stub)", value="llama3")

    st.subheader("Generation parameters")
    N        = st.number_input("Token count", 1000, 20_000, 10_000, step=500)
    min_len  = st.number_input("min_len", 1, 20, 2)
    max_len  = st.number_input("max_len", min_len, 30, 10)

    st.subheader("Separator-safety parameters")
    sep             = st.text_input("Separator", DEFAULT_SEP)
    single_surround = st.checkbox("Require '|token|' rule", True)
    max_L           = st.slider("Max sequence length L", 1, 4, 2)

    out_file = f"{prov.lower()}_{model_name.replace('/', '_')}_{N}.json"
    out_path = os.path.join(TOKENS_DIR, out_file)

    if st.button("🚀  Generate & Trim"):
        with st.spinner("Working…"):

            if prov.lower() == "openai":
                if not tiktoken:
                    st.error("`tiktoken` not installed.")
                    st.stop()
                enc = tiktoken.encoding_for_model(model_name)
                toks = generate_alpha_tokens(
                    N=N,
                    encode=enc.encode,
                    decode_single=lambda tid: enc.decode_single_token_bytes(tid).decode(),
                    min_len=min_len, max_len=max_len,
                )
                save_tokens(toks, out_path)
                cleaned = trim_token_set(
                    out_path, enc.encode,
                    separator=sep,
                    single_surround=single_surround,
                    max_sequence_length=max_L,
                )

            elif prov.lower() == "deepseek":
                if not AutoTokenizer:
                    st.error("`transformers` not installed.")
                    st.stop()
                tok = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3", trust_remote_code=True)
                toks = alpha_tokens_from_vocab(
                    tok, N=N, min_len=min_len, max_len=max_len
                )
                save_tokens(toks, out_path)
                cleaned = trim_token_set(
                    out_path,
                    lambda s: tok.encode(s, add_special_tokens=False),
                    separator=sep,
                    single_surround=single_surround,
                    max_sequence_length=max_L,
                )

            else:
                st.warning("Llama path is stubbed for now.")
                cleaned = None

        if cleaned:
            st.success(f"✅ Clean vocabulary saved → **{cleaned}**")
            st.balloons()
            st.rerun()
