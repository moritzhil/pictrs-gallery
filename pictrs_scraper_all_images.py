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

main_url = "https://www.pictrs.com/moritz-hilpert?l=de"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def get_gallery_slug(url):
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}_{parts[-1]}"
    return "gallery"

all_bilder = []

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print(f"Verarbeite Hauptseite: {main_url}")
    driver.get(main_url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "albums-grid-item")))

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    gallery_links = []
    for a in soup.find_all("a", class_="albums-grid-item no-focus-outline"):
        href = a.get("href")
        if href:
            full_url = urljoin(main_url, href)
            gallery_links.append(full_url)

    print(f"Gefundene {len(gallery_links)} Galerien")

    for url in gallery_links:
        print(f"Verarbeite Galerie: {url}")
        slug = get_gallery_slug(url)
        driver.get(url)

        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))

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

            for item in image_items:
                a_tag = item.find("a", class_="thumba")
                if not a_tag or not a_tag.get("href"):
                    continue

                img_page_url = urljoin(main_url, a_tag["href"])
                driver.get(img_page_url)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "image-preview-img")))
                    img_tag = driver.find_element(By.ID, "image-preview-img")
                    all_bilder.append({
                        "link": img_page_url,
                        "image_url": img_tag.get_attribute("src")
                    })
                except:
                    pass

        except:
            pass

finally:
    driver.quit()

with open("all_images.json", "w", encoding="utf-8") as f:
    json.dump(all_bilder, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Insgesamt {len(all_bilder)} Bilder gespeichert in 'all_images.json'")
