import requests
from bs4 import BeautifulSoup
import json

SHOP_URL = 'https://www.pictrs.com/moritz-hilpert?l=de'
BASE_URL = 'https://www.pictrs.com'

def fetch_galerien():
    response = requests.get(SHOP_URL)
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    galerien = []

    gallery_links = soup.find_all('a', class_='albums-grid-item')
    print(f"{len(gallery_links)} Galerien gefunden")

    for gallery_link in gallery_links:
        relative_url = gallery_link.get('href')  # z.B. /moritz-hilpert/8816720/ravello?l=de
        full_url = BASE_URL + relative_url

        galerie_titel = gallery_link.find('span', class_='albums-grid-title').get_text().strip()
        galerie_bilder_count = gallery_link.find('small', class_='albums-grid-details').get_text().strip()

        # Vorschaubild korrekt aus Style-Attribut extrahieren
        bild_div = gallery_link.find('div', class_='albums-grid-image')
        bild_style = bild_div.get('style') if bild_div else ''
        bild_url = ''

        if 'url(' in bild_style:
            bild_url = bild_style.split('url(')[-1].split(')')[0].strip('"\'')

        galerie = {
            'titel': galerie_titel,
            'link': full_url,
            'bilder_count': galerie_bilder_count,
            'vorschaubild': bild_url
        }

        galerien.append(galerie)

    return galerien

def save_to_json(galerien):
    with open('galerien.json', 'w', encoding='utf-8') as f:
        json.dump(galerien, f, ensure_ascii=False, indent=4)
    print("✔️  JSON-Datei erfolgreich gespeichert!")

if __name__ == "__main__":
    galerien = fetch_galerien()
    if galerien:
        save_to_json(galerien)
