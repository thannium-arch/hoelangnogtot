import os
import sqlite3

BESTAND = 'wensenlijst.txt'
DB_BESTAND = 'evenementen.db'

def voeg_sport_toe(naam, datum, locatie):
    # Maak direct verbinding met je database
    conn = sqlite3.connect(DB_BESTAND)
    cursor = conn.cursor()
    
    # We voegen een standaard sportafbeelding toe en zetten de categorie op 'sport'
    afbeelding_url = "https://hoelangnogtot.nl/images/standaard-sport.jpg"
    
    try:
        cursor.execute('''
            INSERT INTO evenementen (naam, datum, categorie, locatie, afbeelding) 
            VALUES (?, ?, ?, ?, ?)
        ''', (naam, datum, 'sport', locatie, afbeelding_url))
        conn.commit()
        print(f"Succesvol toegevoegd aan database: {naam}")
    except sqlite3.Error as e:
        print(f"Fout bij opslaan in database: {e}")
    finally:
        conn.close()

def verwerk_lijst():
    if not os.path.exists(BESTAND):
        return

    with open(BESTAND, 'r', encoding='utf-8') as f:
        regels = f.readlines()

    if not regels:
        return

    resterende_regels = []
    verwerkt = False

    for regel in regels:
        schone_regel = regel.strip()
        
        # Negeer lege regels of regels zonder dubbele punt
        if not schone_regel or ':' not in schone_regel:
            resterende_regels.append(schone_regel)
            continue

        delen = schone_regel.split(':', 1)
        categorie = delen[0].strip().lower()
        rest = delen[1].strip()

        if categorie == 'sport':
            # Splits de data op basis van het verticale streepje
            sport_delen = [deel.strip() for deel in rest.split('|')]
            naam = sport_delen[0]
            
            # Valback waarden voor als je per ongeluk een datum of locatie vergeet in te vullen
            datum = sport_delen[1] if len(sport_delen) > 1 else '2027-01-01'
            locatie = sport_delen[2] if len(sport_delen) > 2 else 'Internationaal'
            
            voeg_sport_toe(naam, datum, locatie)
            verwerkt = True
        else:
            # Zet films, games of concerten terug in de lijst, klaar voor je externe API scripts
            resterende_regels.append(schone_regel)

    # Overschrijf het tekstbestand zodat de succesvol verwerkte sportevenementen eruit zijn
    if verwerkt:
        with open(BESTAND, 'w', encoding='utf-8') as f:
            for r in resterende_regels:
                if r:  
                    f.write(f"{r}\n")

if __name__ == "__main__":
    verwerk_lijst()
