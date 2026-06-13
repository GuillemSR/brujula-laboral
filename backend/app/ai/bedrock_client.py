from dataclasses import dataclass
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import Settings
from app.core.config import get_settings


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_id: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class BedrockClient:
    """Small adapter for Bedrock Converse calls."""

    def __init__(
        self,
        client: Any | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client or boto3.client(
            "bedrock-runtime",
            region_name=self.settings.aws_region,
            config=Config(
                connect_timeout=10,
                read_timeout=60,
                retries={"total_max_attempts": 2, "mode": "standard"},
            ),
        )

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        *,
        max_tokens: int = 900,
        temperature: float = 0.2,
    ) -> ModelResponse:
        if not self.settings.bedrock_model_id:
            raise RuntimeError("BEDROCK_MODEL_ID is not configured")

        try:
            response = self.client.converse(
                modelId=self.settings.bedrock_model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}],
                    }
                ],
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                },
            )
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError("Could not generate model response") from exc

        content = response["output"]["message"]["content"]
        text = "\n".join(block["text"] for block in content if "text" in block).strip()
        usage = response.get("usage", {})
        return ModelResponse(
            text=text,
            model_id=self.settings.bedrock_model_id,
            input_tokens=usage.get("inputTokens"),
            output_tokens=usage.get("outputTokens"),
        )
