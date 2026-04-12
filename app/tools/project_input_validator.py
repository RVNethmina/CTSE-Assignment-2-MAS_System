from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(slots=True)
class ValidationResult:
    brief_path_exists: bool
    project_path_exists: bool
    project_is_directory: bool
    project_is_git_repo: bool
    top_level_items: list[str]
    likely_stack: str
    issues: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a serializable dictionary representation of the result."""
        return asdict(self)


def detect_likely_stack(project_path: Path) -> str:
    """
    Detect a likely tech stack from common files in the project root.

    Returns:
        A short descriptive stack label.
    """
    indicators = {
        "package.json": "Node.js / JavaScript or TypeScript",
        "requirements.txt": "Python",
        "pyproject.toml": "Python",
        "pom.xml": "Java / Maven",
        "build.gradle": "Java / Gradle",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "docker-compose.yml": "Containerized application",
        "docker-compose.yaml": "Containerized application",
    }

    found: list[str] = []
    for filename, label in indicators.items():
        if (project_path / filename).exists():
            found.append(label)

    if not found:
        return "Unknown"

    # Remove duplicates while keeping order.
    unique_found: list[str] = []
    for item in found:
        if item not in unique_found:
            unique_found.append(item)

    return " + ".join(unique_found)


def validate_project_inputs(brief_path: str, project_path: str) -> ValidationResult:
    """
    Validate the existence and basic structure of the provided assignment brief and project path.

    Args:
        brief_path: Path to the assignment brief file.
        project_path: Path to the local project directory.

    Returns:
        ValidationResult containing validation status, detected stack, and issues.
    """
    brief = Path(brief_path)
    project = Path(project_path)

    issues: list[str] = []

    brief_path_exists = brief.exists()
    if not brief_path_exists:
        issues.append(f"Brief file not found: {brief_path}")

    project_path_exists = project.exists()
    if not project_path_exists:
        issues.append(f"Project path not found: {project_path}")

    project_is_directory = project.is_dir()
    if project_path_exists and not project_is_directory:
        issues.append(f"Project path is not a directory: {project_path}")

    top_level_items: list[str] = []
    if project_path_exists and project_is_directory:
        try:
            top_level_items = sorted(item.name for item in project.iterdir())
            if not top_level_items:
                issues.append("Project directory is empty.")
        except OSError as exc:
            issues.append(f"Unable to inspect project directory: {exc}")

    project_is_git_repo = (project / ".git").exists() if project_is_directory else False

    likely_stack = "Unknown"
    if project_path_exists and project_is_directory:
        likely_stack = detect_likely_stack(project)

    return ValidationResult(
        brief_path_exists=brief_path_exists,
        project_path_exists=project_path_exists,
        project_is_directory=project_is_directory,
        project_is_git_repo=project_is_git_repo,
        top_level_items=top_level_items,
        likely_stack=likely_stack,
        issues=issues,
    )