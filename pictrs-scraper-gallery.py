import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Setze Optionen für den Headless-Modus
options = Options()
options.add_argument('--headless')  # Headless-Modus aktivieren

# Initialisiere den WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Lade die Pictrs-Seite
url = "https://www.pictrs.com/moritz-hilpert/9528141/see?l=de"
driver.get(url)

# Warte, bis die Seite vollständig geladen ist (ggf. anpassen)
time.sleep(5)

# HTML der Seite extrahieren
html = driver.page_source
driver.quit()

# HTML parsen
soup = BeautifulSoup(html, "html.parser")

# Finde alle Bild-Container
image_items = soup.select("span.imageitem")

bilder = []

for item in image_items:
    data_id = item.get("data-id")
    a_tag = item.find("a", class_="thumba")
    img_tag = item.find("img", class_="picthumbs")

    if not all([data_id, a_tag, img_tag]):
        continue

    eintrag = {
        "id": data_id,
        "link": a_tag["href"],
        "image_src": img_tag["src"],
        "alt": img_tag.get("alt", "")
    }

    bilder.append(eintrag)

# Speichern in eine JSON-Datei
with open("bilder.json", "w", encoding="utf-8") as f:
    json.dump(bilder, f, indent=2, ensure_ascii=False)

print(f"{len(bilder)} Bilder gespeichert in bilder.json")
