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
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Gib der Seite Zeit zum Nachladen
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# HTML der Seite extrahieren
html = driver.page_source
driver.quit()

# HTML parsen
soup = BeautifulSoup(html, "html.parser")

# Finde alle Bild-Container
image_items = soup.find_all("span", class_="imageitem")

bilder = []

# Initialisiere den WebDriver nochmal für das Klicken auf die Bilder (für die Lightbox)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for item in image_items:
    # Extrahiere relevante Daten
    data_id = item.get("data-id")
    a_tag = item.find("a", class_="thumba")

    # Wenn keine der benötigten Daten gefunden wird, überspringen
    if not all([data_id, a_tag]):
        continue

    # Klicke auf das Bild-Link, um die Lightbox zu öffnen
    driver.get(a_tag["href"])

    # Warte auf das Bild in der Lightbox (bis das img-Tag mit der ID image-preview-img sichtbar ist)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "image-preview-img")))

    # Extrahiere den Link zur hochauflösenden Bilddatei
    img_tag = driver.find_element(By.ID, "image-preview-img")
    image_src = img_tag.get_attribute("src")

    eintrag = {
        "id": data_id,
        "link": a_tag["href"],
        "image_src": image_src,  # Der Link zur hochauflösenden Bilddatei
        "alt": img_tag.get_attribute("alt")
    }

    bilder.append(eintrag)

# Speichern in eine JSON-Datei
with open("bilder.json", "w", encoding="utf-8") as f:
    json.dump(bilder, f, indent=2, ensure_ascii=False)

print(f"{len(bilder)} Bilder gespeichert in bilder.json")
