from dataclasses import dataclass

from app.core.config import get_settings


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_id: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class BedrockClient:
    """Small adapter for Bedrock calls.

    The concrete request/response shapes will be added after choosing the first model.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate(self, prompt: str) -> ModelResponse:
        if not self.settings.bedrock_model_id:
            raise RuntimeError("BEDROCK_MODEL_ID is not configured")

        raise NotImplementedError("Bedrock generation is pending model selection")
