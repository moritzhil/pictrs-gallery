import requests
from bs4 import BeautifulSoup
import json

# Deine Pictrs-Shop-URL
SHOP_URL = 'https://www.pictrs.com/moritz-hilpert?l=de'

# Funktion zum Abrufen und Parsen der Galerien und Bilder von Pictrs
def fetch_galerien():
    response = requests.get(SHOP_URL)
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Galerien-Daten sammeln
    galerien = []

    # Alle Galerien finden (Hier ist davon auszugehen, dass die Galerien Links sind)
    gallery_links = soup.find_all('a', class_='gallery-link-class')  # Passen Sie die Klasse an, falls sie anders ist
    
    for gallery_link in gallery_links:
        galerie_slug = gallery_link.get('href').split('/')[-1]  # Extrahiert den Slug der Galerie
        galerie_titel = gallery_link.get_text().strip()  # Titel der Galerie

        # Galerie-Daten in ein Dictionary speichern
        galerie = {
            'slug': galerie_slug,
            'titel': galerie_titel,
            'bilder': []
        }

        # Jedes Bild aus der Galerie extrahieren
        bild_tags = gallery_link.find_all('img')

        for bild_tag in bild_tags:
            bild_url = bild_tag.get('src')  # Bild-URL extrahieren
            bild_link = f"https://www.pictrs.com{bild_url}"  # Vollständige URL des Bildes
            
            galerie['bilder'].append({
                'bild': bild_link,
                'link': f'https://deinshop.pictrs.com/galerie/{galerie_slug}/{bild_url.split("/")[-1]}'
            })

        # Die Galerie zur Liste hinzufügen
        galerien.append(galerie)

    return galerien

# Funktion, um die gesammelten Galerie-Daten als JSON-Datei zu speichern
def save_to_json(galerien):
    with open('galerien.json', 'w', encoding='utf-8') as f:
        json.dump(galerien, f, ensure_ascii=False, indent=4)
    print("Daten erfolgreich in 'galerien.json' gespeichert!")

# Hauptprogramm
if __name__ == "__main__":
    galerien = fetch_galerien()  # Galerien abrufen
    if galerien:
        save_to_json(galerien)  # Wenn Galerien gefunden wurden, speichere sie als JSON
