import streamlit as st, pandas as pd, sqlite3
from pages.util.db_utils import get_conn
from token_diff import colour_tokens

def load_trial(eid: str, idx: int) -> dict:
    conn = get_conn()
    row = conn.execute("""
        SELECT * FROM trials WHERE id=? AND trial_idx=?;
    """, (eid, idx)).fetchone()
    if not row:
        return None
    cols = [c[0] for c in conn.execute("PRAGMA table_info(trials)")]
    return dict(zip(cols, row))

eid  = st.session_state.get("current_experiment_id")
idx  = st.session_state.get("current_trial_idx", 0)

if eid is None:
    st.error("Open a trial from the Browse page first.")
    st.stop()

trial = load_trial(eid, idx)
if trial is None:
    st.error("Trial not found.")
    st.stop()

st.title(f"👁️ Trial {idx} of experiment {eid}")
st.subheader("Prompt")
st.code(trial["prompt"])

st.subheader("Model response vs expected")
st.markdown(colour_tokens(trial["expected"], trial["response"]),
            unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
if col1.button("◀️ Prev") and idx > 0:
    st.session_state["current_trial_idx"] -= 1
    st.experimental_rerun()
if col3.button("Next ▶️"):
    st.session_state["current_trial_idx"] += 1
    st.experimental_rerun()
