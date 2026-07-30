from __future__ import annotations

import traceback
from typing import Any, AsyncIterator

from orchestrator.base import BaseOrchestrator
from services.error_service import ErrorService


class APIOrchestrator(BaseOrchestrator):
    async def run_stream(self) -> AsyncIterator[dict[str, Any]]:
        """Yields one dict per Planner/Executor/Critic step, then a final event."""
        runner, session = await self._create_runner()
        message = self._build_message()

        try:
            async for event in runner.run_async(
                user_id="user", session_id=session.id, new_message=message,
            ):
                author = getattr(event, "author", None)
                if not (event.content and event.content.parts):
                    continue

                tool_calls = self.extract_tool_calls_detailed(
                    event.content.parts,
                )
                text = (event.content.parts[0].text or "").strip()
                if not text:
                    continue

                if author == "planner":
                    self.iteration += 1
                    yield {
                        "type": "step", "iteration": self.iteration,
                        "author": "planner", "text": text,
                    }

                elif author == "executor":
                    clean = self.clean_executor(text)
                    step: dict[str, Any] = {
                        "type": "step", "iteration": self.iteration,
                        "author": "executor", "text": clean,
                    }
                    if tool_calls:
                        step["toolCalls"] = tool_calls
                        step["mcpUrls"] = self.mcp_urls
                    yield step

                elif author == "critic":
                    verdict = "APPROVED" if "APPROVED" in text else "REVISE"
                    yield {
                        "type": "step", "iteration": self.iteration,
                        "author": "critic", "text": text, "verdict": verdict,
                    }

                elif author == "summarizer":
                    self.summary_text = text
                    yield {
                        "type": "step", "iteration": self.iteration,
                        "author": "summarizer", "text": text,
                    }
        except Exception as exc:
            traceback.print_exc()
            yield {
                "type": "error",
                "message": ErrorService.clean_provider_error(exc),
                "iteration": self.iteration,
            }
            return

        yield {
            "type": "final",
            "result": self.summary_text or "(no result produced)",
            "iterations": self.iteration,
        }
