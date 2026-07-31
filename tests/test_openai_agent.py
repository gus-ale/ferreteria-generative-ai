from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.config import Settings
from app.schemas.chat import ToolExecution
from app.services.agent import AgentService
from app.services.tools import ToolResult


class FakeResponses:
    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self._responses = responses
        self.calls: list[dict] = []

    async def create(self, **kwargs) -> SimpleNamespace:
        self.calls.append(kwargs)
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_openai_agent_executes_function_call_and_returns_final_answer():
    function_call = SimpleNamespace(
        type="function_call",
        name="search_products",
        arguments='{"query":"martillo","limit":5}',
        call_id="call_123",
    )
    responses = FakeResponses(
        [
            SimpleNamespace(
                id="resp_tool",
                _request_id="req_tool",
                output=[function_call],
                output_text="",
            ),
            SimpleNamespace(
                id="resp_final",
                _request_id="req_final",
                output=[],
                output_text="Hay 18 martillos disponibles.",
            ),
        ]
    )
    client = SimpleNamespace(responses=responses)
    tool_executor = SimpleNamespace(
        definitions=[{"type": "function", "name": "search_products"}],
        serialize=lambda result: '{"products":[{"name":"Martillo","stock":18}]}',
    )
    service = AgentService(
        session=None,
        tool_executor=tool_executor,
        settings=Settings(
            ai_provider="openai",
            openai_api_key="test-key",
            openai_model="test-model",
            auto_create_tables=False,
            seed_demo_data=False,
        ),
        openai_client=client,
    )
    service._execute_and_record = AsyncMock(
        return_value=ToolResult(
            output={"products": [{"name": "Martillo", "stock": 18}]},
            execution=ToolExecution(
                name="search_products",
                arguments={"query": "martillo", "limit": 5},
                result_summary="1 product(s) found",
            ),
            citations=[],
        )
    )

    result = await service._run_openai(
        "conversation-123",
        [SimpleNamespace(role="user", content="¿Hay martillos?")],
    )

    assert result.answer == "Hay 18 martillos disponibles."
    assert result.provider == "openai"
    assert result.trace_id == "req_final"
    assert result.tools_used[0].name == "search_products"
    assert len(responses.calls) == 2
    assert responses.calls[0]["model"] == "test-model"
    assert responses.calls[0]["tools"] == tool_executor.definitions
    assert responses.calls[1]["input"][-1] == {
        "type": "function_call_output",
        "call_id": "call_123",
        "output": '{"products":[{"name":"Martillo","stock":18}]}',
    }
