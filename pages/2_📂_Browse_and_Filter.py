import streamlit as st, pandas as pd, sqlite3
from db_utils import get_conn
from json_import import import_json_dir
st.title("📂 Browse & filter trials")

conn = get_conn()

default_where = st.text_input("Custom SQL WHERE clause", "")
query = f"SELECT * FROM trials {'WHERE ' + default_where if default_where else ''} LIMIT 5000;"
df = pd.read_sql_query(query, conn)

st.dataframe(df, use_container_width=True)

if st.button("Open first selected row"):
    sel = st.session_state.get("selected_rows")
    if sel:
        trial = df.iloc[sel[0]]
        # store keys so the viewer knows what to show
        st.session_state["current_experiment_id"] = trial["id"]
        st.session_state["current_trial_idx"]     = int(trial["trial_idx"])
        st.switch_page("pages/3_👁️_Trial_Viewer.py")
    else:
        st.warning("Click a row first (double-click in Streamlit 1.33+).")

if st.button("🔄  Refresh DB from JSON folders"):
    rows = import_json_dir()      # reuse the helper
    st.toast(f"Imported {rows} new rows", icon="✅")
    st.experimental_rerun()