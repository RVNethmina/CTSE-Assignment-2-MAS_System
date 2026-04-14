from pathlib import Path
import json

def request_reader(path: str) -> list[dict]:
    """Load structured volunteer requests from a JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
