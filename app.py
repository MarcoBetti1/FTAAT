import streamlit as st
from pages.util.db_utils import get_conn
from pages.util.discover import discover_providers   # small helper above

st.set_page_config(page_title="FTAT Workbench", layout="wide")
st.sidebar.success("Select a page above ↖")
get_conn()                   # ensure DB is ready
discover_providers()         # warm-up so pages can use session_state
