import json
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.ai.bedrock_client import ModelResponse
from app.core.config import Settings, get_settings


UrlOpen = Callable[..., Any]


class OllamaClient:
    """Temporary local Ollama adapter for development without Bedrock access."""

    def __init__(
        self,
        settings: Settings | None = None,
        open_url: UrlOpen = urlopen,
    ) -> None:
        self.settings = settings or get_settings()
        self.open_url = open_url

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        *,
        max_tokens: int = 900,
        temperature: float = 0.2,
    ) -> ModelResponse:
        payload = {
            "model": self.settings.ollama_model_id,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        request = Request(
            f"{self.settings.ollama_base_url.rstrip('/')}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with self.open_url(request, timeout=self.settings.ollama_timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError("Could not generate Ollama response") from exc

        text = str(response_payload.get("response", "")).strip()
        return ModelResponse(
            text=text,
            model_id=str(response_payload.get("model") or self.settings.ollama_model_id),
            input_tokens=_optional_int(response_payload.get("prompt_eval_count")),
            output_tokens=_optional_int(response_payload.get("eval_count")),
        )

    def stream(
        self,
        prompt: str,
        system_prompt: str,
        *,
        max_tokens: int = 900,
        temperature: float = 0.2,
    ):
        payload = {
            "model": self.settings.ollama_model_id,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        request = Request(
            f"{self.settings.ollama_base_url.rstrip('/')}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with self.open_url(request, timeout=self.settings.ollama_timeout_seconds) as response:
                for line in response:
                    if not line:
                        continue
                    chunk = json.loads(line.decode("utf-8"))
                    text = str(chunk.get("response", ""))
                    if text:
                        yield text
                    if chunk.get("done") is True:
                        break
        except (HTTPError, URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError("Could not stream Ollama response") from exc


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None
