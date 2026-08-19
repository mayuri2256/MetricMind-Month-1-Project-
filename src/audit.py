from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_audit_event(event: dict[str, Any], path: str = "data/audit_log.jsonl") -> None:
    """Append one governed-query event to a JSONL audit file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, default=str) + "\n")
