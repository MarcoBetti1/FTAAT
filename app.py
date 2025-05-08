import streamlit as st
import os
from core.db_utils import get_conn
from core.discover import discover_providers

st.set_page_config(page_title="FTAT Workbench", layout="wide")
get_conn()                   # ensure DB is ready
discover_providers()         # warm-up so pages can use session_state

# ---- Header & Intro ----
st.title("📊 Welcome to the LLM Dashboard!")
st.markdown("""
This app lets you:
- 🧪 Run LLM experiments
- 📊 View results and compare models
- 🧰 Manage prompt templates and token sets

Use the sidebar to navigate through the app.
""")
st.sidebar.success("Select a page above ↖")

# ---- Markdown Documentation Viewer ----
st.header("📚 Documentation")
docs_dir = "docs"
if not os.path.exists(docs_dir):
    st.warning(f"`{docs_dir}/` folder not found. Create it and add .md files to enable docs.")
else:
    md_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    if md_files:
        selected_doc = st.selectbox("Choose a file to view:", md_files)
        with open(os.path.join(docs_dir, selected_doc), "r") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    else:
        st.info("No markdown files found in `docs/`.")

# ---- Optional Settings Expander ----
with st.expander("⚙️ Advanced / Developer Settings"):
    st.markdown("""
    - [🧠 Prompt Editor](#/Prompt_Editor)
    - [🔤 Token Generator](#/Token_Generator)
    - [🧪 Experiment Viewer](#/Experiment_Viewer)
    """, unsafe_allow_html=True)

    st.button("🔁 Refresh Docs", on_click=lambda: st.experimental_rerun())
