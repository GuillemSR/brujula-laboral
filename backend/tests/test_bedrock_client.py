from app.ai.bedrock_client import BedrockClient
from app.ai.mock_bedrock import MockBedrockRuntimeClient
from app.core.config import Settings


class FakeBedrockRuntimeClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def converse(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return {
            "output": {
                "message": {
                    "content": [
                        {"text": "Respuesta generada."},
                    ]
                }
            },
            "usage": {
                "inputTokens": 10,
                "outputTokens": 5,
            },
        }


def test_bedrock_client_uses_converse_api() -> None:
    runtime = FakeBedrockRuntimeClient()
    settings = Settings(
        bedrock_model_id="eu.amazon.nova-micro-v1:0",
        aws_region="eu-south-2",
    )
    client = BedrockClient(client=runtime, settings=settings)

    response = client.generate("Pregunta", "Sistema")

    assert response.text == "Respuesta generada."
    assert response.model_id == "eu.amazon.nova-micro-v1:0"
    assert response.input_tokens == 10
    assert response.output_tokens == 5
    assert runtime.calls[0]["modelId"] == "eu.amazon.nova-micro-v1:0"
    assert runtime.calls[0]["messages"] == [{"role": "user", "content": [{"text": "Pregunta"}]}]
    assert runtime.calls[0]["system"] == [{"text": "Sistema"}]


def test_mock_bedrock_runtime_returns_converse_shape_with_usage() -> None:
    runtime = MockBedrockRuntimeClient()

    response = runtime.converse(
        modelId="mock.amazon.nova-micro-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": "Consulta de la persona usuaria:\nregistro\n\n[1] Fuente"}],
            }
        ],
        system=[{"text": "Sistema"}],
        inferenceConfig={"maxTokens": 100, "temperature": 0},
    )

    content = response["output"]["message"]["content"]
    usage = response["usage"]
    assert response["output"]["message"]["role"] == "assistant"
    assert content[0]["text"].startswith("Respuesta mock local:")
    assert "[1]" in content[0]["text"]
    assert response["stopReason"] == "end_turn"
    assert usage["inputTokens"] > 0
    assert usage["outputTokens"] > 0
    assert usage["totalTokens"] == usage["inputTokens"] + usage["outputTokens"]
    assert response["metrics"]["latencyMs"] == 1


def test_mock_bedrock_runtime_is_deterministic() -> None:
    runtime = MockBedrockRuntimeClient()
    request = {
        "modelId": "mock.amazon.nova-micro-v1:0",
        "messages": [{"role": "user", "content": [{"text": "Pregunta"}]}],
    }

    assert runtime.converse(**request) == runtime.converse(**request)
