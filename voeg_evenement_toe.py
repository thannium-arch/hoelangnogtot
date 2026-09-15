import os
import sqlite3
import sys

DB_BESTAND = 'evenementen.db'

naam = os.environ.get("INPUT_NAAM")
datum = os.environ.get("INPUT_DATUM")
categorie = os.environ.get("INPUT_CATEGORIE")
locatie = os.environ.get("INPUT_LOCATIE")

if not naam or not datum:
    print("Fout: Naam en datum zijn verplicht.")
    sys.exit(1)

afbeelding_url = f"https://hoelangnogtot.nl/images/standaard-{categorie.lower()}.jpg"

try:
    conn = sqlite3.connect(DB_BESTAND)
    cursor = conn.cursor()
    
    # We voegen de data nu toe aan de juiste tabel: 'events'
    cursor.execute('''
        INSERT INTO events (naam, datum, categorie, locatie, afbeelding) 
        VALUES (?, ?, ?, ?, ?)
    ''', (naam, datum, categorie, locatie, afbeelding_url))
    
    conn.commit()
    print(f"Succes: '{naam}' is succesvol toegevoegd aan de tabel 'events'!")
except sqlite3.Error as e:
    print(f"Database fout: {e}")
    sys.exit(1)
finally:
    if 'conn' in locals():
        conn.close()
