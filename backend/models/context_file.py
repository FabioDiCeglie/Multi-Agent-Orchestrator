from __future__ import annotations

from dataclasses import dataclass

from fastapi import UploadFile


@dataclass(frozen=True)
class ContextFile:
    name: str
    content: str

    @classmethod
    async def from_upload(cls, file: UploadFile) -> ContextFile:
        content = (await file.read()).decode("utf-8", errors="replace")
        return cls(name=file.filename or "file", content=content)

    @classmethod
    async def from_uploads(cls, files: list[UploadFile]) -> list[ContextFile]:
        return [await cls.from_upload(f) for f in files]
