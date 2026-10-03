"""Small domain models shared by the backend foundation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PrintSpec:
    pages: str = "all"
    colour: str = "colour"
    sides: str = "single"
    flip: str = "long"
    copies: int = 1


@dataclass(frozen=True)
class Job:
    id: str
    original_name: str
    original_path: str
    print_path: str
    pages: str
    colour: str
    sides: str
    flip: str
    copies: int
    page_count: int | None
    status: str
    created_at: datetime | str
    claimed_at: datetime | str | None = None
    updated_at: datetime | str | None = None
    error: str | None = None

    def __getitem__(self, key: str) -> Any:
        """Allow the model to be used like the mapping returned by SQLite."""
        return getattr(self, key)

    def to_dict(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}

    @classmethod
    def from_row(cls, row: Any) -> "Job":
        values = dict(row)
        return cls(**values)
