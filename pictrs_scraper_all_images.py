import json
import time
from urllib.parse import urljoin
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
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

all_bilder = []

try:
    driver.get(main_url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "albums-grid-item")))

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        if driver.execute_script("return document.body.scrollHeight") == last_height:
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    gallery_links = [urljoin(main_url, a["href"]) for a in soup.select("a.albums-grid-item.no-focus-outline")]

    for url in gallery_links:
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))
            while True:
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                if driver.execute_script("return document.body.scrollHeight") == last_height:
                    break

            soup = BeautifulSoup(driver.page_source, "html.parser")
            for item in soup.select("span.imageitem"):
                a_tag = item.select_one("a.thumba")
                if not a_tag or not a_tag.get("href"):
                    continue

                img_page_url = urljoin(main_url, a_tag["href"])
                driver.get(img_page_url)
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "image-preview-img")))
                    img = driver.find_element(By.ID, "image-preview-img")
                    all_bilder.append({
                        "link": img_page_url,
                        "image_url": img.get_attribute("src")
                    })
                except:
                    pass
        except:
            pass
finally:
    driver.quit()

with open("all_images.json", "w", encoding="utf-8") as f:
    json.dump(all_bilder, f, indent=2, ensure_ascii=False)
