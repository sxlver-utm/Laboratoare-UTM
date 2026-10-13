# Laborator: funcții, metode și importuri pe web
# Student: Bacalu Silviu-Laurentiu

import requests
import time

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10



# exercitiu 21  

def fetch(url: str, timeout: float = 10) -> requests.Response:
    """Descarcă pagina și returnează obiectul răspuns."""
    response = requests.get(url, timeout=timeout)
    return response


response = fetch(BASE_URL)
print("Cod de stare:", response.status_code)


# exercitiu 22

def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa indicată."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.status_code


print("\n Verificarea celor trei căi:")

paths = ["/", "/robots.txt", "/sitemap.xml"]

for path in paths:
    time.sleep(1)
    status = get_status(BASE_URL + path)
    print("Cale:", path, "| Cod de stare:", status)


# exercițiu 23

time.sleep(1)

default_response = fetch(BASE_URL)
print("\n Timeout implicit de 10 secunde:")
print("Cod de stare:", default_response.status_code)

time.sleep(1)

custom_response = fetch(BASE_URL, timeout=3)
print("Timeout personalizat de 3 secunde:")
print("Cod de stare:", custom_response.status_code)


# exercițiu 24

def get_title(html: str) -> str | None:
    """Returnează titlul din HTML sau None dacă acesta lipsește."""
    start = html.find("<title>")

    if start == -1:
        return None

    start += len("<title>")
    end = html.find("</title>", start)

    if end == -1:
        return None

    return html[start:end].strip()


title = get_title(default_response.text)
print("\nTitlul paginii:", title)


# exercițiu 25

help(get_title)


# exercițiu 26

print("\nTest cu un argument de tip greșit:")

try:
    print(get_status(123))
except requests.RequestException as error:
    print("Eroare pentru get_status(123):", error)

# exercițiu 27

def page_exists(url: str) -> bool:
    """Returnează True dacă pagina există , altfel False."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


time.sleep(1)
print("\nVerificarea existenței paginilor:", page_exists(BASE_URL))

time.sleep(1)
print("Domeniu inexistent:", page_exists("https://nonexistentdomain.example"))


# exercițiu 28

def check_paths(base: str, paths: list[str]) -> dict[str, int]:
    """Returnează un dicționar cu căile și codurile de stare corespunzătoare."""
    results = {}
    for path in paths:
        time.sleep(1)
        full_url = base + path
        results[path] = get_status(full_url)
    return results

results = check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"])
print ("\nRezultatele verificării căilor:", results)

# exercițiu 29

def get_header(url: str, name: str, default: str = "Lipseste") -> str: 
    """Returnează valoarea antetului specificat sau None dacă acesta lipsește."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.headers.get(name, default)

time.sleep(1)

server = get_header(BASE_URL, name="Server")
print("\nAntetul Server:", server)


# exercițiu 30

def security_headers(url: str) -> dict[str, bool]:
    """Returnează un dicționar cu anteturile de securitate."""
    response = requests.get(url, timeout=TIMEOUT)
    headers_to_check = {
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy"
    }
    results = {}

    for header in headers_to_check:

        results[header] = header in response.headers

    return results

time.sleep(1)

security_results = security_headers(BASE_URL)
print("\nAnteturile de securitate:")

for header, present in security_results.items(): 

    print(f"{header}: {'Prezent' if present else 'Lipsa'}")

# exercițiu 31

def score_header(results: dict[str, bool]) -> str:
    """Returneaza scorul antetelor prezente in formatul numar/total."""
    present = sum(results.values())
    total = len(results)
    return f"{present}/{total}"


time.sleep(1)


score = score_header(security_headers(BASE_URL))
print("\nScorul antetelor de securitate:", score)

# exercițiu 32

def fetch_robots(base: str) -> str | None:
    """Returnează textul robots.txt sau None dacă nu poate fi obținut."""
    try:
        response = requests.get(
            base.rstrip("/") + "/robots.txt",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def disallowed_paths(robots_text: str | None) -> list[str]:
    """Returnează căile Disallow sau o listă goală dacă textul lipsește."""
    paths = []

    if robots_text is None:
        return paths

    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip()
        name, separator, value = line.partition(":")

        if separator and name.strip().lower() == "disallow":
            path = value.strip()

            if path:
                paths.append(path)

    return paths


time.sleep(1)

robots_text = fetch_robots(BASE_URL)
print("\nCăi interzise:", disallowed_paths(robots_text))
print("Test cu None:", disallowed_paths(None))


# exercitiu 33
def response_times(*urls: str) -> dict[str, float]:
    """Returneaza durata in secunde"""
    results = {}

    for url in urls:
        time.sleep(1)

        start = time.perf_counter()
        requests.get(url, timeout=TIMEOUT)
        end = time.perf_counter()

        results[url] = end - start
    return results

times = response_times(BASE_URL, BASE_URL + "/robots.txt")

print("\nDuratele cererilor")

for ulr, seconds in times.items():
    print(f"{ulr}: {seconds: .3f} secunde")


# exercitiu 34  

def log(message: str, **details) -> None:
    """Afiseaza mesajul urmat de detaliile primite."""
    parts = [message]

    for name, value in details.items():
        parts.append(f"{name} = {value}")

    print(" | " .join(parts))


log("verificat", url=BASE_URL, status=response.status_code)

