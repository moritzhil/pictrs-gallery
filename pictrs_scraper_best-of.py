import requests
from bs4 import BeautifulSoup
import json

BASE_URL = 'https://www.pictrs.com'
GALERIE_URL = 'https://www.pictrs.com/moritz-hilpert/8816720/ravello?l=de'  # Beispiel-URL einer spezifischen Galerie

def fetch_bilder_from_galerie():
    response = requests.get(GALERIE_URL)
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    bilder = []

    # Alle Bild-Links der Galerie finden
    image_tags = soup.find_all('img', class_='picthumbs js-picthumbs')  # Passen Sie hier die richtige Klasse an
    print(f"{len(image_tags)} Bilder in der Galerie gefunden.")

    for img_tag in image_tags:
        bild_url = img_tag.get('src')
        if bild_url:
            print(f"Gefundenes Bild-URL: {bild_url}")  # Zum Debuggen: Bild-URL anzeigen
            # Ändern des Bild-URL von "medium" zu "large"
            if '/medium_' in bild_url:
                bild_url = bild_url.replace('/medium_', '/large_')
                print(f"Ändertes Bild-URL: {bild_url}")  # Zum Debuggen: Geänderte Bild-URL anzeigen
            bilder.append(bild_url)

    return bilder

def save_to_json(bilder):
    gallery_data = {
        'bilder': bilder
    }

    # Speichern der Galerie als JSON-Datei unter dem Namen 'gallerie_best-of.json'
    with open('gallerie_best-of.json', 'w', encoding='utf-8') as f:
        json.dump(gallery_data, f, ensure_ascii=False, indent=4)
    print("✔️  JSON-Datei 'gallerie_best-of.json' erfolgreich gespeichert!")

if __name__ == "__main__":
    bilder = fetch_bilder_from_galerie()
    if bilder:
        save_to_json(bilder)  # Wenn Bilder gefunden wurden, speichere sie als JSON
