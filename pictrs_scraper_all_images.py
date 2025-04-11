import json
import time
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Die URL der Hauptseite
main_url = "https://www.pictrs.com/moritz-hilpert?l=de"

# Selenium Optionen
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Galerie-Slug extrahieren
def get_gallery_slug(url):
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}_{parts[-1]}"
    return "gallery"

# Alle Bilder
all_bilder = []

# Starte den WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print(f"Verarbeite Hauptseite: {main_url}")
    driver.get(main_url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "albums-grid-item")))

    # Scroll bis zum Ende
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Galerie-Links sammeln
    gallery_links = []
    for a in soup.find_all("a", class_="albums-grid-item no-focus-outline"):
        href = a.get("href")
        if href:
            full_url = urljoin(main_url, href)
            gallery_links.append(full_url)

    print(f"Gefundene {len(gallery_links)} Galerien")

    # Alle Galerien durchgehen
    for url in gallery_links:
        print(f"Verarbeite Galerie: {url}")
        slug = get_gallery_slug(url)
        driver.get(url)

        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))

            # Scroll bis zum Ende
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")
            image_items = soup.find_all("span", class_="imageitem")

            bilder = []
            for item in image_items:
                data_id = item.get("data-id")
                a_tag = item.find("a", class_="thumba")
                if not data_id or not a_tag or not a_tag.get("href"):
                    continue

                img_page_url = urljoin(main_url, a_tag["href"])
                driver.get(img_page_url)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "image-preview-img")))
                    img_tag = driver.find_element(By.ID, "image-preview-img")
                    image_url = img_tag.get_attribute("src")  # Hier wird `image_src` zu `image_url` geändert
                    eintrag = {
                        "link": img_page_url,
                        "image_url": image_url  # 'image_src' wird zu 'image_url' geändert
                    }
                    bilder.append(eintrag)
                except Exception as e:
                    print(f"❌ Fehler beim Laden von Bild {data_id}: {e}")

            print(f"✔️  {len(bilder)} Bilder in Galerie '{slug}' gefunden")
            all_bilder.extend(bilder)

        except Exception as e:
            print(f"⚠️ Fehler beim Verarbeiten der Galerie {url}: {e}")

finally:
    driver.quit()

# Speichern als JSON
filename = "all_images.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(all_bilder, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Insgesamt {len(all_bilder)} Bilder gespeichert in '{filename}'")
