from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from config.loader import ConfigLoader
from config.schema import AgentConfig, OrchestratorConfig


def test_orchestrator_config_defaults() -> None:
    cfg = OrchestratorConfig(goal="Research LLM frameworks")

    assert cfg.goal == "Research LLM frameworks"
    assert cfg.max_iterations == 2
    assert cfg.agent.model == "claude-sonnet-4-6"
    assert cfg.agent.temperature == 0.2


def test_orchestrator_config_with_agent_block() -> None:
    cfg = OrchestratorConfig(
        goal="Compare tools",
        max_iterations=5,
        agent=AgentConfig(model="gpt-4o", temperature=0.5),
    )

    assert cfg.max_iterations == 5
    assert cfg.agent.model == "gpt-4o"
    assert cfg.agent.temperature == 0.5


def test_orchestrator_config_rejects_invalid_iterations() -> None:
    with pytest.raises(ValidationError):
        OrchestratorConfig(goal="test", max_iterations=0)


def test_config_loader_reads_yaml(tmp_path: Path) -> None:
    yaml_path = tmp_path / "goal.yaml"
    yaml_path.write_text(
        yaml.dump(
            {
                "orchestrator": {
                    "goal": "Research MCP servers",
                    "max_iterations": 3,
                    "agent": {"model": "claude-sonnet-4-6", "temperature": 0.1},
                }
            }
        ),
        encoding="utf-8",
    )

    cfg = ConfigLoader(yaml_path).load()

    assert cfg.goal == "Research MCP servers"
    assert cfg.max_iterations == 3
    assert cfg.agent.temperature == 0.1


def test_config_loader_reads_example_file() -> None:
    cfg = ConfigLoader("examples/research_goal.yaml").load()

    assert "LLM frameworks" in cfg.goal
    assert cfg.max_iterations == 3
