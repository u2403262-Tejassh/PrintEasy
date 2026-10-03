"""PDF validation, page selection, and print-ready PDF creation."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter

_RANGE = re.compile(r"^(\d+)(?:-(\d+))?$")


def parse_pages(spec: str | None, total: int) -> list[int]:
    """Return zero-based page indexes for a 1-based selection like ``1,3-5``."""
    if total < 1:
        raise ValueError("PDF must contain at least one page")
    if spec is None or not str(spec).strip() or str(spec).strip().lower() == "all":
        return list(range(total))
    result: list[int] = []
    for part in str(spec).replace(" ", "").split(","):
        match = _RANGE.fullmatch(part)
        if not match:
            raise ValueError(f"Invalid page selection: {part!r}")
        first, last = int(match.group(1)), int(match.group(2) or match.group(1))
        if first < 1 or last < first or last > total:
            raise ValueError(f"Page selection {part!r} is outside 1-{total}")
        result.extend(range(first - 1, last))
    if not result:
        raise ValueError("Page selection cannot be empty")
    return result


def validate_pdf(src: str | Path) -> int:
    """Validate a readable PDF and return its page count."""
    try:
        reader = PdfReader(str(src), strict=True)
        count = len(reader.pages)
    except Exception as exc:  # pypdf has several parser-specific exceptions
        raise ValueError(f"Invalid PDF: {exc}") from exc
    if count == 0:
        raise ValueError("PDF must contain at least one page")
    return count


def _value(spec: Any, name: str, default: Any = None) -> Any:
    if isinstance(spec, dict):
        return spec.get(name, default)
    return getattr(spec, name, default)


def make_print_pdf(src: str | Path, dst: str | Path, spec: Any) -> int:
    """Write the selected pages to ``dst`` and return the number of pages."""
    reader = PdfReader(str(src), strict=True)
    selection = spec if isinstance(spec, str) else _value(
        spec, "pages", _value(spec, "page_spec", "all")
    )
    indexes = parse_pages(selection, len(reader.pages))
    writer = PdfWriter()
    for index in indexes:
        writer.add_page(reader.pages[index])
    destination = Path(dst)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        writer.write(handle)
    return len(indexes)


def compute_sheets(page_count: int, sides: str | bool = "single", copies: int = 1) -> int:
    """Compute physical sheets: duplex uses two pages per sheet, per copy."""
    if page_count < 0 or copies < 1:
        raise ValueError("page_count must be non-negative and copies must be positive")
    duplex = sides is True or str(sides).lower() in {"double", "duplex", "two-sided"}
    return ((page_count + 1) // 2 if duplex else page_count) * copies


# Friendly aliases for callers that use either wording from the specification.
sheets_for = compute_sheets
calculate_sheets = compute_sheets
