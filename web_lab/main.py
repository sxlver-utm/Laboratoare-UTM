# Laborator: funcții, metode și importuri pe web
# Student: Bacalu Silviu-Laurentiu
"""Programul principal pentru exercițiile 44–50."""

import argparse
import csv
from datetime import datetime
from urllib.parse import urlparse

import requests

# EXERCIȚIUL 44 — Importarea modulului propriu
import webtools

# EXERCIȚIILE 45 și 47 — Importarea anumitor nume și a constantei
from webtools import DEFAULT_HEADERS, get_title, security_headers

# Dacă am defini aici o altă funcție get_title, definiția nouă ar înlocui
# numele importat în main.py. webtools.get_title ar rămâne accesibilă.


# EXERCIȚIUL 49
def save_csv(base: str) -> None:
    """Salvează verificarea celor trei căi în report.csv."""
    results = webtools.check_paths(base, ["/", "/robots.txt", "/sitemap.xml"])
    with open("report.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["path", "status", "checked_at"])
        for path, status in results.items():
            writer.writerow([path, status if status is not None else "eroare", datetime.now().isoformat()])
    print("Salvat în report.csv")


def main() -> None:
    """Citește URL-ul și execută demonstrațiile și raportul final."""
    # EXERCIȚIUL 48 — Argument pozițional din linia de comandă
    parser = argparse.ArgumentParser(description="Raport despre site-ul laboratorului.")
    parser.add_argument("url", help="Folosește https://cybercor.org")
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https") or parsed.hostname != "cybercor.org" or parsed.path not in ("", "/") or parsed.query or parsed.fragment or parsed.port is not None or parsed.username is not None:
        parser.error("Pentru acest laborator folosește https://cybercor.org sau http://cybercor.org.")

    print("Exercițiul 47 — DEFAULT_HEADERS:", DEFAULT_HEADERS)

    try:
        # EXERCIȚIUL 44 — Apel prin numele modulului
        response = webtools.fetch(args.url)
        print("Exercițiul 44 — Titlu:", webtools.get_title(response.text))

        # EXERCIȚIUL 45 — Apel prin numele importate
        print("Exercițiul 45 — Titlu:", get_title(response.text))
        print("Antete:", security_headers(args.url))
    except requests.RequestException as error:
        print("Demonstrația inițială a eșuat:", error)

    base = f"{parsed.scheme}://{parsed.netloc}"
    save_csv(base)
    webtools.site_report(args.url)


if __name__ == "__main__":
    main()
