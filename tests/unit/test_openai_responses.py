import json

import httpx
import pytest

from app.ai.openai_responses import OpenAIConfigurationError, OpenAIResponsesClient


def test_responses_request_is_stateless_structured_and_minimized() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {"subject": "Uma ideia", "body": "Olá, podemos conversar?", "safety_notes": []}
                                ),
                            }
                        ],
                    }
                ],
                "usage": {"input_tokens": 50, "output_tokens": 20, "total_tokens": 70},
            },
        )

    client = OpenAIResponsesClient("test-key", "gpt-5.6-luna", 5, 0, 300, httpx.MockTransport(handler))
    result = client.generate(
        {"draft_type": "COMMERCIAL_INTRODUCTION", "company_name": "Empresa Fictícia", "city": "Recife"}
    )
    assert captured["store"] is False
    assert captured["model"] == "gpt-5.6-luna"
    assert captured["max_output_tokens"] == 300
    assert captured["text"]["format"]["type"] == "json_schema"
    assert "tools" not in captured
    assert "Empresa Fictícia" in captured["input"]
    assert result.subject == "Uma ideia"
    assert result.usage == {"input_tokens": 50, "output_tokens": 20, "total_tokens": 70}


def test_missing_key_is_rejected_before_network() -> None:
    client = OpenAIResponsesClient(None, "gpt-5.6-luna", 5, 0, 300)
    with pytest.raises(OpenAIConfigurationError, match="não configurado"):
        client.generate({"company_name": "Empresa"})
