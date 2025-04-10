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

# URLs der Galleries
urls = [
    "https://www.pictrs.com/moritz-hilpert/8520217?l=de",
    "https://www.pictrs.com/moritz-hilpert/6296877?l=de",
    # weitere URLs hier ergänzen
]

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

# Starte den Hauptprozess
for url in urls:
    print(f"Verarbeite: {url}")
    slug = get_gallery_slug(url)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))

    # Scrollen zum vollständigen Laden
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

    soup = BeautifulSoup(html, "html.parser")
    image_items = soup.find_all("span", class_="imageitem")

    bilder = []
    # Neuen Driver zum Öffnen der Bilder
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

    driver.quit()

    # Speichern
    filename = f"{slug}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bilder, f, indent=2, ensure_ascii=False)
    print(f"{len(bilder)} Bilder gespeichert in {filename}")
