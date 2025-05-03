from pathlib import Path
import streamlit as st
from jinja2 import Template, meta

TPL_PATH = Path("prompt_template.j2")
if not TPL_PATH.exists():          # bootstrap if first run
    TPL_PATH.write_text("{{ intro }}\n\n{{ facts_block }}\n")

code = st.text_area("Edit Jinja2 template", TPL_PATH.read_text(), height=550)

col1, col2, col3 = st.columns([1,1,1])
with col1:
    insert_n = st.button("Insert {{ n }}")
with col2:
    insert_k = st.button("Insert {{ k }}")
with col3:
    if st.button("💾 Save"):
        TPL_PATH.write_text(code)
        st.success("Template saved. New experiments will use it.")

# quick insertion logic
if insert_n:
    code += "{{ n }}"
    st.experimental_rerun()
if insert_k:
    code += "{{ k }}"
    st.experimental_rerun()

with st.expander("👁️ Preview with sample data", expanded=False):
    preview = Template(code).render(
        intro="Intro...",
        instructions="Instructions...",
        outro="Outro...",
        facts_block="alpha|bravo => charlie|delta",
        questions_block="alpha|bravo",
        n=1,
        k=2,
    )
    st.code(preview)

# Show which placeholders are currently present
env = Template(code).environment
ast = env.parse(code)
vars_ = sorted(meta.find_undeclared_variables(ast))
st.markdown("**Variables found in template:** " + ", ".join(vars_) if vars_ else "_none_")
