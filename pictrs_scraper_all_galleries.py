import requests
from bs4 import BeautifulSoup
import json
import os
import re

SHOP_URL = 'https://www.pictrs.com/moritz-hilpert?l=de'
BASE_URL = 'https://www.pictrs.com'

def fetch_galerien():
    response = requests.get(SHOP_URL)
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    galerien = []

    # Alle Galerie-Links finden
    gallery_links = soup.find_all('a', class_='albums-grid-item')
    print(f"{len(gallery_links)} Galerien gefunden")

    # Durch alle gefundenen Galerie-Links iterieren
    for gallery_link in gallery_links:
        relative_url = gallery_link.get('href')  # z.B. /moritz-hilpert/8816720/ravello?l=de
        
        # Überprüfen, ob die URL bereits mit der BASE_URL beginnt
        if not relative_url.startswith('https://'):
            full_url = BASE_URL + relative_url  # Komplettiere die URL nur, wenn sie relativ ist
        else:
            full_url = relative_url  # Wenn sie bereits absolut ist, verwende sie direkt

        galerie_titel = gallery_link.find('span', class_='albums-grid-title').get_text().strip()
        galerie_bilder_count = gallery_link.find('small', class_='albums-grid-details').get_text().strip()

        # Vorschaubild korrekt aus dem style-Attribut extrahieren
        bild_div = gallery_link.find('div', class_='albums-grid-image')
        bild_style = bild_div.get('style') if bild_div else ''
        bild_url = ''

        if 'url(' in bild_style:
            # Extrahieren der Bild-URL aus dem style-Attribut
            bild_url = bild_style.split('url(')[-1].split(')')[0].strip('"\'')

            # Prüfen, ob die Bild-URL relativ ist
            if bild_url.startswith('/'):
                bild_url = BASE_URL + bild_url  # Wenn relativ, BASE_URL hinzufügen
            
            # Ersetze "_medium" mit "_large" für das Vorschaubild
            bild_url = bild_url.replace('/medium_', '/large_')

        galerie = {
            'titel': galerie_titel,
            'link': full_url,
            'bilder_count': galerie_bilder_count,
            'vorschaubild': bild_url
        }

        galerien.append(galerie)

        # Speichern jeder Galerie in einer eigenen JSON-Datei
        safe_title = re.sub(r'[^\w\s-]', '', galerie_titel).strip().replace(' ', '_')  # Ersetzt ungültige Zeichen
        filename = f"{safe_title}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(galerie, f, ensure_ascii=False, indent=4)
        print(f"✔️ Galerie '{galerie_titel}' als JSON gespeichert!")

    return galerien

if __name__ == "__main__":
    galerien = fetch_galerien()
