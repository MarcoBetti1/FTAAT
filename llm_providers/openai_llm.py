import os
import json
import time
import uuid
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

class OpenAIProvider:
    provider_id = "openai"
    model_name  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    token_set_path = "tokens/gpt4o_tokens_clean.json"

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY")
        self._client   = OpenAI(api_key=api_key)
        self._encoding = tiktoken.encoding_for_model(self.model_name)
        self.max_tokens = 16384

        self.batch_inputs = []
        self.batch_metadata = []

    def count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))

    def queue_batch_request(self, prompt: str, metadata: dict, max_tokens=500):
        self.batch_inputs.append({
            "custom_id": str(uuid.uuid4()),
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": max_tokens
            }
        })
        self.batch_metadata.append(metadata)

# llm_providers/openai_llm.py   ← replace ONLY the submit_batch method
    def submit_batch(self, save_dir: str, timeout_sec: int = 300):
        """
        Flush the currently-queued batch_inputs to OpenAI’s Batch API.
        Returns
        -------
        result_path : str   – local path to the output JSONL
        meta_copy   : list  – copy of self.batch_metadata (one-to-one with lines)
        """
        if not self.batch_inputs:
            raise RuntimeError("submit_batch() called with an empty queue.")

        # 1.  ------------  upload input file  -------------------------------
        input_path = os.path.join(save_dir, "batch_input.jsonl")
        with open(input_path, "w", encoding="utf-8") as f:
            for item in self.batch_inputs:
                f.write(json.dumps(item) + "\n")

        input_file = self._client.files.create(
            file=open(input_path, "rb"),
            purpose="batch"
        )

        # 2.  ------------  create batch job  --------------------------------
        batch = self._client.batches.create(
            input_file_id=input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        print(f"🔁 Batch ID: {batch.id}")

        # 3.  ------------  poll for completion  -----------------------------
        start = time.time()
        while batch.status not in {"completed", "failed", "cancelled"}:
            if time.time() - start > timeout_sec:
                raise TimeoutError("⏱️ Batch processing timed out")
            time.sleep(10)
            batch = self._client.batches.retrieve(batch.id)
            print(f"⏳ Status: {batch.status}")

        if batch.status != "completed":
            raise RuntimeError(f"❌ Batch failed with status: {batch.status}")

        # 4.  ------------  download output file  ----------------------------
        output_file_id = batch.output_file_id          # <- FIXED
        result_path = os.path.join(save_dir, "batch_output.jsonl")
        with open(result_path, "wb") as f:
            # files.content() returns a stream-like object (new SDK ≥0.28)
            f.write(self._client.files.content(output_file_id).read())

        print(f"✅ Batch results saved to {result_path}")

        # 5.  ------------  return & reset internal queues -------------------
        meta_copy = list(self.batch_metadata)        # keep a copy for caller
        self.batch_inputs.clear()
        self.batch_metadata.clear()
        return result_path, meta_copy
