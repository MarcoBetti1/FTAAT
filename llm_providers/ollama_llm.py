# llm_providers/ollama_llm.py
import json, os, requests, tiktoken
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    
    provider_id = "ollama"
    model_name  = os.getenv("OLLAMA_MODEL", "llama3.2")
    token_set_path = "data/tokens/llama3_tokens.json"

    def __init__(self, host: str = "http://localhost:11434"):
        self._url = f"{host}/api/generate"
        try:
            # tiktoken already ships 'llama3' as of v0.6.0; fallback if absent
            self._encoding = tiktoken.get_encoding("llama3")
        except KeyError:
            from transformers import AutoTokenizer
            self._encoding = AutoTokenizer.from_pretrained(
                "NousResearch/Meta-Llama-3-8B-Instruct", use_fast=True
            )

    # --- interface ---
    def query(self, prompt: str, *, temperature: float = 0.0) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        r = requests.post(self._url, json=payload, timeout=600)
        r.raise_for_status()
        return r.json()["response"].strip()

    def count_tokens(self, text: str) -> int:
        # transformers encoders expose either .encode or __call__
        if hasattr(self._encoding, "encode"):
            return len(self._encoding.encode(text))
        return len(self._encoding(text)["input_ids"])
