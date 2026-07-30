from __future__ import annotations

import json as json_mod
import traceback
from typing import Any, AsyncIterator

from orchestrator.base import BaseOrchestrator


class APIOrchestrator(BaseOrchestrator):
    @staticmethod
    def _clean_error(exc: Exception) -> str:
        raw = getattr(exc, "message", None) or str(exc)
        if " - " not in raw:
            return raw
        try:
            body = json_mod.loads(raw.split(" - ", 1)[1])
            return body.get("error", {}).get("message") or raw
        except (json_mod.JSONDecodeError, AttributeError):
            return raw

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
                "message": self._clean_error(exc),
                "iteration": self.iteration,
            }
            return

        yield {
            "type": "final",
            "result": self.summary_text or "(no result produced)",
            "iterations": self.iteration,
        }
