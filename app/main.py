from __future__ import annotations

import argparse
import json

from app.graph.workflow import build_workflow
from app.models.state import ProjectState
from app.utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Project Rescue MAS")
    parser.add_argument(
        "--brief",
        required=True,
        help="Path to the assignment brief file.",
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to the local project folder.",
    )
    parser.add_argument(
        "--request",
        default="Analyze this project against the brief and identify missing work.",
        help="User request for the MAS.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the initial Project Rescue MAS workflow."""
    logger = setup_logger()
    args = parse_args()

    initial_state: ProjectState = {
        "user_request": args.request,
        "brief_path": args.brief,
        "project_path": args.project,
    }

    logger.info("Starting Project Rescue MAS workflow.")
    workflow = build_workflow()
    final_state = workflow.invoke(initial_state)

    print("\n=== FINAL STATE ===")
    print(json.dumps(final_state, indent=2, default=str))


if __name__ == "__main__":
    main()