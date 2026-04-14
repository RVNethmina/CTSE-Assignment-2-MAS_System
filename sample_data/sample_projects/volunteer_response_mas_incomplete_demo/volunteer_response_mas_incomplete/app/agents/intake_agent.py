from pathlib import Path
import json

def intake_agent(input_path: str) -> list[dict]:
    """Read incoming volunteer requests from a local JSON file."""
    data = Path(input_path).read_text(encoding="utf-8")
    return json.loads(data)
