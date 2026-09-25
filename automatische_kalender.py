import sqlite3
import datetime
import ephem
from dateutil.relativedelta import relativedelta, SU

DB_BESTAND = 'evenementen.db'

def update_of_voeg_toe(cursor, naam, datum, categorie, locatie, afbeelding, forceer_update=False):
    # Controleer of het evenement al in de database staat
    cursor.execute("SELECT datum FROM events WHERE naam = ?", (naam,))
    result = cursor.fetchone()
    
    nieuwe_datum_str = datum.strftime("%Y-%m-%d")
    
    if result:
        huidige_datum_str = result[0]
        try:
            huidige_datum = datetime.datetime.strptime(huidige_datum_str, "%Y-%m-%d").date()
        except ValueError:
            huidige_datum = datetime.date.today() - datetime.timedelta(days=1)
            
        # Alleen updaten als de datum in het verleden ligt, OF als we een correctie forceren
        if huidige_datum < datetime.date.today() or forceer_update:
            cursor.execute("UPDATE events SET datum = ?, categorie = ?, locatie = ?, afbeelding = ? WHERE naam = ?", 
                           (nieuwe_datum_str, categorie, locatie, afbeelding, naam))
            print(f"Geüpdatet: {naam} (Categorie: {categorie})")
        else:
            print(f"Overgeslagen: {naam} staat al correct in de toekomst ({huidige_datum_str})")
    else:
        # Bestaat nog niet, dus toevoegen
        cursor.execute('''
            INSERT INTO events (naam, datum, categorie, locatie, afbeelding) 
            VALUES (?, ?, ?, ?, ?)
        ''', (naam, nieuwe_datum_str, categorie, locatie, afbeelding))
        print(f"Toegevoegd: {naam} gepland op {nieuwe_datum_str} als {categorie}")

def bereken_datums():
    vandaag = datetime.date.today()
    conn = sqlite3.connect(DB_BESTAND)
    cursor = conn.cursor()

    try:
        # 1. Maancyclus (Aangepast naar 'seizoen' en forceer_update=True toegevoegd)
        volgende_volle_maan = ephem.next_full_moon(vandaag).datetime().date()
        volgende_nieuwe_maan = ephem.next_new_moon(vandaag).datetime().date()
        
        update_of_voeg_toe(cursor, "Volle Maan", volgende_volle_maan, "seizoen", "Ruimte", "https://hoelangnogtot.nl/images/volle-maan.jpg", forceer_update=True)
        update_of_voeg_toe(cursor, "Nieuwe Maan", volgende_nieuwe_maan, "seizoen", "Ruimte", "https://hoelangnogtot.nl/images/nieuwe-maan.jpg", forceer_update=True)

        # 2. Eerste dag van de volgende maand (Aangepast naar 'seizoen' en forceer_update=True)
        eerste_volgende_maand = (vandaag.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        update_of_voeg_toe(cursor, "Start Nieuwe Maand", eerste_volgende_maand, "seizoen", "Wereldwijd", "https://hoelangnogtot.nl/images/nieuwe-maand.jpg", forceer_update=True)

        # 3. Award Shows (Blijven 'cultuur' / 'film' / 'concert')
        jaar_oscars = vandaag.year if vandaag.month < 3 or (vandaag.month == 3 and vandaag.day < 15) else vandaag.year + 1
        oscars_datum = datetime.date(jaar_oscars, 3, 1) + relativedelta(weekday=SU(+2))
        update_of_voeg_toe(cursor, "Oscars", oscars_datum, "film", "Los Angeles", "https://hoelangnogtot.nl/images/oscars.jpg")

        jaar_grammys = vandaag.year if vandaag.month < 2 or (vandaag.month == 2 and vandaag.day < 10) else vandaag.year + 1
        grammys_datum = datetime.date(jaar_grammys, 2, 1) + relativedelta(weekday=SU(+1))
        update_of_voeg_toe(cursor, "Grammy Awards", grammys_datum, "concert", "Los Angeles", "https://hoelangnogtot.nl/images/grammys.jpg")

        jaar_tonys = vandaag.year if vandaag.month < 6 or (vandaag.month == 6 and vandaag.day < 15) else vandaag.year + 1
        tonys_datum = datetime.date(jaar_tonys, 6, 1) + relativedelta(weekday=SU(+2))
        update_of_voeg_toe(cursor, "Tony Awards", tonys_datum, "cultuur", "New York", "https://hoelangnogtot.nl/images/tonys.jpg")

        jaar_emmys = vandaag.year if vandaag.month < 9 or (vandaag.month == 9 and vandaag.day < 25) else vandaag.year + 1
        emmys_datum = datetime.date(jaar_emmys, 9, 1) + relativedelta(weekday=SU(+3))
        update_of_voeg_toe(cursor, "Emmy Awards", emmys_datum, "film", "Los Angeles", "https://hoelangnogtot.nl/images/emmys.jpg")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database fout: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    bereken_datums()
