from __future__ import annotations

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    model: str = "gemini-2.5-flash"
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class OrchestratorConfig(BaseModel):
    goal: str
    max_iterations: int = Field(default=5, ge=1, le=20)
    quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
