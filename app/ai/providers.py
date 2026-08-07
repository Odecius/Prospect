from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DraftGeneration:
    subject: str
    body: str
    safety_notes: list[str]
    provider: str
    model: str
    usage: dict


class MessageDraftProvider(Protocol):
    model: str

    def generate(self, business_context: dict) -> DraftGeneration: ...
