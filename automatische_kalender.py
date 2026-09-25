import sqlite3
import datetime
import ephem
from dateutil.relativedelta import relativedelta, SU

DB_BESTAND = 'evenementen.db'

def update_of_voeg_toe(cursor, naam, datum, categorie, locatie, afbeelding, forceer_update=False):
    cursor.execute("SELECT datum FROM events WHERE naam = ?", (naam,))
    result = cursor.fetchone()
    
    nieuwe_datum_str = datum.strftime("%Y-%m-%d")
    
    if result:
        huidige_datum_str = result[0]
        try:
            huidige_datum = datetime.datetime.strptime(huidige_datum_str, "%Y-%m-%d").date()
        except ValueError:
            huidige_datum = datetime.date.today() - datetime.timedelta(days=1)
            
        if huidige_datum < datetime.date.today() or forceer_update:
            cursor.execute("UPDATE events SET datum = ?, categorie = ?, locatie = ?, afbeelding = ? WHERE naam = ?", 
                           (nieuwe_datum_str, categorie, locatie, afbeelding, naam))
            print(f"Geüpdatet: {naam} (Categorie: {categorie})")
        else:
            print(f"Overgeslagen: {naam} staat al correct in de toekomst ({huidige_datum_str})")
    else:
        cursor.execute('''
            INSERT INTO events (naam, datum, categorie, locatie, afbeelding) 
            VALUES (?, ?, ?, ?, ?)
        ''', (naam, nieuwe_datum_str, categorie, locatie, afbeelding))
        print(f"Toegevoegd: {naam} gepland op {nieuwe_datum_str} als {categorie}")

def bereken_datums():
    vandaag = datetime.date.today()
    conn = sqlite3.connect(DB_BESTAND)
    cursor = conn.cursor()

    maanden_nl = {
        1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
        9: "September", 10: "Oktober", 11: "November", 12: "December"
    }

    try:
        # 1. Maancyclus (6 Volle en 6 Nieuwe manen vooruit)
        # Verwijder eerst de oude, generieke maan-registraties
        cursor.execute("DELETE FROM events WHERE naam = 'Volle Maan'")
        cursor.execute("DELETE FROM events WHERE naam = 'Nieuwe Maan'")
        
        reken_datum_vol = vandaag
        for i in range(6):
            volgende_volle = ephem.next_full_moon(reken_datum_vol).datetime().date()
            naam_vol = f"Volle Maan ({maanden_nl[volgende_volle.month]} {volgende_volle.year})"
            update_of_voeg_toe(cursor, naam_vol, volgende_volle, "seizoen", "Ruimte", "https://hoelangnogtot.nl/images/volle-maan.jpg", forceer_update=True)
            # Zet de reken_datum vooruit naar de dag ná de gevonden maan om de volgende te vinden
            reken_datum_vol = volgende_volle + datetime.timedelta(days=1)

        reken_datum_nieuw = vandaag
        for i in range(6):
            volgende_nieuwe = ephem.next_new_moon(reken_datum_nieuw).datetime().date()
            naam_nieuw = f"Nieuwe Maan ({maanden_nl[volgende_nieuwe.month]} {volgende_nieuwe.year})"
            update_of_voeg_toe(cursor, naam_nieuw, volgende_nieuwe, "seizoen", "Ruimte", "https://hoelangnogtot.nl/images/nieuwe-maan.jpg", forceer_update=True)
            reken_datum_nieuw = volgende_nieuwe + datetime.timedelta(days=1)

        # 2. De 12 maanden (Rollende horizon voor een heel jaar)
        cursor.execute("DELETE FROM events WHERE naam = 'Start Nieuwe Maand'")
        
        for mnd_num, mnd_naam in maanden_nl.items():
            jaar = vandaag.year
            if vandaag.month > mnd_num or (vandaag.month == mnd_num and vandaag.day > 1):
                jaar += 1
            
            start_datum = datetime.date(jaar, mnd_num, 1)
            naam = f"Start {mnd_naam}"
            
            update_of_voeg_toe(cursor, naam, start_datum, "seizoen", "Wereldwijd", "https://hoelangnogtot.nl/images/nieuwe-maand.jpg", forceer_update=True)

        # 3. Award Shows
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
