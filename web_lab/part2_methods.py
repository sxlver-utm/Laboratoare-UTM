# Laborator: funcții, metode și importuri pe web
# Student: Bacalu Silviu-Laurentiu

import requests
import time

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10


# exercitiu 9

response = requests.get(BASE_URL, timeout=TIMEOUT)

print("Cod de stare:", response.status_code)  # Atribut
print("Cerere reușită:", response.ok)         # Atribut
print("URL final:", response.url)            # Atribut
print("Codificare:", response.encoding)      # Atribut

# exercitiu 10
try: 
    response.raise_for_status()  # Metodă care ridică o excepție dacă cererea nu a avut succes
    print("Pagina principala nu are erori HTTP.")
except requests.exceptions.HTTPError as error:
    print("Pagina principala are erori HTTP:", error)

time.sleep(1)  # pauză de 1 secundă

# accesam adresa indicata in exercitiu.
try:
    missing_response = requests.get(ECHO_URL + "/missing", timeout=TIMEOUT)

    missing_response.raise_for_status()  # Metodă care ridică o excepție dacă cererea nu a avut succes
    print("Serverul nu a returnat o eroare HTTP pentru aceasta adresă.")

except requests.exceptions.HTTPError as error:
    print("Serverul a returnat o eroare HTTP pentru aceasta adresă:", error)
    print("Cod de stare:", missing_response.status_code)  # Atribut

except requests.RequestException as error:
    print("Nu s-a putut accesa adresa:", error)

# exercitiu 11
print("\nAntetele paginii principale:")

for name, value in response.headers.items():
    print(f"{name}: {value}")


# exercitiu 12
print("Antete selectate:")
print("Server:", response.headers.get("Server", "Lipsa"))
print("Content-Type:", response.headers.get("Content-Type", "Lipsa"))
print("content-type:", response.headers.get("content-type", "Lipsa"))



# exercitiu 13
count = response.text.lower().count("cyber")
print("Numărul de apariții ale cuvântului 'cyber' în conținutul paginii principale: ", count)


# exercitiu 14

html = response.text
start = html.find("<title>")
if start != -1:
    start += len("<title>")
    end = html.find("</title>", start)
    if end != -1:
        title = html[start:end]
        print("Titlul paginii principale:", title)
    else:
        print("Tagul </title> nu a fost găsit.")
else:
    print("\nTagul <title> nu a fost găsit în conținutul paginii principale.")

# exercitiu 15
lines = response.text.splitlines()

print("\nNumarul de linii HTML:", len(lines))

if lines:
    longest_line = max(lines, key=len)
    print("Cea mai lungă linie HTML are", len(longest_line), "caractere.")
else:
    print("Lungimea celei mai lungi linii: 0")

# exercitiu 16

if response.url.startswith("https://"):
    print("\nConexiunea este securizată cu HTTPS.")
else: 
    print("\nConexiunea nu este securizată cu HTTPS.")

# exercitiu 17
time.sleep(1)  # pauză de 1 secundă

redirect_response = requests.get("https://cybercor.org/redirect", timeout=TIMEOUT)

print("\nNumărul de redirecționări:")

for redirect in redirect_response.history:
    print(f"{redirect.status_code} -> {redirect.url}")
if not redirect_response.history:
    print("Nu au existat redirecționări.")
print("URL final după redirecționări:", redirect_response.url)


# exercitiu 18
time.sleep(1)  # pauză de 1 secundă

head_response = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)  # pauză de 1 secundă 


get_response = requests.get(BASE_URL, timeout=TIMEOUT)

print("\nDimensiunea corpului HEAD", len(head_response.content), "octeți.")
print("Dimensiunea corpului GET", len(get_response.content), "octeți.")

# exercitiul 19

print("\nCookiurile paginii principale:")
if response.cookies:
    for cookie in response.cookies:
        print("Nume:", cookie.name, "|Secure:", cookie.secure)
else: 
    print("Nu există cookie-uri pentru această pagină.")


# exercitiu 20

time.sleep(1)  # pauză de 1 secundă

with requests.Session() as session:
    user_agent = "Weblab - Silviu Laurentiu Bacalu"
    session.headers.update({"User-Agent": user_agent})

    echo_response = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)  
    echo_response.raise_for_status()
recieved_headers = echo_response.json().get("headers", {})
recieved_agent = recieved_headers.get("User-Agent", "Lipsa")
print("\nUser-Agent primit de server:", recieved_agent)

if recieved_agent == user_agent:
    print("User-Agent-ul a fost setat corect în sesiune.")
else:
    print("User-Agent-ul nu a fost setat corect în sesiune.")

