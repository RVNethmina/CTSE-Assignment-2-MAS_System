from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(slots=True)
class ParsedBriefResult:
    source_path: str
    detected_format: str
    content: str
    content_preview: str
    issues: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a serializable dictionary representation."""
        return asdict(self)


def normalize_whitespace(text: str) -> str:
    """Collapse excessive blank lines and trailing spaces."""
    cleaned_lines = [line.strip() for line in text.splitlines()]
    compact: list[str] = []
    previous_blank = False

    for line in cleaned_lines:
        is_blank = not line
        if is_blank and previous_blank:
            continue
        compact.append(line)
        previous_blank = is_blank

    return "\n".join(compact).strip()


def read_text_file(path: Path) -> str:
    """Read a UTF-8 text-based brief file."""
    return path.read_text(encoding="utf-8")


def read_pdf_file(path: Path) -> str:
    """Extract text from a PDF brief using pypdf."""
    reader = PdfReader(str(path))
    pages_text: list[str] = []

    for page in reader.pages:
        extracted = page.extract_text() or ""
        pages_text.append(extracted)

    return "\n".join(pages_text)


def parse_assignment_brief(source_path: str) -> ParsedBriefResult:
    """
    Read an assignment brief from PDF, TXT, or Markdown and return normalized text.

    Args:
        source_path: Path to the assignment brief file.

    Returns:
        ParsedBriefResult containing extracted text, preview, and any issues.
    """
    path = Path(source_path)
    issues: list[str] = []

    if not path.exists():
        return ParsedBriefResult(
            source_path=source_path,
            detected_format="unknown",
            content="",
            content_preview="",
            issues=[f"Brief file not found: {source_path}"],
        )

    suffix = path.suffix.lower()
    detected_format = suffix.lstrip(".") or "unknown"

    try:
        if suffix == ".pdf":
            raw_text = read_pdf_file(path)
        elif suffix in {".txt", ".md"}:
            raw_text = read_text_file(path)
        else:
            issues.append(
                f"Unsupported brief format '{suffix}'. Attempting text read anyway."
            )
            raw_text = read_text_file(path)

        content = normalize_whitespace(raw_text)

        if not content:
            issues.append("Brief content was empty after parsing.")

        preview = content[:1200]

        return ParsedBriefResult(
            source_path=str(path),
            detected_format=detected_format,
            content=content,
            content_preview=preview,
            issues=issues,
        )

    except Exception as exc:
        issues.append(f"Failed to parse brief: {exc}")
        return ParsedBriefResult(
            source_path=str(path),
            detected_format=detected_format,
            content="",
            content_preview="",
            issues=issues,
        )