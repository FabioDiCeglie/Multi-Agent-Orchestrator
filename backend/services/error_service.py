from __future__ import annotations

import json


class ErrorService:
    @staticmethod
    def clean_provider_error(exc: Exception) -> str:
        """Extract a human-readable message from provider/LiteLLM errors."""
        raw = getattr(exc, "message", None) or str(exc)
        if " - " not in raw:
            return raw
        try:
            body = json.loads(raw.split(" - ", 1)[1])
            return body.get("error", {}).get("message") or raw
        except (json.JSONDecodeError, AttributeError):
            return raw
