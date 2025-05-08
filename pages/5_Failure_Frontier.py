# failure_frontier_dashboard.py
#
# Streamlit “drop-in” page that replaces all previous graphs with one
# interactive canvas + side-panel controls.
#
# Requires:  pip install altair vega_datasets scikit-image statsmodels

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from skimage.measure import find_contours
import statsmodels.stats.proportion as smp
from core.db_utils import get_conn           # ← keep your helper

# ──────────────────────── load & cache ──────────────────────────
@st.cache_data(show_spinner=False)
def load_trials() -> pd.DataFrame:
    return (pd.read_sql("""
            SELECT num_facts AS N,
                   k          AS K,
                   flaw       AS flaw,
                   seq_acc    AS acc
            FROM trials
        """, get_conn())
            .assign(P=lambda t: t.N * t.K))

df = load_trials()
if df.empty:
    st.info("No data yet."); st.stop()

agg = (df.groupby(["N", "K"])
         .agg(flaw_rate=("flaw", "mean"),
              runs      =("flaw", "size"))
         .reset_index())

# ──────────────────────── UI controls ───────────────────────────
st.title("🛑 Failure-Frontier Dashboard")

st.sidebar.header("🔧 Controls")
thr        = st.sidebar.slider("Major-flaw threshold", 0.0, 1.0, 0.50, 0.05)
x_axis_opt = ["N", "K", "P"]
x_axis_lab = st.sidebar.radio("X-axis", x_axis_opt, index=0)
y_axis_lab = st.sidebar.radio("Y-axis", ["K", "N"], index=1)
show_pts   = st.sidebar.checkbox("Show individual (N,K) points", value=True)
show_heat  = st.sidebar.checkbox("Heat-map background",          value=True)
show_front = st.sidebar.checkbox("Frontier isoline",             value=True)
conf_int   = st.sidebar.checkbox("95 % confidence ribbon",       value=False)

# ──────────────────────── chart builder ─────────────────────────
def frontier_chart(agg: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(agg).encode(
        x=alt.X(x_axis_lab, title=x_axis_lab, scale=alt.Scale(zero=False)),
        y=alt.Y(y_axis_lab, title=y_axis_lab, scale=alt.Scale(zero=False))
    )

    layers = []

    # Heat-map tiles
    if show_heat:
        layers.append(
            base.mark_rect().encode(
                color=alt.Color("flaw_rate:Q",
                                scale=alt.Scale(domain=[0, 1],
                                                scheme="redyellowgreen"),
                                title="flaw rate")
            )
        )

    # Scatter points sized by run count
    if show_pts:
        layers.append(
            base.mark_circle(size=80, stroke="black").encode(
                tooltip=["N", "K", "runs", alt.Tooltip("flaw_rate:Q", format=".2%")],
                size=alt.Size("runs:Q",
                              scale=alt.Scale(range=[30, 300]), legend=None),
                color=alt.condition(f"datum.flaw_rate >= {thr}",
                                    alt.value("red"), alt.value("green"))
            )
        )

    # Frontier isoline (marching-squares on flaw_rate grid)
    if show_front:
        grid = agg.pivot(index="N", columns="K", values="flaw_rate").sort_index()
        if grid.notna().sum().sum() >= 4:                       # need min area
            Z = np.nan_to_num(grid.to_numpy(), nan=thr)        # fill NaNs
            contours = find_contours(Z, thr)
            K_vals, N_vals = grid.columns.to_numpy(), grid.index.to_numpy()
            for cont in contours:
                Ks = np.interp(cont[:, 1], np.arange(len(K_vals)), K_vals)
                Ns = np.interp(cont[:, 0], np.arange(len(N_vals)), N_vals)
                layers.append(
                    alt.Chart(pd.DataFrame({"K": Ks, "N": Ns}))
                       .mark_line(strokeDash=[4, 4], color="black")
                       .encode(x="K:Q", y="N:Q")
                )

    chart = alt.layer(*layers).properties(
        width="container",
        height=500,
        title=f"Failure frontier @ threshold ≥ {thr:0.2f}"
    )

    # 1-D confidence ribbon (only when axis collapses)
    if conf_int and x_axis_lab != y_axis_lab:
        by_x = agg.groupby(x_axis_lab).apply(
            lambda g: pd.Series({
                "pos": (g.flaw_rate * g.runs).sum(),
                "n":   g.runs.sum()
            })
        ).reset_index()
        lo, hi = smp.proportion_confint(by_x.pos, by_x.n, alpha=0.05, method="wilson")
        ci = pd.DataFrame({x_axis_lab: by_x[x_axis_lab], "lo": lo, "hi": hi})
        chart += (alt.Chart(ci).mark_area(opacity=0.20, color="grey")
                        .encode(x=f"{x_axis_lab}:Q", y="lo:Q", y2="hi:Q"))

    return chart

st.altair_chart(frontier_chart(agg), use_container_width=True)

# ──────────────────────── stats & table ─────────────────────────
with st.expander("🔍 Aggregated statistics"):
    st.dataframe(
        agg.style.format({"flaw_rate": "{:.1%}"})
           .background_gradient(cmap="RdYlGn_r", subset=["flaw_rate"])
    )

st.sidebar.markdown(
    f"**{len(df):,}** individual trials  •  "
    f"**{agg.runs.sum():,}** aggregated runs"
)
