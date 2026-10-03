from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter

from backend.pdf_utils import compute_sheets, make_print_pdf, parse_pages, validate_pdf


def pdf_file(path, pages=4):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=100, height=100)
    with open(path, "wb") as f:
        writer.write(f)


def test_parse_pages_all_ranges_and_order():
    assert parse_pages("all", 4) == [0, 1, 2, 3]
    assert parse_pages("1, 3-4", 5) == [0, 2, 3]
    assert parse_pages("4,2", 4) == [3, 1]


@pytest.mark.parametrize("spec", ["0", "1-5", "3-2", "one", "1,,2"])
def test_parse_pages_rejects_bad_ranges(spec):
    with pytest.raises(ValueError):
        parse_pages(spec, 4)


def test_validate_pdf_and_invalid_pdf(tmp_path):
    source = tmp_path / "source.pdf"
    pdf_file(source, 3)
    assert validate_pdf(source) == 3
    bad = tmp_path / "bad.pdf"
    bad.write_text("not a pdf")
    with pytest.raises(ValueError, match="Invalid PDF"):
        validate_pdf(bad)


def test_make_print_pdf_selects_pages_and_returns_count(tmp_path):
    source, destination = tmp_path / "source.pdf", tmp_path / "out" / "print.pdf"
    pdf_file(source, 5)
    assert make_print_pdf(source, destination, {"pages": "2,4-5"}) == 3
    assert len(PdfReader(destination).pages) == 3


def test_sheets_for_simplex_duplex_and_copies():
    assert compute_sheets(5, "single") == 5
    assert compute_sheets(5, "double") == 3
    assert compute_sheets(5, "duplex", 2) == 6
    with pytest.raises(ValueError):
        compute_sheets(1, "single", 0)
