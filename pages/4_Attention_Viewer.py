# pages/02_attention_dashboard.py
import streamlit as st, pandas as pd, sqlite3, numpy as np, matplotlib.pyplot as plt
from core.db_utils import get_conn

st.title("📊 Attention-capacity dashboard")

conn = get_conn()
df   = pd.read_sql("SELECT num_facts AS N, k AS K, seq_acc, latency_ms FROM trials",
                   conn)

if df.empty:
    st.info("No trials in the database yet.")
    st.stop()

# 1️⃣ Heat-map --------------------------------------------------------------
st.subheader("Heat-map: mean sequence accuracy")
pivot = df.pivot_table(index="N", columns="K", values="seq_acc", aggfunc="mean")
fig, ax = plt.subplots()
im = ax.imshow(pivot.values, aspect="auto", origin="lower")
ax.set_xticks(range(len(pivot.columns)), labels=pivot.columns)
ax.set_yticks(range(len(pivot.index)),   labels=pivot.index)
ax.set_xlabel("K  (tokens per fact)")
ax.set_ylabel("N  (num facts)")
fig.colorbar(im, ax=ax, label="mean sequence accuracy")
st.pyplot(fig)

# 2️⃣ Boundary curve -------------------------------------------------------
st.subheader("Capacity curve (P = N × K)")

df["P"] = df["N"] * df["K"]
cap = df.groupby("P")["seq_acc"].mean().sort_index()
smooth = cap.rolling(3, center=True).mean()

fig2, ax2 = plt.subplots()
ax2.plot(smooth.index, smooth.values, marker="o")
ax2.axhline(0.5, ls="--", label="0.5 accuracy")
ax2.set_xscale("log")
ax2.set_xlabel("Size product  P = N × K   (log scale)")
ax2.set_ylabel("Mean sequence accuracy")
ax2.legend()
st.pyplot(fig2)

# Latency toggle
with st.expander("Show latency overlay"):
    cap_lat = df.groupby("P")["latency_ms"].mean().sort_index()
    fig3, ax3 = plt.subplots()
    ax3.plot(cap_lat.index, cap_lat.values, marker="x")
    ax3.set_xscale("log")
    ax3.set_xlabel("P  (log)")
    ax3.set_ylabel("Mean latency (ms)")
    st.pyplot(fig3)
