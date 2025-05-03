import streamlit as st, pandas as pd, plotly.express as px
from db_utils import get_conn

def build_mismatch_df(where: str, top_n=40):
    conn = get_conn()
    q = f"SELECT expected, response FROM trials {('WHERE ' + where) if where else ''};"
    df = pd.read_sql_query(q, conn)

    from collections import Counter
    counter = Counter()
    for exp, resp in zip(df["expected"], df["response"]):
        exp_toks = exp.split("|")
        resp_toks = resp.split("|")
        for e, r in zip(exp_toks, resp_toks):
            if e != r:
                counter[r] += 1
        # extra tokens
        if len(resp_toks) > len(exp_toks):
            for r in resp_toks[len(exp_toks):]:
                counter[r] += 1

    rows = counter.most_common(top_n)
    return pd.DataFrame(rows, columns=["token", "count"])

def plot_heat(df):
    fig = px.imshow(df[["count"]].T,
                    labels=dict(x="token", y="", color="mismatch count"),
                    x=df["token"].tolist(),
                    aspect="auto",
                    color_continuous_scale="Reds",
                    text_auto=True)
    fig.update_yaxes(visible=False)
    return fig

st.title("🔥 Token-level mismatch heat-map")

conn = get_conn()
providers = [r[0] for r in conn.execute("SELECT DISTINCT provider FROM trials")]
ks        = [r[0] for r in conn.execute("SELECT DISTINCT k FROM trials")]

p_sel = st.multiselect("Provider", providers, default=providers)
k_sel = st.multiselect("k", ks, default=ks)
tok_min, tok_max = st.slider("token_accuracy range", 0.0, 1.0, (0.0, 1.0), 0.01)
extra_sql = st.text_input("Additional SQL predicates", "")

where_parts = []
if p_sel: where_parts.append(f"provider IN ({','.join(map(repr,p_sel))})")
if k_sel: where_parts.append(f"k IN ({','.join(map(str,k_sel))})")
where_parts.append(f"tok_acc BETWEEN {tok_min} AND {tok_max}")
if extra_sql.strip(): where_parts.append(extra_sql)

where_clause = " AND ".join(where_parts)
df = build_mismatch_df(where_clause)
st.plotly_chart(plot_heat(df), use_container_width=True)
