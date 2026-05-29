from __future__ import annotations

import json

import httpx
import pytest

from app.services.perplexity_client import (
    PerplexityClient,
    _extract_json_object,
    build_consultant_system_prompt,
)


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_perplexity_client_respond_action():
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["model"] == "sonar-pro"
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][-1]["role"] == "user"
        body = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "action": "respond",
                                "reason": "",
                                "text": "Здравствуйте. Подскажите марку и модель.",
                                "manager_note": "",
                            },
                            ensure_ascii=False,
                        )
                    }
                }
            ]
        }
        return httpx.Response(200, json=body)

    async with httpx.AsyncClient(transport=_mock_transport(handler)) as http_client:
        client = PerplexityClient(api_key="test", http_client=http_client)
        result = await client.generate(
            system_prompt="sys",
            history=[{"role": "user", "content": "Здравствуйте"}],
            user_text="Хочу авто",
        )

    assert result.action == "respond"
    assert "марку" in result.text


@pytest.mark.asyncio
async def test_perplexity_client_escalate_action_with_citations():
    def handler(request: httpx.Request) -> httpx.Response:
        body = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "action": "escalate",
                                "reason": "tech_low_confidence",
                                "text": "Передаю запрос профильному менеджеру.",
                                "manager_note": "вопрос про панораму",
                            },
                            ensure_ascii=False,
                        )
                    }
                }
            ],
            "citations": ["https://drom.ru/x"],
        }
        return httpx.Response(200, json=body)

    async with httpx.AsyncClient(transport=_mock_transport(handler)) as http_client:
        client = PerplexityClient(api_key="test", http_client=http_client)
        result = await client.generate(system_prompt="sys", history=[], user_text="люк есть?")

    assert result.action == "escalate"
    assert result.reason == "tech_low_confidence"
    assert result.citations == ["https://drom.ru/x"]


@pytest.mark.asyncio
async def test_perplexity_client_timeout_returns_escalate(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    async with httpx.AsyncClient(transport=_mock_transport(handler)) as http_client:
        client = PerplexityClient(
            api_key="test", http_client=http_client, max_retries=1
        )
        # Не ждём реальные backoff-задержки в тесте.
        monkeypatch.setattr("app.services.perplexity_client.asyncio.sleep", _noop_sleep)
        result = await client.generate(system_prompt="sys", history=[], user_text="x")

    assert result.action == "escalate"
    assert result.reason == "timeout"


@pytest.mark.asyncio
async def test_perplexity_client_http_4xx_no_retry():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(400, json={"error": "bad"})

    async with httpx.AsyncClient(transport=_mock_transport(handler)) as http_client:
        client = PerplexityClient(api_key="test", http_client=http_client, max_retries=3)
        result = await client.generate(system_prompt="sys", history=[], user_text="x")

    assert result.action == "escalate"
    assert result.reason == "http_400"
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_perplexity_client_malformed_json_in_content():
    def handler(request: httpx.Request) -> httpx.Response:
        body = {"choices": [{"message": {"content": "это не json"}}]}
        return httpx.Response(200, json=body)

    async with httpx.AsyncClient(transport=_mock_transport(handler)) as http_client:
        client = PerplexityClient(api_key="test", http_client=http_client)
        result = await client.generate(system_prompt="sys", history=[], user_text="x")

    assert result.action == "escalate"
    assert result.reason == "invalid_json"


@pytest.mark.asyncio
async def test_perplexity_client_not_configured_returns_escalate():
    client = PerplexityClient(api_key="")
    result = await client.generate(system_prompt="sys", history=[], user_text="x")
    assert result.action == "escalate"
    assert result.reason == "not_configured"


@pytest.mark.asyncio
async def test_perplexity_client_http_429_returns_escalate():
    """Rate limit должен приводить к escalate с понятным reason (B.1 requirement)."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(429, json={"error": "rate limited"})

    async with httpx.AsyncClient(transport=_mock_transport(handler)) as http_client:
        client = PerplexityClient(api_key="test", http_client=http_client, max_retries=1)
        result = await client.generate(system_prompt="sys", history=[], user_text="x")

    assert result.action == "escalate"
    assert result.reason == "http_429"
    # 429 ретраится (в отличие от других 4xx), поэтому 2 вызова при max_retries=1
    assert calls["n"] == 2


def test_build_consultant_system_prompt_includes_collected_and_pending():
    prompt = build_consultant_system_prompt(
        collected={"brand_model": "Toyota Camry", "budget_rub": 2500000},
        pending_field_question="Какой кузов?",
        calc_hint="Мощность 220 л.с. — вне контура.",
    )
    assert "Toyota Camry" in prompt
    assert "Какой кузов?" in prompt
    assert "вне контура" in prompt
    assert "Автоподбор" in prompt


def test_extract_json_object_handles_code_fence():
    raw = "```json\n{\"action\":\"respond\",\"text\":\"ok\"}\n```"
    obj = _extract_json_object(raw)
    assert obj == {"action": "respond", "text": "ok"}


def test_extract_json_object_finds_embedded_object():
    raw = (
        "Sure, here it is: "
        '{"action":"escalate","reason":"low_confidence","text":"..."} thanks'
    )
    obj = _extract_json_object(raw)
    assert obj["action"] == "escalate"


async def _noop_sleep(*_a, **_kw):  # pragma: no cover - вспомогательная заглушка
    return None
