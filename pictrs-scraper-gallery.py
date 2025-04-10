import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# Warte, bis die Seite vollständig geladen ist
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))

# Optional: Scrollen, um sicherzustellen, dass alle Bilder geladen sind
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_count = 0
max_scrolls = 5  # Maximale Anzahl an Scroll-Versuchen

while scroll_count < max_scrolls:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Gib der Seite Zeit zum Nachladen
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    scroll_count += 1

# HTML der Seite extrahieren
html = driver.page_source
driver.quit()

# HTML parsen
soup = BeautifulSoup(html, "html.parser")

# Alle Bilder auf der Seite extrahieren
image_items = soup.find_all("span", class_="imageitem")

bilder = []

for item in image_items:
    # Extrahiere relevante Daten
    data_id = item.get("data-id")
    a_tag = item.find("a", class_="thumba")
    img_tag = item.find("img", class_="picthumbs")

    # Wenn keine der benötigten Daten gefunden wird, überspringen
    if not all([data_id, a_tag, img_tag]):
        continue

    # Hole den Bild-Link (src)
    image_src = img_tag.get("src", "")
    if not image_src:
        image_src = "N/A"  # Setze einen Platzhalter, falls kein Bild vorhanden ist

    eintrag = {
        "id": data_id,
        "link": a_tag["href"],
        "image_src": image_src,
        "alt": img_tag.get("alt", "")
    }

    bilder.append(eintrag)

# Falls Bilder fehlen, versuche zusätzliche `img`-Tags zu extrahieren
extra_images = soup.find_all("img")
for img_tag in extra_images:
    # Manchmal sind zusätzliche Bilder auf der Seite
    img_src = img_tag.get("src", "")
    if img_src and img_src != "N/A":
        bilder.append({
            "id": "unknown",  # Wir haben keine `data-id` für diese Bilder
            "link": img_tag.get("src", ""),
            "image_src": img_src,
            "alt": img_tag.get("alt", "Unknown Alt Text")
        })

# Speichern in eine JSON-Datei
with open("bilder.json", "w", encoding="utf-8") as f:
    json.dump(bilder, f, indent=2, ensure_ascii=False)

print(f"{len(bilder)} Bilder gespeichert in bilder.json")
