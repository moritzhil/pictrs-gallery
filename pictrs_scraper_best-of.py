import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json

# Hier die URL einer spezifischen Galerie einfügen (z.B. für die Galerie "Ravello")
GALERIE_URL = 'https://www.pictrs.com/moritz-hilpert/8816720/ravello?l=de'
BASE_URL = 'https://www.pictrs.com'

# Initialisiere den WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: Im Hintergrund ausführen (ohne GUI)
chrome_service = Service(executable_path='path/to/chromedriver')  # Ersetze dies durch den Pfad zu deinem ChromeDriver

def fetch_bilder_aus_galerie(galerie_url):
    # Starte den WebDriver
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(galerie_url)
    
    # Warte darauf, dass die Seite vollständig geladen wird
    time.sleep(5)  # Warten auf die Ladezeit der Seite, ggf. erhöhen

    # Holen Sie sich den Seitenquelltext nach dem Laden
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    bilder = []

    # Alle <img> Tags mit der Klasse 'picthumbs js-picthumbs' extrahieren
    img_tags = soup.find_all('img', class_='picthumbs js-picthumbs')
    print(f"{len(img_tags)} Bilder gefunden")

    # Alle Bild-URLs extrahieren
    for img_tag in img_tags:
        bild_url = img_tag.get('src')
        
        # Wenn das Bild "medium_" enthält, ersetzen wir es mit "large_"
        if 'medium_' in bild_url:
            bild_url = bild_url.replace('medium_', 'large_')
        
        # Überprüfen, ob die Bild-URL relativ ist und BASE_URL hinzufügen, wenn nötig
        if bild_url.startswith('/'):
            bild_url = BASE_URL + bild_url

        bilder.append(bild_url)

    # Schließen des Webdrivers
    driver.quit()

    return bilder

def save_to_json(bilder):
    with open('bilder.json', 'w', encoding='utf-8') as f:
        json.dump(bilder, f, ensure_ascii=False, indent=4)
    print("✔️ JSON-Datei mit Bildern erfolgreich gespeichert!")

if __name__ == "__main__":
    bilder = fetch_bilder_aus_galerie(GALERIE_URL)
    if bilder:
        save_to_json(bilder)  # Bilder als JSON speichern
