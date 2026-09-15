import os
import sqlite3
import sys

DB_BESTAND = 'evenementen.db'

# 1. Inspecteer de database eerst
try:
    conn = sqlite3.connect(DB_BESTAND)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabellen = cursor.fetchall()
    
    if not tabellen:
        print("LET OP: De database is compleet leeg! (Waarschijnlijk een nieuw, onzichtbaar bestand)")
    else:
        print(f"Gevonden tabellen in de database: {tabellen}")
except sqlite3.Error as e:
    print(f"Kan database niet lezen: {e}")

# 2. Ga verder met de toevoeging (om de foutmelding te forceren als het mis is)
naam = os.environ.get("INPUT_NAAM")
datum = os.environ.get("INPUT_DATUM")
categorie = os.environ.get("INPUT_CATEGORIE")
locatie = os.environ.get("INPUT_LOCATIE")

if not naam or not datum:
    print("Fout: Naam en datum zijn verplicht.")
    sys.exit(1)

afbeelding_url = f"https://hoelangnogtot.nl/images/standaard-{categorie.lower()}.jpg"

try:
    cursor.execute('''
        INSERT INTO evenementen (naam, datum, categorie, locatie, afbeelding) 
        VALUES (?, ?, ?, ?, ?)
    ''', (naam, datum, categorie, locatie, afbeelding_url))
    conn.commit()
    print(f"Succes: '{naam}' is toegevoegd aan de database.")
except sqlite3.Error as e:
    print(f"Database fout: {e}")
    sys.exit(1)
finally:
    conn.close()
