from __future__ import annotations

import traceback
from typing import Any, AsyncIterator

from orchestrator.base import BaseOrchestrator
from services.error_service import ErrorService
from services.pipeline_service import PipelineService


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
                    yield PipelineService.shape_planner_step(self.iteration, text)

                elif author == "executor":
                    yield PipelineService.shape_executor_step(
                        self.iteration,
                        text,
                        tool_calls,
                        self.mcp_urls,
                    )

                elif author == "critic":
                    yield PipelineService.shape_critic_step(self.iteration, text)

                elif author == "summarizer":
                    self.summary_text = text
                    yield PipelineService.shape_summarizer_step(self.iteration, text)
        except Exception as exc:
            traceback.print_exc()
            yield PipelineService.shape_error_step(
                ErrorService.clean_provider_error(exc),
                self.iteration,
            )
            return

        yield PipelineService.shape_final_step(
            self.summary_text or "(no result produced)",
            self.iteration,
        )
