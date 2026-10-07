"""Standard-library HTTP adapter for LM Studio's Chat Completions API."""
import json
import os
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

class LocalClient:
    def __init__(self, *, model=None, base_url=None):
        self.base = (base_url or os.getenv("LM_STUDIO_BASE_URL") or os.getenv("LM_BASE_URL", "http://127.0.0.1:1234/v1")).rstrip("/")
        parsed = urlsplit(self.base)
        if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("v0.1 supports only a loopback HTTP model server")
        self.model = model or os.getenv("SUT_MODEL") or os.getenv("LM_MODEL", "openai/gpt-oss-20b")

    def request(self, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        req = Request(self.base + path, data=data, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=180) as response:
            return json.load(response)

    def models(self):
        return self.request("/models")

    def __call__(self, messages, tools):
        response = self.request("/chat/completions", {
            "model": self.model, "messages": messages, "tools": tools,
            "temperature": 0, "max_tokens": 2048, "stream": False})
        try:
            message = response["choices"][0]["message"]
            finish = response["choices"][0].get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Invalid Chat Completions response") from exc
        if finish == "length":
            raise ValueError("Model output truncated; increase max_tokens or simplify prompt")
        # Only send fields that belong in a subsequent Chat Completions request.
        return {k: v for k, v in message.items() if k in {"role", "content", "tool_calls"}}
