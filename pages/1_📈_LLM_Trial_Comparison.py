import streamlit as st
import pandas as pd
import plotly.express as px
from pages.util.db_utils import get_conn

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(layout="wide")
st.title("📈 LLM Trial Comparison Dashboard")

# ----------------------------
# Load data
# ----------------------------
conn = get_conn()
df = pd.read_sql_query("SELECT * FROM trials", conn)

# ----------------------------
# Sidebar controls
# ----------------------------
with st.sidebar:
    st.header("🔍 Filter and Display Options")

    models = sorted(df["model"].dropna().unique())
    providers = sorted(df["provider"].dropna().unique())
    metrics = ["seq_acc", "tok_acc", "flaw_percent"]

    selected_models = st.multiselect("Models", models, default=models)
    selected_providers = st.multiselect("Providers", providers, default=providers)

    x_axis = st.radio("X-axis", ["num_facts", "k"])
    selected_metrics = st.multiselect("Y-axis Metrics", metrics, default=["seq_acc", "tok_acc"])

    st.markdown("#### Filter by Test Parameters")
    n_range = st.slider("N (Number of Facts)", int(df["num_facts"].min()), int(df["num_facts"].max()), (1, 10))
    k_range = st.slider("K (Tokens per Fact)", int(df["k"].min()), int(df["k"].max()), (1, 4))

    min_trials = st.slider("Min trials per test", 1, 10, 1)
    exclude_flaw = st.checkbox("Exclude major format flaw trials", value=False)

    chart_type = st.radio("Chart Type", ["Line", "Bar"])

# ----------------------------
# Preprocessing
# ----------------------------
df["flaw_percent"] = df["flaw"] * 100

df_filtered = df[
    df["model"].isin(selected_models) &
    df["provider"].isin(selected_providers) &
    df["num_facts"].between(*n_range) &
    df["k"].between(*k_range)
]

if exclude_flaw:
    df_filtered = df_filtered[df_filtered["flaw"] == 0]

# ----------------------------
# Group and Aggregate
# ----------------------------
group_keys = ["model", "num_facts", "k"]
agg_df = (
    df_filtered
    .groupby(group_keys)
    .agg(
        seq_acc=('seq_acc', 'mean'),
        tok_acc=('tok_acc', 'mean'),
        flaw_percent=('flaw_percent', 'mean'),
        num_trials=('trial_idx', 'count')
    )
    .reset_index()
)

# Filter out test groups with too few trials
agg_df = agg_df[agg_df["num_trials"] >= min_trials]

# ----------------------------
# Plotting
# ----------------------------
if agg_df.empty:
    st.warning("No data to plot. Try relaxing the filters.")
else:
    st.markdown(f"### 📊 Visualizing: {', '.join(selected_metrics)} vs {x_axis}")

    cols = st.columns(2)
    for idx, metric in enumerate(selected_metrics):
        with cols[idx % 2]:
            fig = None
            if chart_type == "Line":
                fig = px.line(
                    agg_df,
                    x=x_axis,
                    y=metric,
                    color="model",
                    markers=True,
                    title=f"{metric.replace('_', ' ').title()} vs {x_axis.upper()}",
                    labels={"model": "Model"}
                )
            else:
                fig = px.bar(
                    agg_df,
                    x=x_axis,
                    y=metric,
                    color="model",
                    barmode="group",
                    title=f"{metric.replace('_', ' ').title()} vs {x_axis.upper()}",
                    labels={"model": "Model"}
                )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Optional: Data Export
# ----------------------------
with st.expander("📥 Download Aggregated Data"):
    st.download_button("Download CSV", agg_df.to_csv(index=False), "aggregated_trials.csv")
