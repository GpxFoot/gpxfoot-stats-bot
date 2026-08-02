from src.numbers import format_change, format_number


def delta(current: int | None, previous: int | None) -> int | None:
    return None if current is None or previous is None else current - previous


def diagnostic(change: int | None) -> str:
    if change is None:
        return "Premier relevé ou compteur public indisponible. Ce rapport servira de point zéro."
    if change >= 30000:
        return "Très forte journée. La chaîne bénéficie d'une distribution puissante."
    if change >= 10000:
        return "Bonne dynamique. La chaîne conserve une croissance solide sur 24 heures."
    if change > 0:
        return "Progression réelle mais plus calme. Surveille surtout la vitesse du dernier Short."
    return "Aucune hausse détectée publiquement, ou retard de mise à jour YouTube."


def build_report(current: dict, previous: dict | None) -> str:
    previous = previous or {}
    subscriber_change = delta(current.get("subscribers"), previous.get("subscribers"))
    total_change = delta(current.get("total_views"), previous.get("total_views"))
    short_change = None
    if previous and current.get("latest_video_id") == previous.get("latest_video_id"):
        short_change = delta(current.get("latest_views"), previous.get("latest_views"))
    return f"""🎬 GPXFOOT DAILY REPORT

Abonnés : {format_number(current.get('subscribers'))}
Évolution depuis hier : {format_change(subscriber_change)}

Vues totales : {format_number(current.get('total_views'))}
Évolution depuis hier : {format_change(total_change)}

Dernier Short : “{current.get('latest_title', 'Titre indisponible')}”
Vues : {format_number(current.get('latest_views'))}
Progression depuis hier : {format_change(short_change)}

Vitesse actuelle :
{format_change(total_change)} vues gagnées sur la chaîne en 24 h

Diagnostic :
{diagnostic(total_change)}

Dernier Short :
{current.get('latest_url', 'indisponible')}

Relevé :
{current.get('timestamp', 'indisponible')}
"""
