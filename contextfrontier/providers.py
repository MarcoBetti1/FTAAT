"""Official HTTP APIs. No hidden retries, local tokenizer substitutions or auto truncation."""
import os
from dataclasses import dataclass
from time import perf_counter
import httpx


class ProviderError(RuntimeError):
    pass


@dataclass
class Reply:
    text: str
    status: str
    model: str
    usage: dict
    latency_ms: float
    request_id: str | None
    raw: dict


class APIProvider:
    def __init__(self, spec, client=None):
        self.spec = spec
        self.provider = spec["provider"]
        if self.provider not in ("openai", "anthropic"):
            raise ValueError("Only official OpenAI and Anthropic APIs are supported")
        self.model = spec["model"]
        key_env = "OPENAI_API_KEY" if self.provider == "openai" else "ANTHROPIC_API_KEY"
        key = os.environ.get(key_env)
        if client is None and not key:
            raise ProviderError(f"Missing {key_env}; set it locally, never commit it")
        headers = ({"Authorization": f"Bearer {key}"} if self.provider == "openai" else
                   {"x-api-key": key or "test", "anthropic-version": "2023-06-01"})
        base = "https://api.openai.com/v1/" if self.provider == "openai" else "https://api.anthropic.com/v1/"
        self.client = client or httpx.Client(base_url=base, headers=headers, timeout=120)

    def close(self):
        self.client.close()

    def _post(self, path, body):
        # Do not log API error bodies: they may echo request data or credentials.
        try:
            response = self.client.post(path, json=body)
            response.raise_for_status()
            return response.json(), response.headers.get("x-request-id") or response.headers.get("request-id")
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"{self.provider} HTTP {e.response.status_code} at {path}") from None
        except httpx.HTTPError as e:
            raise ProviderError(f"{self.provider} transport error ({type(e).__name__}); billing may be uncertain") from None

    def input_body(self, case):
        if self.provider == "openai":
            body = dict(model=self.model, instructions=case.system, input=case.prompt)
            if "reasoning_effort" in self.spec:
                body["reasoning"] = {"effort": self.spec["reasoning_effort"]}
            return body
        body = dict(model=self.model, system=case.system,
                    messages=[{"role": "user", "content": case.prompt}])
        if "thinking" in self.spec:
            body["thinking"] = self.spec["thinking"]
        return body

    def count(self, case):
        path = "responses/input_tokens" if self.provider == "openai" else "messages/count_tokens"
        data, request_id = self._post(path, self.input_body(case))
        count = data.get("input_tokens")
        if type(count) is not int or count < 1:
            raise ProviderError("Provider returned an invalid input token count")
        return dict(input_tokens=count, source=f"{self.provider}:{path}",
                    model=self.model, request_id=request_id,
                    is_estimate=self.provider == "anthropic")

    def generate(self, case):
        body = self.input_body(case)
        cap = self.spec["max_output_tokens"]
        if self.provider == "openai":
            body.update(max_output_tokens=cap, store=False, truncation="disabled")
        else:
            body["max_tokens"] = cap
            if "effort" in self.spec:
                body["output_config"] = {"effort": self.spec["effort"]}
        if "temperature" in self.spec:
            body["temperature"] = self.spec["temperature"]
        t0 = perf_counter()
        raw, request_id = self._post("responses" if self.provider == "openai" else "messages", body)
        latency = (perf_counter() - t0) * 1000
        usage = raw.get("usage")
        if not isinstance(usage, dict):
            raise ProviderError("Missing provider usage; billed amount unknown")
        if self.provider == "openai":
            blocks = [c for item in raw.get("output", []) if item.get("type") == "message"
                      for c in item.get("content", [])]
            text = "".join(c.get("text", "") for c in blocks if c.get("type") == "output_text")
            status = "refusal" if any(c.get("type") == "refusal" for c in blocks) else raw.get("status", "unknown")
        else:
            text = "".join(c.get("text", "") for c in raw.get("content", []) if c.get("type") == "text")
            stop = raw.get("stop_reason", "unknown")
            status = "completed" if stop == "end_turn" else "incomplete" if stop == "max_tokens" else stop
        return Reply(text, status, raw.get("model", self.model), usage, latency, request_id, raw)


def usage_counts(provider, usage):
    def integer(key):
        value = usage.get(key, 0)
        if type(value) is not int or value < 0:
            raise ProviderError(f"Invalid usage field {key}")
        return value
    if "input_tokens" not in usage or "output_tokens" not in usage:
        raise ProviderError("Required usage fields missing")
    inp, out = integer("input_tokens"), integer("output_tokens")
    if provider == "anthropic":
        inp += integer("cache_creation_input_tokens") + integer("cache_read_input_tokens")
    return inp, out


def local_text_tokens(model, text):
    """Diagnostic only: excludes API message framing. Unknown models fail explicitly."""
    import tiktoken
    enc = tiktoken.encoding_for_model(model)
    return {"tokens": len(enc.encode(text, disallowed_special=())), "encoding": enc.name,
            "scope": "text_only_not_request", "model": model}
