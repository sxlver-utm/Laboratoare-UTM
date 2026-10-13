# Laborator: funcții, metode și importuri pe web
# Student: Bacalu Silviu-Laurentiu

import urllib.parse
import re
import requests
from html.parser import HTMLParser
import hashlib
import time
import json
import socket
import ssl
import time
from datetime import datetime, timezone





BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10

# exercitiul 35


def show_url_parts(url: str) -> None:
    """Descompune URL-ul și afișează componentele sale."""
    parsed = urllib.parse.urlparse(url)

    print("Scheme:", parsed.scheme)
    print("Netloc:", parsed.netloc)
    print("Path:", parsed.path)
    print("Query:", parsed.query)
    print("Fragment:", parsed.fragment)


show_url_parts("https://cybercor.org/path?x=1#top")


# exercitiul 36

def show_full_urls(base: str) -> None:
    """Transforma cele trei legaturi relative in URL-uri complete"""
    links = ["/about", "/contact.html", "../index.html"]
    for link in links:
        full_url = urllib.parse.urljoin(base, link)
        print(f"{link} -> {full_url}")

print("\nURL-uri complete:")
show_full_urls(BASE_URL)


# exercitiul 37

def extract_links(html: str) -> list[str]:
    """Extrage legaturile din HTML si elimina duplicatele."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))

response = requests.get(BASE_URL, timeout=TIMEOUT)
html = response.text
links = extract_links(html)

print("\nLegaturi fara duplicate")
print("Numar de legaturi:", len(links))

for link in links:
    print(link)


# exercitiul 38

def split_links(links: list[str], domain: str) -> tuple[list[str], list[str]]:
    """Separa legaturile web in interne si externe"""
    internal = []
    external = []
    base = f"https://{domain}/"

    for link in links:
        full_url = urllib.parse.urljoin(base, link)
        parsed = urllib.parse.urlparse(full_url)


        if parsed.scheme not in ("http", "https"):
            continue

        if parsed.netloc.lower() == domain.lower():
            internal.append(full_url)
        else:
            external.append(full_url)


        return internal, external

domain = urllib.parse.urlparse(BASE_URL).netloc
internal_links, external_links = split_links(links, domain)


print("\nLegaturi interne:", len(internal_links))
for link in internal_links:
    print(link)

print("\nLegaturi interne:", len(external_links))
for link in external_links:
    print(link)

# exercitiul 39


class ImageFinder(HTMLParser):
    """Colectează adresele imaginilor din tag-urile img."""

    def __init__(self):
        """Inițializează parserul și lista imaginilor."""
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Adaugă atributul src al fiecărui tag img."""
        if tag == "img":
            src = dict(attrs).get("src")

            if src is not None:
                self.images.append(src)


test_html = """
<html><body>
    <img src="/logo.png" alt="Logo">
    <IMG SRC="poza.jpg">
    <img alt="imagine fără src">
    <img src="https://cdn.example.com/banner.webp" />
    <a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""

finder = ImageFinder()
finder.feed(test_html)

print("\nImagini din test:", finder.images)

assert finder.images == [
    "/logo.png",
    "poza.jpg",
    "https://cdn.example.com/banner.webp"
], "Parserul nu a găsit exact imaginile așteptate"

print("Testul a trecut!")


finder = ImageFinder()
finder.feed(response.text)

print("\nImagini găsite pe site:", len(finder.images))

for src in finder.images:
    print(src)

print("Apariții ale '<img' în HTML:", response.text.lower().count("<img"))



# exercitiul 40

def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 a corpului răspunsului."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()


time.sleep(1)
first_hash = page_fingerprint(BASE_URL)

time.sleep(1)
second_hash = page_fingerprint(BASE_URL)

print("\nExercițiul 40 — Prima amprentă:", first_hash)
print("A doua amprentă:", second_hash)
print("Amprente identice:", first_hash == second_hash)





# exercitiul 41

def save_and_read_headers(url: str) -> None:
    """Salvează antetele în headers.json, apoi citește fișierul."""
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()

    with open("headers.json", "w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2, ensure_ascii=False)

    with open("headers.json", "r", encoding="utf-8") as file:
        saved_headers = json.load(file)

    normalized = {name.lower(): value for name, value in saved_headers.items()}
    print("\nExercițiul 41 — Content-Type:", normalized.get("content-type", "lipsește"))
    print("Antetele au fost salvate în headers.json.")


time.sleep(1)
try:
    save_and_read_headers(BASE_URL)
except requests.RequestException as error:
    print("Exercițiul 41 — Cererea a eșuat:", error)


# exercitiul 42 

def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 a domeniului."""
    return socket.gethostbyname(hostname)


time.sleep(1)
try:
    print("\nExercițiul 42 — Adresa IP:", resolve("cybercor.org"))
except OSError as error:
    print("Exercițiul 42 — Interogarea DNS a eșuat:", error)


# exercitiul 43

def cert_days_left(hostname: str) -> int:
    """Returnează zilele întregi rămase până la expirarea certificatului TLS."""
    context = ssl.create_default_context()

    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            certificate = secure_sock.getpeercert()

    expires_at = ssl.cert_time_to_seconds(certificate["notAfter"])
    now = datetime.now(timezone.utc).timestamp()
    return int((expires_at - now) // 86400)


time.sleep(1)
try:
    print("\nExercițiul 43 — Zile până la expirare:", cert_days_left("cybercor.org"))
except (OSError, KeyError, ValueError) as error:
    print("Exercițiul 43 — Certificatul nu a putut fi verificat:", error)
