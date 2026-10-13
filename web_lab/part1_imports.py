# Laborator: funcții, metode și importuri pe web
# Student: Bacalu Silviu-Laurentiu

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# exercitiu 1
import requests
import urllib.request

print("Versiunea requests:", requests.__version__)

# requests este o bibliotecă externă și se instalează cu pip.
# urllib face parte din biblioteca standard Python și nu necesită instalare.

# exercitiu 2
import time

response = requests.get(BASE_URL, timeout=TIMEOUT)
print ("Cu requests.get():", response.status_code) 
time.sleep(1)  # pauză de 1 secundă
# exercitiu 3
import requests as req
time.sleep(1)  # pauză de 1 secundă   


response = req.get(ECHO_URL, timeout=TIMEOUT)
print("Cu requests.get() (alias):", response.status_code)

# exercitiu 4
time.sleep(1)  # pauză de 1 secundă

time.sleep(1)

try:
    with urllib.request.urlopen(BASE_URL, timeout=TIMEOUT) as page:
        print("Status urllib:", page.status)
        html = page.read().decode("utf-8", errors="replace")
        print(html[:200])

except urllib.error.HTTPError as error:
    print("Status urllib:", error.code)
    print("Serverul a refuzat cererea.")
    html = error.read().decode("utf-8", errors="replace")
    print(html[:200])

except urllib.error.URLError as error:
    print("Eroare de conexiune:", error.reason)

# exercitiu 5
time.sleep(1)  # pauză de 1 secundă
print(dir(requests))  # afișează toate atributele și metodele disponibile în requests

# exercitiu 6
help(requests.get)

time.sleep(1)  # pauză de 1 secundă

response = requests.get(ECHO_URL, timeout=TIMEOUT)
print("Status cu timeout:", response.status_code)

# Parametrul timeout limiteaza timpul de asteptare pentru cerere.

# exercitiu 7
time.sleep(1)  # pauză de 1 secundă

start = time.perf_counter()
response = requests.get(ECHO_URL, timeout=TIMEOUT)
end = time.perf_counter()

print("Durata totala:", end - start, "secunde")
print("response.elapsed:", response.elapsed.total_seconds(), "secunde")

# exercitiu 8

try:
    import bs4
    print("BeautifulSoup4 este instalat.")
except ImportError: 
    print("instalati modulul cu: pip install beautifulsoup4")
