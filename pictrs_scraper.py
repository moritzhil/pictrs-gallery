import requests
from bs4 import BeautifulSoup
import json

SHOP_URL = 'https://www.pictrs.com/moritz-hilpert?l=de'

def fetch_galerien():
    response = requests.get(SHOP_URL)

    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    galerien = []
    gallery_links = soup.find_all('a', class_='albums-grid-item')  # Richtige Klasse!

    print(f"{len(gallery_links)} Galerien gefunden.")

    for gallery_link in gallery_links:
        try:
            url_parts = gallery_link.get('href').split('/')
            galerie_id = url_parts[-2]
            galerie_slug = url_parts[-1]
            galerie_titel = gallery_link.find('span', class_='albums-grid-title').get_text(strip=True)
            galerie_bilder_count = gallery_link.find('small', class_='albums-grid-details').get_text(strip=True)

            bild_style = gallery_link.find('div', class_='albums-grid-image').get('style')
            bild_url = bild_style.split("url(")[-1].split(")")[0]
            bild_link = f"https://www.pictrs.com{bild_url}"

            galerie = {
                'id': galerie_id,
                'slug': galerie_slug,
                'titel': galerie_titel,
                'bilder_count': galerie_bilder_count,
                'bilder': [{
                    'bild': bild_link,
                    'link': f'https://www.pictrs.com/moritz-hilpert/{galerie_id}/{galerie_slug}'
                }]
            }

            galerien.append(galerie)

        except Exception as e:
            print(f"Fehler beim Verarbeiten einer Galerie: {e}")
            continue

    return galerien

def save_to_json(galerien):
    with open('galerien.json', 'w', encoding='utf-8') as f:
        json.dump(galerien, f, ensure_ascii=False, indent=4)
    print("Daten erfolgreich in 'galerien.json' gespeichert!")

if __name__ == "__main__":
    galerien = fetch_galerien()
    if galerien:
        save_to_json(galerien)
    else:
        print("Keine Galerien gefunden.")
