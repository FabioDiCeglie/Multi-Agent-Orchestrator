from __future__ import annotations

import re
from typing import Any


class PipelineService:
    @staticmethod
    def clean_executor(text: str) -> str:
        text = re.sub(
            r"<search[\s\S]*?</search>", "", text, flags=re.IGNORECASE,
        )
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def extract_tool_calls(parts: list) -> list[str]:
        return [
            p.function_call.name
            for p in parts
            if getattr(p, "function_call", None)
        ]

    @staticmethod
    def extract_tool_calls_detailed(parts: list) -> list[dict[str, Any]]:
        return [
            {"name": p.function_call.name, "args": dict(p.function_call.args)}
            for p in parts
            if getattr(p, "function_call", None)
        ]

    @staticmethod
    def shape_planner_step(iteration: int, text: str) -> dict[str, Any]:
        return {
            "type": "step",
            "iteration": iteration,
            "author": "planner",
            "text": text,
        }

    @staticmethod
    def shape_executor_step(
        iteration: int,
        text: str,
        tool_calls: list[dict[str, Any]],
        mcp_urls: list[str],
    ) -> dict[str, Any]:
        step: dict[str, Any] = {
            "type": "step",
            "iteration": iteration,
            "author": "executor",
            "text": PipelineService.clean_executor(text),
        }
        if tool_calls:
            step["toolCalls"] = tool_calls
            step["mcpUrls"] = mcp_urls
        return step

    @staticmethod
    def shape_critic_step(iteration: int, text: str) -> dict[str, Any]:
        verdict = "APPROVED" if "APPROVED" in text else "REVISE"
        return {
            "type": "step",
            "iteration": iteration,
            "author": "critic",
            "text": text,
            "verdict": verdict,
        }

    @staticmethod
    def shape_summarizer_step(iteration: int, text: str) -> dict[str, Any]:
        return {
            "type": "step",
            "iteration": iteration,
            "author": "summarizer",
            "text": text,
        }

    @staticmethod
    def shape_final_step(result: str, iterations: int) -> dict[str, Any]:
        return {
            "type": "final",
            "result": result,
            "iterations": iterations,
        }

    @staticmethod
    def shape_error_step(message: str, iteration: int) -> dict[str, Any]:
        return {
            "type": "error",
            "message": message,
            "iteration": iteration,
        }
