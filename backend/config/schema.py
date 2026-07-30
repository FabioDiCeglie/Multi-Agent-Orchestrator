from __future__ import annotations

from pydantic import BaseModel, Field

DEFAULT_MODEL = "claude-sonnet-4-6"


class AgentConfig(BaseModel):
    model: str = DEFAULT_MODEL


class OrchestratorConfig(BaseModel):
    goal: str
    max_iterations: int = Field(default=2, ge=1, le=20)
    agent: AgentConfig = Field(default_factory=AgentConfig)
