import streamlit as st, importlib, pkgutil, inspect
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

LLM_ROOT = Path("llm_providers")

@st.cache_data(show_spinner=False)
def discover_providers():
    providers = {}
    for module_info in pkgutil.iter_modules([LLM_ROOT]):
        if not module_info.name.endswith("_llm"):
            continue
        module = importlib.import_module(f"llm_providers.{module_info.name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.lower().endswith("provider"):
                dotted = f"llm_providers.{module_info.name}.{name}"
                providers[name.replace("Provider","")] = dotted
    return providers
