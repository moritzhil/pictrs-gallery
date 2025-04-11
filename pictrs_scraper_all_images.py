import json, time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.pictrs.com/moritz-hilpert?l=de"

def scroll(driver):
    while True:
        height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        if height == driver.execute_script("return document.body.scrollHeight"):
            break

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options().add_argument("--headless"))
    all_images = []

    try:
        driver.get(URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "albums-grid-item")))
        scroll(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        gallery_urls = [urljoin(URL, a["href"]) for a in soup.select("a.albums-grid-item.no-focus-outline")]

        for gal_url in gallery_urls:
            driver.get(gal_url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "imageitem")))
            scroll(driver)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            for item in soup.select("span.imageitem"):
                a_tag = item.select_one("a.thumba")
                if not a_tag or not a_tag.get("href"):
                    continue
                link = urljoin(URL, a_tag["href"])
                driver.get(link)
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "image-preview-img")))
                    img = driver.find_element(By.ID, "image-preview-img")
                    all_images.append({
                        "link": link,
                        "image_url": img.get_attribute("src")
                    })
                except: pass

    finally:
        driver.quit()

    with open("image_links.json", "w", encoding="utf-8") as f:
        json.dump(all_images, f, indent=2, ensure_ascii=False)

    print(f"✔️  {len(all_images)} Bild-Links gespeichert in image_links.json")

if __name__ == "__main__":
    main()
