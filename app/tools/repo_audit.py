from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class RepoAuditResult:
    project_path: str
    total_files: int
    total_directories: int
    top_level_items: list[str]
    detected_artifacts: list[str]
    important_files: list[str]
    directory_summary: dict[str, int]
    agent_file_count: int
    tool_file_count: int
    test_file_count: int
    has_logging_evidence: bool
    has_output_writer_evidence: bool
    issues: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a serializable dictionary representation."""
        return asdict(self)


IMPORTANT_FILENAMES = {
    "README.md": "README",
    "requirements.txt": "Python dependencies",
    "pyproject.toml": "Python project config",
    "package.json": "Node project config",
    "pom.xml": "Maven build file",
    "build.gradle": "Gradle build file",
    "dockerfile": "Dockerfile",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    ".gitignore": "Git ignore file",
}

ARTIFACT_PATTERNS = {
    "tests": ["test", "tests"],
    "documentation": ["docs", "report", "documentation"],
    "source_code": ["src", "app", "lib"],
    "notebooks": [".ipynb"],
    "diagrams": [".png", ".jpg", ".jpeg", ".svg", ".drawio", ".mmd"],
    "configuration": [".json", ".yaml", ".yml", ".toml", ".ini"],
}


def _safe_relative_path(path: Path, root: Path) -> str:
    """Return a path relative to root when possible."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def audit_repository(project_path: str) -> RepoAuditResult:
    """
    Inspect a local project directory and summarize repository evidence.

    Args:
        project_path: Path to the local project directory.

    Returns:
        RepoAuditResult containing counts, detected artifacts, and important files.
    """
    root = Path(project_path)
    issues: list[str] = []

    if not root.exists():
        return RepoAuditResult(
            project_path=project_path,
            total_files=0,
            total_directories=0,
            top_level_items=[],
            detected_artifacts=[],
            important_files=[],
            directory_summary={},
            agent_file_count = 0,
            tool_file_count = 0,
            test_file_count = 0,
            has_logging_evidence = False,
            has_output_writer_evidence = False,
            issues=[f"Project path not found: {project_path}"],
        )

    if not root.is_dir():
        return RepoAuditResult(
            project_path=project_path,
            total_files=0,
            total_directories=0,
            top_level_items=[],
            detected_artifacts=[],
            important_files=[],
            directory_summary={},
            issues=[f"Project path is not a directory: {project_path}"],
        )

    total_files = 0
    total_directories = 0
    important_files: list[str] = []
    detected_artifacts: set[str] = set()
    directory_summary = {
        "source_like_directories": 0,
        "test_like_directories": 0,
        "docs_like_directories": 0,
    }

    agent_file_count = 0
    tool_file_count = 0
    test_file_count = 0
    has_logging_evidence = False
    has_output_writer_evidence = False

    try:
        top_level_items = sorted(item.name for item in root.iterdir())
    except OSError as exc:
        return RepoAuditResult(
            project_path=project_path,
            total_files=0,
            total_directories=0,
            top_level_items=[],
            detected_artifacts=[],
            important_files=[],
            directory_summary={},
            issues=[f"Could not list project directory: {exc}"],
        )

    for path in root.rglob("*"):
        name_lower = path.name.lower()

        if path.is_dir():
            total_directories += 1

            if any(token in name_lower for token in ("src", "app", "lib")):
                directory_summary["source_like_directories"] += 1
                detected_artifacts.add("source_code")

            if any(token in name_lower for token in ("test", "tests")):
                directory_summary["test_like_directories"] += 1
                detected_artifacts.add("tests")

            if any(token in name_lower for token in ("docs", "report", "documentation")):
                directory_summary["docs_like_directories"] += 1
                detected_artifacts.add("documentation")

            continue

        if path.is_file():
            total_files += 1

            if path.name.lower() == "readme.md":
                detected_artifacts.add("documentation")

            if path.name.lower() in {"requirements.txt", "pyproject.toml", "package.json"}:
                detected_artifacts.add("configuration")

            if path.suffix.lower() == ".py":
                detected_artifacts.add("source_code")

            if path.name in IMPORTANT_FILENAMES or name_lower in IMPORTANT_FILENAMES:
                important_files.append(_safe_relative_path(path, root))

            suffix = path.suffix.lower()

            if suffix == ".ipynb":
                detected_artifacts.add("notebooks")
            if suffix in {".png", ".jpg", ".jpeg", ".svg", ".drawio", ".mmd"}:
                detected_artifacts.add("diagrams")
            if suffix in {".json", ".yaml", ".yml", ".toml", ".ini"}:
                detected_artifacts.add("configuration")

            if "test" in name_lower:
                detected_artifacts.add("tests")

            path_parts_lower = [part.lower() for part in path.parts]

            if "agents" in path_parts_lower and path.suffix.lower() == ".py":
                agent_file_count += 1

            if "tools" in path_parts_lower and path.suffix.lower() == ".py":
                tool_file_count += 1

            if "tests" in path_parts_lower or path.name.lower().startswith("test_"):
                test_file_count += 1
                detected_artifacts.add("tests")

            if path.name.lower() in {"logger.py", "logging.py"}:
                has_logging_evidence = True

            if any(keyword in path.name.lower() for keyword in ("writer", "report", "output")):
                has_output_writer_evidence = True

    if "README.md" not in top_level_items:
        issues.append("README.md is missing from the project root.")

    if total_files == 0:
        issues.append("Project contains no files.")

    return RepoAuditResult(
        project_path=str(root),
        total_files=total_files,
        total_directories=total_directories,
        top_level_items=top_level_items,
        detected_artifacts=sorted(detected_artifacts),
        important_files=sorted(set(important_files)),
        directory_summary=directory_summary,
        agent_file_count=agent_file_count,
        tool_file_count=tool_file_count,
        test_file_count=test_file_count,
        has_logging_evidence=has_logging_evidence,
        has_output_writer_evidence=has_output_writer_evidence,
        issues=issues,
    )