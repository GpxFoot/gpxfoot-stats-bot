import re
from playwright.sync_api import sync_playwright
from src.config import ABOUT_URL, CHANNEL_URL, SHORTS_URL
from src.numbers import clean_text, find_number, parse_compact_number


def accept_cookies(page) -> None:
    for label in ("Tout accepter", "Accept all", "J'accepte", "I agree", "Tout refuser", "Reject all"):
        try:
            button = page.get_by_role("button", name=re.compile(re.escape(label), re.IGNORECASE))
            if button.count():
                button.first.click(timeout=2000)
                page.wait_for_timeout(1000)
                return
        except Exception:
            pass


def body_text(page) -> str:
    return clean_text(page.locator("body").inner_text())


def get_subscribers(page) -> int | None:
    page.goto(CHANNEL_URL, wait_until="domcontentloaded", timeout=60000)
    accept_cookies(page)
    page.wait_for_timeout(4000)
    for selector in ("#subscriber-count", "yt-formatted-string#subscriber-count", "[aria-label*='abonné']", "[aria-label*='subscriber']"):
        try:
            locator = page.locator(selector)
            if locator.count():
                raw = locator.first.get_attribute("aria-label") or locator.first.inner_text()
                parsed = parse_compact_number(raw)
                if parsed is not None:
                    return parsed
        except Exception:
            pass
    return find_number(body_text(page), ("abonnés", "abonné", "subscribers", "subscriber"))


def get_total_views(page) -> int | None:
    page.goto(ABOUT_URL, wait_until="domcontentloaded", timeout=60000)
    accept_cookies(page)
    page.wait_for_timeout(4000)
    text = body_text(page)
    candidates = []
    for pattern in (
        r"(\d[\d\s.,]*\s*[kKmMbB]?)\s+(?:vues|views)",
        r"(?:vues|views)\s*[:\-]?\s*(\d[\d\s.,]*\s*[kKmMbB]?)",
    ):
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = parse_compact_number(match.group(1))
            if value is not None:
                candidates.append(value)
    return max(candidates) if candidates else None


def get_latest_short(page) -> dict:
    page.goto(SHORTS_URL, wait_until="domcontentloaded", timeout=60000)
    accept_cookies(page)
    page.wait_for_timeout(5000)
    cards = page.locator("ytd-rich-item-renderer, ytd-rich-grid-media")
    for index in range(min(cards.count(), 30)):
        card = cards.nth(index)
        try:
            link = card.locator('a[href*="/shorts/"]').first
            href = link.get_attribute("href")
            if not href:
                continue
            url = f"https://www.youtube.com{href}" if href.startswith("/") else href
            title = link.get_attribute("title") or link.get_attribute("aria-label")
            if not title:
                title_locator = card.locator("#video-title, a#video-title-link")
                if title_locator.count():
                    title = title_locator.first.get_attribute("title") or title_locator.first.inner_text()
            views = find_number(clean_text(card.inner_text()), ("vues", "vue", "views", "view"))
            match = re.search(r"/shorts/([^?&/]+)", url)
            return {
                "latest_title": clean_text(title) or "Titre indisponible",
                "latest_views": views,
                "latest_url": url,
                "latest_video_id": match.group(1) if match else url,
            }
        except Exception:
            continue
    raise RuntimeError("Impossible d'identifier le Short le plus récent.")


def collect_public_stats() -> dict:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(locale="fr-FR", timezone_id="Europe/Paris", viewport={"width": 1440, "height": 1200})
        page = context.new_page()
        try:
            return {
                "subscribers": get_subscribers(page),
                "total_views": get_total_views(page),
                **get_latest_short(page),
            }
        finally:
            browser.close()
