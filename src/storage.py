import json
from pathlib import Path

DATA_DIR = Path("data")
LATEST_JSON = DATA_DIR / "latest_stats.json"
REPORT_FILE = Path("report.md")


def load_previous_stats() -> dict | None:
    if not LATEST_JSON.exists():
        return None
    try:
        return json.loads(LATEST_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def save_outputs(stats: dict, report: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_FILE.write_text(report, encoding="utf-8")
