import requests
from bs4 import BeautifulSoup
import json
import os

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

    # Alle Galerien finden
    gallery_links = soup.find_all('a', class_='albums-grid-item')  # Hier die richtige Klasse für die Galerie-Links
    print(f"Gefundene Galerien: {len(gallery_links)}")

    for gallery_link in gallery_links:
        galerie_slug = gallery_link.get('href').split('/')[-2]  # Extrahiert den Slug der Galerie aus der URL
        galerie_titel = gallery_link.find('span', class_='albums-grid-title').get_text().strip()  # Titel der Galerie
        galerie_bilder_count = gallery_link.find('small', class_='albums-grid-details').get_text().strip()  # Anzahl der Bilder

        # Galerie-Daten in ein Dictionary speichern
        galerie = {
            'slug': galerie_slug,
            'titel': galerie_titel,
            'bilder': [],
            'bilder_count': galerie_bilder_count  # Anzahl der Bilder
        }

        # Das Hintergrundbild des <div> mit der Klasse 'albums-grid-image' extrahieren
        bild_url = gallery_link.find('div', class_='albums-grid-image').get('style').split('url(')[-1].split(')')[0]  # Bild-URL extrahieren
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
    # Den Pfad zum aktuellen Verzeichnis ermitteln
    current_directory = os.getcwd()  # Verwendet das Arbeitsverzeichnis der GitHub Actions Umgebung
    json_file_path = os.path.join(current_directory, 'pictrs-gallery', 'galerien.json')  # Setzt den Pfad für die JSON-Datei

    # Überprüfen, ob der Pfad korrekt ist
    print(f"Speichere die Datei in: {json_file_path}")

    # Überprüfe, ob das Verzeichnis existiert, falls nicht, dann erstelle es
    if not os.path.exists(os.path.dirname(json_file_path)):
        os.makedirs(os.path.dirname(json_file_path))
        print(f"Verzeichnis {os.path.dirname(json_file_path)} wurde erstellt.")

    # Die JSON-Datei speichern
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(galerien, f, ensure_ascii=False, indent=4)
    print(f"Daten erfolgreich in '{json_file_path}' gespeichert!")

# Hauptprogramm
if __name__ == "__main__":
    galerien = fetch_galerien()  # Galerien abrufen
    if galerien:
        save_to_json(galerien)  # Wenn Galerien gefunden wurden, speichere sie als JSON
