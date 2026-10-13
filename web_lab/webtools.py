# Laborator: funcții, metode și importuri pe web
# Student: Bacalu Silviu-Laurentiu
"""Modulul reutilizabil pentru exercițiile 44–50."""

import json
import re
import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests

TIMEOUT = 10
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]

# EXERCIȚIUL 47 — Constantă de modul
DEFAULT_HEADERS = {"User-Agent": "WebLab-Bacalu-Silviu-Laurentiu"}


# EXERCIȚIUL 44 — Funcții mutate în modul
def fetch(url: str, timeout: float = TIMEOUT) -> requests.Response:
    """Descarcă un URL cu timeout și o pauză înaintea cererii."""
    time.sleep(1)
    # Regula laboratorului permite antete personalizate doar pe httpbin.org.
    # Ex. 47 cere folosirea constantei în fetch: o folosim pe acea țintă.
    if urlparse(url).hostname == "httpbin.org":
        return requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
    return requests.get(url, timeout=timeout)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP."""
    return fetch(url).status_code


def get_title(html: str) -> str | None:
    """Extrage titlul HTML sau returnează None dacă acesta lipsește."""
    lower_html = html.lower()
    start = lower_html.find("<title>")
    if start == -1:
        return None
    start += len("<title>")
    end = lower_html.find("</title>", start)
    if end == -1:
        return None
    return html[start:end].strip()


def security_headers(url: str) -> dict[str, bool]:
    """Verifică prezența celor cinci antete de securitate."""
    response = fetch(url)
    response.raise_for_status()
    return {name: name in response.headers for name in SECURITY_HEADERS}


def score_headers(results: dict[str, bool]) -> str:
    """Returnează numărul antetelor prezente raportat la total."""
    return f"{sum(results.values())}/{len(results)}"


def fetch_robots(base: str) -> str | None:
    """Returnează robots.txt; întoarce None pentru HTTP 404."""
    response = fetch(base.rstrip("/") + "/robots.txt")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text


def disallowed_paths(robots_text: str | None) -> list[str]:
    """Extrage valorile Disallow care nu sunt goale, ignorând comentariile."""
    paths = []
    if robots_text is None:
        return paths
    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip()
        name, separator, value = line.partition(":")
        if separator and name.strip().lower() == "disallow" and value.strip():
            paths.append(value.strip())
    return paths


def extract_links(html: str) -> list[str]:
    """Extrage legăturile href scrise între ghilimele duble, fără duplicate."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))


def split_links(links: list[str], base: str) -> tuple[list[str], list[str]]:
    """Transformă legăturile în URL-uri și separă domeniile interne/externe."""
    internal, external = [], []
    domain = urlparse(base).netloc.lower()
    for link in links:
        full_url = urljoin(base, link)
        parsed = urlparse(full_url)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc.lower() == domain:
            internal.append(full_url)
        else:
            external.append(full_url)
    return list(dict.fromkeys(internal)), list(dict.fromkeys(external))


def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 a domeniului."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str) -> int:
    """Returnează zilele întregi până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            certificate = secure_sock.getpeercert()
    expires_at = ssl.cert_time_to_seconds(certificate["notAfter"])
    return int((expires_at - datetime.now(timezone.utc).timestamp()) // 86400)


# EXERCIȚIUL 49 — Funcția utilizată pentru raportul CSV
def check_paths(base: str, paths: list[str]) -> dict[str, int | None]:
    """Returnează codurile de stare; None indică o eroare de conexiune."""
    results = {}
    for path in paths:
        try:
            results[path] = get_status(urljoin(base.rstrip("/") + "/", path))
        except requests.RequestException as error:
            results[path] = None
            print(f"Eroare la verificarea {path}: {error}")
    return results


# EXERCIȚIUL 50 — Raportul complet
def site_report(url: str) -> dict:
    """Colectează datele site-ului, le afișează și le salvează în report.json."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Introdu un URL complet, de exemplu https://cybercor.org.")
    base = f"{parsed.scheme}://{parsed.netloc}"
    errors = {}

    def collect(name, function, *args):
        """Execută o verificare și consemnează erorile fără a inventa rezultate."""
        try:
            return function(*args)
        except (requests.RequestException, OSError, KeyError, ValueError) as error:
            errors[name] = str(error)
            return None

    response = collect("page", fetch, url)
    header_results = collect("security_headers", security_headers, url)
    robots = collect("robots", fetch_robots, base)
    redirect_response = collect("redirects", fetch, f"http://{parsed.netloc}/")
    ip = collect("ip", resolve, parsed.hostname)
    days = collect("certificate", cert_days_left, parsed.hostname)

    internal, external = [], []
    if response is not None:
        internal, external = split_links(extract_links(response.text), response.url)

    redirects = None
    if redirect_response is not None:
        redirects = [
            {
                "status": item.status_code,
                "url": item.url,
                "next_url": urljoin(item.url, item.headers.get("Location", "")),
            }
            for item in redirect_response.history
        ]

    report = {
        "url": url,
        "checked_at": datetime.now().isoformat(),
        "status_code": response.status_code if response is not None else None,
        "final_url": response.url if response is not None else None,
        "title": get_title(response.text) if response is not None else None,
        "ip": ip,
        "redirects": redirects,
        "redirect_final_url": redirect_response.url if redirect_response is not None else None,
        "security_headers": header_results,
        "security_score": score_headers(header_results) if header_results is not None else None,
        "certificate_days_left": days,
        "internal_links_count": len(internal) if response is not None else None,
        "external_links_count": len(external) if response is not None else None,
        "robots_available": robots is not None if "robots" not in errors else None,
        "disallowed_paths": disallowed_paths(robots) if "robots" not in errors else None,
        "errors": errors,
    }

    print(f"\n=== Raport site: {url} ===")
    print("Cod de stare:", report["status_code"])
    print("URL final:", report["final_url"])
    print("Titlu:", report["title"])
    print("Adresă IP:", ip)
    print("Redirecționări de la HTTP:")
    if redirects is None:
        print("  Verificarea a eșuat.")
    elif redirects:
        for item in redirects:
            print(f"  {item['status']} | {item['url']} -> {item['next_url']}")
    else:
        print("  Nicio redirecționare.")
    print("URL final după HTTP:", report["redirect_final_url"])
    print("Scor antete de securitate:", report["security_score"])
    print("Zile până la expirarea certificatului:", days)
    print("Legături interne:", report["internal_links_count"])
    print("Legături externe:", report["external_links_count"])
    print("robots.txt disponibil:", report["robots_available"])
    print("Căi interzise:", report["disallowed_paths"])
    for name, error in errors.items():
        print(f"Verificare nereușită ({name}): {error}")

    with open("report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print("Salvat în report.json")
    return report


# EXERCIȚIUL 46 — Rulează doar când executăm direct webtools.py.
# La import, __name__ este 'webtools'; la rulare directă, este '__main__'.
if __name__ == "__main__":
    try:
        print("Autotest:", get_status("https://cybercor.org"))
    except requests.RequestException as error:
        print("Autotest — Cererea a eșuat:", error)
