from datetime import datetime
from zoneinfo import ZoneInfo
from src.report import build_report
from src.storage import load_previous_stats, save_outputs
from src.youtube import collect_public_stats


def main() -> None:
    previous = load_previous_stats()
    current = collect_public_stats()
    current["timestamp"] = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    report = build_report(current, previous)
    save_outputs(current, report)
    print(report)


if __name__ == "__main__":
    main()
