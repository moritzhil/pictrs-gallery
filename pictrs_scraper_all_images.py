import json
import os
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Die URL der Hauptseite, die alle Galerie-Links enthält
main_url = "https://www.pictrs.com/moritz-hilpert?l=de"

# Selenium-Optionen
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Funktion zum Extrahieren des Slugs aus der URL für Dateinamen
def get_gallery_slug(url):
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}_{parts[-1]}"
    return "gallery"

# Liste zur Speicherung aller Bilder aus allen Galerien
all_bilder = []

# Starte den Hauptprozess
print(f"Verarbeite: {main_url}")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(main_url)

# Warten, bis die Galerie-Links geladen sind
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "albums-grid-item")))

# Scrollen zum vollständigen Laden der Seite
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

html = driver.page_source
driver.quit()

# BeautifulSoup für das Parsen des HTML-Codes
soup = BeautifulSoup(html, "html.parser")

# Finde alle Galerie-Links auf der Seite
gallery_links = []
album_items = soup.find_all("a", class_="albums-grid-item no-focus-outline")
for item in album_items:
    href = item.get("href")
    if href:
        gallery_links.append(href)

print(f"Gefundene {len(gallery_links)} Galerien")

# Neuen Driver zum Öffnen der Bilder
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Gehe alle gefundenen Galerie-Links durch
for url in gallery_links:
    print(f"Verarbeite Galerie: {url}")
    slug = get_gallery_slug(url)
    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))

    # Scrollen zum vollständigen Laden der Bilder
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    image_items = soup.find_all("span", class_="imageitem")

    bilder = []
    for item in image_items:
        data_id = item.get("data-id")
        a_tag = item.find("a", class_="thumba")
        if not all([data_id, a_tag]):
            continue
        driver.get(a_tag["href"])
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "image-preview-img")))
            img_tag = driver.find_element(By.ID, "image-preview-img")
            image_src = img_tag.get_attribute("src")
            eintrag = {
                "id": data_id,
                "link": a_tag["href"],
                "image_src": image_src,
                "alt": img_tag.get_attribute("alt")
            }
            bilder.append(eintrag)
        except Exception as e:
            print(f"Fehler bei Bild {data_id}: {e}")

    all_bilder.extend(bilder)

# Speichern der gesamten Bilddaten in einer JSON-Datei
filename = "all_pictrs_images.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(all_bilder, f, indent=2, ensure_ascii=False)

print(f"{len(all_bilder)} Bilder aus allen Galerien gespeichert in {filename}")
