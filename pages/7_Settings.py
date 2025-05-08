import streamlit as st, os
from dotenv import dotenv_values, set_key

ENV_PATH = ".env"

st.title("🔑  API keys & model settings")

config = dotenv_values(ENV_PATH)

openai_key  = st.text_input("OPENAI_API_KEY",  config.get("OPENAI_API_KEY", ""),  type="password")
openai_model = st.text_input("OPENAI_MODEL",  config.get("OPENAI_MODEL", "gpt-4o"))

deepseek_key = st.text_input("DEEPSEEK_API_KEY", config.get("DEEPSEEK_API_KEY", ""), type="password")
deepseek_model = st.text_input("DEEPSEEK_MODEL", config.get("DEEPSEEK_MODEL", "deepseek-chat"))

if st.button("Save .env"):
    for k, v in [("OPENAI_API_KEY", openai_key),
                 ("OPENAI_MODEL",  openai_model),
                 ("DEEPSEEK_API_KEY", deepseek_key),
                 ("DEEPSEEK_MODEL",  deepseek_model)]:
        set_key(ENV_PATH, k, v, quote_mode="never")
    st.success("Saved!  You must restart the Streamlit server for changes to take effect.")
