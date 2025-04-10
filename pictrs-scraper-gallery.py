import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# Warte auf das erste Bild (um sicherzustellen, dass der Inhalt vollständig geladen ist)
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "picthumbs")))

# Optional: Scrollen, um sicherzustellen, dass alle Bilder geladen sind
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_count = 0

# Wir scrollen bis 3-5 Mal, je nachdem, wie viele Bilder auf der Seite sind
while scroll_count < 5:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Pausiert, um sicherzustellen, dass das Lazy Loading durchgeführt wird
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

# Finde alle Bild-Container
image_items = soup.select("span.imageitem")

bilder = []

# Gehe durch alle gefundenen Bilder und extrahiere deren Links
for item in image_items:
    data_id = item.get("data-id")
    a_tag = item.find("a", class_="thumba")
    img_tag = item.find("img", class_="picthumbs")

    if not all([data_id, a_tag, img_tag]):
        continue

    # Klicke auf das Bild, um die große Version anzuzeigen
    image_link = a_tag["href"]
    driver.get(image_link)  # Öffnet den Link des Bildes in einem neuen Tab

    # Warte, bis das Bild geladen ist
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "image-preview-img")))

    # Extrahiere die große Bild-URL
    large_image_tag = driver.find_element(By.CLASS_NAME, "image-preview-img")
    large_image_url = large_image_tag.get_attribute("src")

    # Speichere die Bilddaten
    eintrag = {
        "id": data_id,
        "link": image_link,
        "large_image_src": large_image_url,
        "alt": img_tag.get("alt", "")
    }

    bilder.append(eintrag)

# Speichern in eine JSON-Datei
with open("bilder_mit_large_images.json", "w", encoding="utf-8") as f:
    json.dump(bilder, f, indent=2, ensure_ascii=False)

print(f"{len(bilder)} Bilder mit großen Links gespeichert in bilder_mit_large_images.json")
