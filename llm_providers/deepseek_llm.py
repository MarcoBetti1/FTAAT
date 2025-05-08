# llm_providers/deepseek_llm.py
import os, streamlit as st
from openai import OpenAI          # DeepSeek’s API is OpenAI-compatible
from .base import LLMProvider
from dotenv import load_dotenv
from functools import partial      
from transformers import AutoTokenizer


_encoder = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3",
                                         trust_remote_code=True)

ENCODE = partial(_encoder.encode, add_special_tokens=False)   
# ----------------------------------------------------------------------

class DeepSeekProvider(LLMProvider):
    provider_id      = "deepseek"
    model_name       = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    token_set_path   = "tokens/deepseek_tokens2_clean.json"

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            st.warning("DEEPSEEK_API_KEY not found in environment – provider disabled.")
            raise RuntimeError("Missing API key")

        self._client   = OpenAI(api_key=api_key,
                                base_url="https://api.deepseek.com")
        self._encode   = ENCODE      
        self.max_tokens = 16384 ##OAI          

    # ------------------------------------------------------------------
    # public methods
    # ------------------------------------------------------------------
    def query(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        timeout:    int | None = None
    ) -> str:
        params = dict(
            model       = self.model_name,
            messages    = [{"role": "user", "content": prompt}],
            temperature = temperature,
        )
        if max_tokens is not None:
            params["max_tokens"] = max_tokens      # hard cap
        if timeout is not None:
            params["timeout"] = timeout            #  failed responses take forever

        resp = self._client.chat.completions.create(**params)
        return resp.choices[0].message.content.strip()

    def count_tokens(self, text: str) -> int:   
        return len(self._encode(text))

    # def queue_batch_request(self, *args, **kwargs):
    #     """DeepSeek does not support native batch API; use single-call mode."""
    #     raise NotImplementedError("DeepSeek API has no /batches endpoint")

    # def submit_batch(self, *args, **kwargs):
    #     """DeepSeek does not support native batch API; use single-call mode."""
    #     raise NotImplementedError("DeepSeek API has no /batches endpoint")