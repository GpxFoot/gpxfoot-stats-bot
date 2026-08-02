import re


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.replace("\u202f", " ").replace("\xa0", " ").split())


def parse_compact_number(value: str | None) -> int | None:
    if not value:
        return None
    text = clean_text(value).lower()
    match = re.search(r"(\d[\d\s.,]*)\s*([kmb])?", text)
    if not match:
        return None
    raw = match.group(1).replace(" ", "")
    suffix = match.group(2)
    try:
        number = float(raw.replace(",", ".")) if suffix else float(re.sub(r"[.,]", "", raw))
    except ValueError:
        return None
    return int(number * {None: 1, "k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[suffix])


def find_number(text: str, keywords: tuple[str, ...]) -> int | None:
    normalized = clean_text(text)
    for keyword in keywords:
        escaped = re.escape(keyword)
        for pattern in (
            rf"(\d[\d\s.,]*\s*[kKmMbB]?)\s+{escaped}",
            rf"{escaped}\s*[:\-]?\s*(\d[\d\s.,]*\s*[kKmMbB]?)",
        ):
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                parsed = parse_compact_number(match.group(1))
                if parsed is not None:
                    return parsed
    return None


def format_number(value: int | None) -> str:
    return "indisponible" if value is None else f"{value:,}".replace(",", " ")


def format_change(value: int | None) -> str:
    if value is None:
        return "indisponible pour le premier relevé"
    return ("+" if value >= 0 else "") + format_number(value)
