import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.services import llm_service


class LlmServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_opencode_sends_chat_completions_request_with_json_mode(self):
        response = Mock()
        response.json.return_value = {
            "choices": [{"message": {"content": "{\"ok\": true}"}}]
        }
        response.raise_for_status = Mock()
        client = Mock()
        client.post = AsyncMock(return_value=response)
        client_context = Mock()
        client_context.__aenter__ = AsyncMock(return_value=client)
        client_context.__aexit__ = AsyncMock(return_value=None)

        with (
            patch.object(llm_service, "OPENCODE_API_KEY", "test-key"),
            patch.object(llm_service, "OPENCODE_MODEL", "gpt-6-luna"),
            patch.object(llm_service, "OPENCODE_BASE_URL", "https://opencode.ai/inference/go"),
            patch("app.services.llm_service.httpx.AsyncClient", return_value=client_context),
        ):
            result = await llm_service.generate_with_opencode("prompt", json_mode=True)

        self.assertEqual(result, "{\"ok\": true}")
        args, kwargs = client.post.call_args
        self.assertEqual(
            args[0],
            "https://opencode.ai/inference/go/openai/v1/chat/completions",
        )
        self.assertEqual(kwargs["json"]["model"], "gpt-6-luna")
        self.assertEqual(kwargs["json"]["response_format"], {"type": "json_object"})
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertIn("x-opencode-session", kwargs["headers"])

    async def test_provider_override_is_scoped_to_context(self):
        with patch(
            "app.services.llm_service.generate_with_opencode",
            new=AsyncMock(return_value="generated"),
        ) as generate:
            with llm_service.use_llm_provider("opencode_go", session_id="stable-session"):
                self.assertEqual(await llm_service.generate_text("prompt"), "generated")
            self.assertEqual(llm_service._active_llm_provider(), llm_service.LLM_PROVIDER)

        generate.assert_awaited_once_with(prompt="prompt", json_mode=True)


if __name__ == "__main__":
    unittest.main()
