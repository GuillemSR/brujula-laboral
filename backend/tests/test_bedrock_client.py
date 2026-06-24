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


def test_bedrock_client_uses_dedicated_bedrock_region(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_boto3_client(service_name: str, **kwargs: object) -> FakeBedrockRuntimeClient:
        captured["service_name"] = service_name
        captured.update(kwargs)
        return FakeBedrockRuntimeClient()

    monkeypatch.setattr("app.ai.bedrock_client.boto3.client", fake_boto3_client)

    BedrockClient(
        settings=Settings(
            aws_region="eu-south-2",
            bedrock_region="eu-west-3",
            bedrock_model_id="eu.amazon.nova-micro-v1:0",
        )
    )

    assert captured["service_name"] == "bedrock-runtime"
    assert captured["region_name"] == "eu-west-3"


def test_bedrock_client_falls_back_to_aws_region(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_boto3_client(service_name: str, **kwargs: object) -> FakeBedrockRuntimeClient:
        captured["service_name"] = service_name
        captured.update(kwargs)
        return FakeBedrockRuntimeClient()

    monkeypatch.setattr("app.ai.bedrock_client.boto3.client", fake_boto3_client)

    BedrockClient(
        settings=Settings(
            aws_region="eu-south-2",
            bedrock_region=None,
            bedrock_model_id="eu.amazon.nova-micro-v1:0",
        )
    )

    assert captured["region_name"] == "eu-south-2"


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
    assert "Orientacion inicial:" in content[0]["text"]
    assert "Siguiente paso:" in content[0]["text"]
    assert "[1]" in content[0]["text"]
    assert response["stopReason"] == "end_turn"
    assert usage["inputTokens"] > 0
    assert usage["outputTokens"] > 0
    assert usage["totalTokens"] == usage["inputTokens"] + usage["outputTokens"]
    assert response["metrics"]["latencyMs"] == 1


def test_mock_bedrock_runtime_does_not_cite_format_instructions_as_sources() -> None:
    runtime = MockBedrockRuntimeClient()

    response = runtime.converse(
        modelId="mock.amazon.nova-micro-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Consulta de la persona usuaria:\n"
                            "despido estando de baja\n\n"
                            "Fuentes RAG disponibles:\n"
                            "Sin fragmentos de apoyo para citar.\n\n"
                            "Instrucciones de formato:\n"
                            "- Si usas una fuente RAG, cita el marcador correspondiente como [1]."
                        )
                    }
                ],
            }
        ],
    )

    content = response["output"]["message"]["content"]
    assert "[1]" not in content[0]["text"]


def test_mock_bedrock_runtime_is_deterministic() -> None:
    runtime = MockBedrockRuntimeClient()
    request = {
        "modelId": "mock.amazon.nova-micro-v1:0",
        "messages": [{"role": "user", "content": [{"text": "Pregunta"}]}],
    }

    assert runtime.converse(**request) == runtime.converse(**request)
