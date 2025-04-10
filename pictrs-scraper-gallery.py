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
# options.add_argument('--headless')  # Deaktiviere den Headless-Modus, um den Browser sichtbar zu machen

# Initialisiere den WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Lade die Pictrs-Seite
url = "https://www.pictrs.com/moritz-hilpert/9528141/see?l=de"
driver.get(url)

# Warte, bis das erste Bild sichtbar ist
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "picthumbs")))

# Scrollen, um sicherzustellen, dass alle Bilder geladen sind
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Gib der Seite Zeit zum Nachladen
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# HTML der Seite extrahieren
html = driver.page_source
driver.quit()

# HTML parsen
soup = BeautifulSoup(html, "html.parser")

# Alle Bilder extrahieren
image_items = soup.select("img.picthumbs")  # Direkter Zugriff auf die Bild-Tags
bilder = []

for item in image_items:
    image_src = item.get("src")
    alt = item.get("alt", "")
    link = item.find_parent("a")["href"] if item.find_parent("a") else None

    if image_src and link:
        eintrag = {
            "image_src": image_src,
            "alt": alt,
            "link": link
        }
        bilder.append(eintrag)

# Speichern in eine JSON-Datei
with open("bilder.json", "w", encoding="utf-8") as f:
    json.dump(bilder, f, indent=2, ensure_ascii=False)

print(f"{len(bilder)} Bilder gespeichert in bilder.json")
