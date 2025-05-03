# llm_providers/deepseek_llm.py
import os, tiktoken
from openai import OpenAI     # DeepSeek’s API is OpenAI-compatible
from .base import LLMProvider
from dotenv import load_dotenv
try:
    from deepseek_tokenizer import ds_token            
    _encoder = ds_token
except ImportError:                                   
    from transformers import AutoTokenizer
    _encoder = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3")

class DeepSeekProvider(LLMProvider):
    provider_id = "deepseek"
    model_name  = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")  # pick yours
    token_set_path = "data/tokens/deepseek_tokens_clean.json"

    def __init__(self):
        load_dotenv()
        self._client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")
        self._encoding = _encoder   

    def query(self, prompt: str, *, temperature: float = 0.0) -> str:
        resp = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()

    def count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))
