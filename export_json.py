import sqlite3
import json

def exporteer_naar_json():
    conn = sqlite3.connect('evenementen.db')
    
    # Deze instelling zorgt ervoor dat we de kolomnamen uit de database behouden
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    # Haal alle opgeslagen data op
    cursor.execute("SELECT * FROM events")
    rijen = cursor.fetchall()

    # Zet de tabelrijen om naar een formaat dat JSON begrijpt (dictionaries)
    evenementen_lijst = [dict(rij) for rij in rijen]

    # Schrijf alles weg naar een nieuw JSON-bestand met de juiste codering
    with open('evenementen.json', 'w', encoding='utf-8') as json_bestand:
        json.dump(evenementen_lijst, json_bestand, indent=4, ensure_ascii=False)

    conn.close()
    print(f"Succes: {len(evenementen_lijst)} evenementen zijn geëxporteerd naar evenementen.json.")

if __name__ == "__main__":
    exporteer_naar_json()