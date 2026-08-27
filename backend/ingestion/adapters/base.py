"""Base class for every external data-source adapter.

Adapters MUST:
- Be side-effect free until an explicit ``fetch`` / ``sync`` call.
- Return primitive dicts (never raw HTML / vendor objects).
- Never leak vendor-specific fields to the API layer.

In the foundation phase every concrete adapter simply raises
``NotImplementedError`` — this is intentional and validated by tests.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class AdapterStatus:
    key: str
    name: str
    homepage: str
    implemented: bool


class BaseAdapter:
    key: str = ""
    name: str = ""
    homepage: str = ""

    @classmethod
    def status(cls) -> AdapterStatus:
        return AdapterStatus(
            key=cls.key,
            name=cls.name,
            homepage=cls.homepage,
            implemented=False,
        )

    async def fetch(self, **kwargs: Any) -> list[dict]:
        raise NotImplementedError(
            f"{self.__class__.__name__}.fetch is a placeholder. "
            "Implement in a future ingestion phase."
        )
