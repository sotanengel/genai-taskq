from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class ProviderResult:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class Provider(Protocol):
    def generate(self, prompt: str, **opts: object) -> ProviderResult: ...
