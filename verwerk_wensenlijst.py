import os
import sqlite3

BESTAND = 'wensenlijst.txt'
DB_BESTAND = 'evenementen.db'

def voeg_sport_toe(naam, datum, locatie):
    conn = sqlite3.connect(DB_BESTAND)
    cursor = conn.cursor()
    
    afbeelding_url = "https://hoelangnogtot.nl/images/standaard-sport.jpg"
    
    try:
        cursor.execute('''
            INSERT INTO evenementen (naam, datum, categorie, locatie, afbeelding) 
            VALUES (?, ?, ?, ?, ?)
        ''', (naam, datum, 'sport', locatie, afbeelding_url))
        conn.commit()
        print(f"Succesvol toegevoegd aan database: {naam}")
        succes = True
    except sqlite3.Error as e:
        print(f"CRITIEKE FOUT bij database: {e}")
        succes = False
    finally:
        conn.close()
        
    return succes

def verwerk_lijst():
    if not os.path.exists(BESTAND):
        return

    with open(BESTAND, 'r', encoding='utf-8') as f:
        regels = f.readlines()

    if not regels:
        return

    resterende_regels = []

    for regel in regels:
        schone_regel = regel.strip()
        
        if not schone_regel or ':' not in schone_regel:
            resterende_regels.append(schone_regel)
            continue

        delen = schone_regel.split(':', 1)
        categorie = delen[0].strip().lower()
        rest = delen[1].strip()

        if categorie == 'sport':
            sport_delen = [deel.strip() for deel in rest.split('|')]
            naam = sport_delen[0]
            datum = sport_delen[1] if len(sport_delen) > 1 else '2027-01-01'
            locatie = sport_delen[2] if len(sport_delen) > 2 else 'Internationaal'
            
            # De syntax is nu correct in het Engels
            if not voeg_sport_toe(naam, datum, locatie):
                resterende_regels.append(schone_regel)
        else:
            resterende_regels.append(schone_regel)

    with open(BESTAND, 'w', encoding='utf-8') as f:
        for r in resterende_regels:
            if r:  
                f.write(f"{r}\n")

if __name__ == "__main__":
    verwerk_lijst()
