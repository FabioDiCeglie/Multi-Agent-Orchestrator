from __future__ import annotations

from pathlib import Path

import yaml

from config.schema import OrchestratorConfig


class ConfigLoader:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def load(self) -> OrchestratorConfig:
        data = yaml.safe_load(self._path.read_text())
        return OrchestratorConfig(**data["orchestrator"])
