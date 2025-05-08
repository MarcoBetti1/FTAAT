import streamlit as st, pandas as pd, sqlite3
from core.db_utils import get_conn
from core.json_import import import_json_dir
import streamlit as st
import pandas as pd
import ace_tools_open as tools

st.set_page_config(layout="wide")
st.title("📊 Experiment Dashboard")

# Connect to DB and load data
conn = get_conn()
df = pd.read_sql_query("SELECT * FROM trials LIMIT 10000;", conn)

# Sidebar filters
with st.sidebar.expander("🎛️ Filters & Settings", expanded=False):
    provider_options = sorted(df['provider'].dropna().unique())
    model_options = sorted(df['model'].dropna().unique())
    n_options = sorted(df['num_facts'].dropna().unique())
    k_options = sorted(df['k'].dropna().unique())

    selected_provider = st.multiselect("Provider", provider_options, default=provider_options)
    selected_model = st.multiselect("Model", model_options, default=model_options)
    selected_n = st.multiselect("Num Facts (N)", n_options, default=n_options)
    selected_k = st.multiselect("Tokens per Fact (K)", k_options, default=k_options)

    custom_where = st.text_input("Optional SQL WHERE override")

# Filter data based on sidebar or custom SQL
if custom_where.strip():
    try:
        df_filtered = pd.read_sql_query(f"SELECT * FROM trials WHERE {custom_where}", conn)
    except Exception as e:
        st.error(f"Invalid SQL WHERE clause: {e}")
        df_filtered = pd.DataFrame()
else:
    df_filtered = df[
        df["provider"].isin(selected_provider) &
        df["model"].isin(selected_model) &
        df["num_facts"].isin(selected_n) &
        df["k"].isin(selected_k)
    ]

# Summary statistics grouped by (provider, model, N, K)
if not df_filtered.empty:
    stats_df = (
        df_filtered
        .groupby(['provider', 'model', 'num_facts', 'k'], as_index=False)
        .agg(
            avg_seq_acc=('seq_acc', 'mean'),
            avg_tok_acc=('tok_acc', 'mean'),
            pct_major_flaw=('flaw', lambda x: (x > 0).mean() * 100),
            n_trials=('trial_idx', 'count')
        )
        .sort_values(['provider', 'model', 'num_facts', 'k'])
    )

    st.markdown("### 📈 Summary Statistics (grouped)")
    edited = st.data_editor(
        stats_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "avg_seq_acc": st.column_config.NumberColumn("Avg Sequence Accuracy", format="%.3f"),
            "avg_tok_acc": st.column_config.NumberColumn("Avg Token Accuracy", format="%.3f"),
            "pct_major_flaw": st.column_config.ProgressColumn("Major Format Flaws (%)", format="%.1f"),
        },
        key="summary_table"
    )

    # Select row for drill-down
    selected_rows = st.session_state["summary_table"]["edited_rows"]
    if selected_rows:
        selected = stats_df.iloc[list(selected_rows.keys())[0]]  # single selection
        st.markdown(f"### 🔍 Trials for `{selected['provider']}` / `{selected['model']}` / N={selected['num_facts']} / K={selected['k']}")

        matching_trials = df_filtered[
            (df_filtered['provider'] == selected['provider']) &
            (df_filtered['model'] == selected['model']) &
            (df_filtered['num_facts'] == selected['num_facts']) &
            (df_filtered['k'] == selected['k'])
        ].sort_values("trial_idx")

        st.dataframe(matching_trials, use_container_width=True)

        if st.button("👁️ Inspect first trial"):
            trial = matching_trials.iloc[0]
            st.session_state["current_experiment_id"] = trial["id"]
            st.session_state["current_trial_idx"] = int(trial["trial_idx"])
            st.switch_page("pages/3_👁️_Trial_Viewer.py")

else:
    st.info("No trials match the current filter criteria.")

# Option to refresh from JSON
st.divider()
if st.button("🔄  Refresh DB from JSON folders"):
    rows = import_json_dir()
    st.toast(f"Imported {rows} new rows", icon="✅")
    st.rerun()