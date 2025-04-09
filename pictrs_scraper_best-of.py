import requests
from bs4 import BeautifulSoup
import json

# Hier die URL einer spezifischen Galerie einfügen (z.B. für die Galerie "Ravello")
GALERIE_URL = 'https://www.pictrs.com/moritz-hilpert/8816720/ravello?l=de'
BASE_URL = 'https://www.pictrs.com'

def fetch_bilder_aus_galerie(galerie_url):
    response = requests.get(galerie_url)
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    bilder = []

    # Alle <img> Tags mit der Klasse 'picthumbs js-picthumbs' extrahieren
    img_tags = soup.find_all('img', class_='')
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

    return bilder

def save_to_json(bilder):
    with open('bilder.json', 'w', encoding='utf-8') as f:
        json.dump(bilder, f, ensure_ascii=False, indent=4)
    print("✔️ JSON-Datei mit Bildern erfolgreich gespeichert!")

if __name__ == "__main__":
    bilder = fetch_bilder_aus_galerie(GALERIE_URL)
    if bilder:
        save_to_json(bilder)  # Bilder als JSON speichern
