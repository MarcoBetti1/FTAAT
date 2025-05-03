# llm_providers/openai_llm.py
import os, tiktoken
from openai import OpenAI
from .base import LLMProvider
from dotenv import load_dotenv

class OpenAIProvider(LLMProvider):
    provider_id = "openai"
    model_name  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    token_set_path = "data/tokens/gpt4o_tokens_clean.json"

    def __init__(self):
        load_dotenv()
        self._client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._encoding = tiktoken.encoding_for_model(self.model_name)

    # --- interface ---
    def query(self, prompt: str, *, temperature: float = 0.0) -> str:
        resp = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()

    def count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))
