import sqlite3
import datetime
import calendar

# --- REKENFUNCTIES VOOR WISSELENDE DATUMS ---

def bereken_pasen(jaar):
    a = jaar % 19
    b = jaar // 100
    c = jaar % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    maand = (h + l - 7 * m + 114) // 31
    dag = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(jaar, maand, dag)

def laatste_weekdag_van_maand(jaar, maand, weekdag):
    # weekdag: 0=maandag, 6=zondag
    dagen_in_maand = calendar.monthrange(jaar, maand)[1]
    laatste_dag = datetime.date(jaar, maand, dagen_in_maand)
    offset = (laatste_dag.weekday() - weekdag) % 7
    return laatste_dag - datetime.timedelta(days=offset)

def n_de_weekdag_van_maand(jaar, maand, weekdag, n):
    eerste_dag = datetime.date(jaar, maand, 1)
    offset = (weekdag - eerste_dag.weekday()) % 7
    eerste_gezochte_dag = eerste_dag + datetime.timedelta(days=offset)
    return eerste_gezochte_dag + datetime.timedelta(weeks=n-1)

# --- DATABASE UPDATE FUNCTIE ---

def update_database():
    conn = sqlite3.connect('evenementen.db')
    cursor = conn.cursor()

    # 1. Opschonen van oude generieke data (om dubbele vermeldingen te voorkomen)
    te_verwijderen = ['Eerste Kerstdag', 'Tweede Kerstdag', 'Nieuwjaarsdag', 'Goede Vrijdag', 'Eerste Paasdag', 'Tweede Paasdag']
    for naam in te_verwijderen:
        cursor.execute('DELETE FROM events WHERE naam = ? AND categorie = "feestdag"', (naam,))
    
    # Bepaal het huidige jaar en kijk of we al moeten doorschuiven naar volgend jaar
    vandaag = datetime.date.today()
    jaar = vandaag.year

    # 2. BEREKENINGEN VOOR DIT JAAR (of doorschuiven naar volgend jaar indien verstreken)
    
    # Pasen
    paas_datum = bereken_pasen(jaar)
    if paas_datum < vandaag:
        paas_datum = bereken_pasen(jaar + 1)
    jaar_pasen = paas_datum.year
    tweede_paas_datum = paas_datum + datetime.timedelta(days=1)

    # Zomertijd / Wintertijd (Laatste zondag van maart en oktober)
    zomertijd = laatste_weekdag_van_maand(jaar, 3, 6)
    wintertijd = laatste_weekdag_van_maand(jaar, 10, 6)
    if zomertijd < vandaag: zomertijd = laatste_weekdag_van_maand(jaar + 1, 3, 6)
    if wintertijd < vandaag: wintertijd = laatste_weekdag_van_maand(jaar + 1, 10, 6)

    # Seizoenen (Meteorologische start - vaak 20/21, we pakken een veilige vaste datum voor de kalender)
    lente = datetime.date(jaar, 3, 20)
    zomer = datetime.date(jaar, 6, 21)
    herfst = datetime.date(jaar, 9, 22)
    winter = datetime.date(jaar, 12, 21)
    
    if lente < vandaag: lente = datetime.date(jaar + 1, 3, 20)
    if zomer < vandaag: zomer = datetime.date(jaar + 1, 6, 21)
    if herfst < vandaag: herfst = datetime.date(jaar + 1, 9, 22)
    if winter < vandaag: winter = datetime.date(jaar + 1, 12, 21)

    # Inhaakkalender: Black Friday (Dag na de 4e donderdag van november)
    thanksgiving = n_de_weekdag_van_maand(jaar, 11, 3, 4)
    black_friday = thanksgiving + datetime.timedelta(days=1)
    if black_friday < vandaag:
        black_friday = n_de_weekdag_van_maand(jaar + 1, 11, 3, 4) + datetime.timedelta(days=1)

    # Inhaakkalender: Blue Monday (3e maandag van januari)
    blue_monday = n_de_weekdag_van_maand(jaar, 1, 0, 3)
    if blue_monday < vandaag:
        blue_monday = n_de_weekdag_van_maand(jaar + 1, 1, 0, 3)

    # 3. VERZAMELING VAN ALLE EVENTS
    ah_affiliate_url = "https://www.ah.nl/"
    bol_affiliate_url = "https://www.bol.com/"

    events = [
        # Feestdagen
        {"naam": f"Eerste Paasdag {jaar_pasen}", "cat": "feestdag", "datum": paas_datum, "icon": "fa-egg", "img": "https://images.unsplash.com/photo-1522337660859-02fbefca4702?w=400&q=80", "url": ah_affiliate_url, "knop": "Bestel AH Thuisbezorgd"},
        {"naam": f"Tweede Paasdag {jaar_pasen}", "cat": "feestdag", "datum": tweede_paas_datum, "icon": "fa-egg", "img": "https://images.unsplash.com/photo-1522337660859-02fbefca4702?w=400&q=80", "url": ah_affiliate_url, "knop": "Bestel AH Thuisbezorgd"},
        
        # Tijdverzettingen (categorie 'seizoen' zorgt in je frontend dat er geen categorie-label staat)
        {"naam": f"Start Zomertijd {zomertijd.year}", "cat": "seizoen", "datum": zomertijd, "icon": "fa-clock", "img": "https://images.unsplash.com/photo-1501139083538-0139583c060f?w=400&q=80", "url": "", "knop": ""},
        {"naam": f"Start Wintertijd {wintertijd.year}", "cat": "seizoen", "datum": wintertijd, "icon": "fa-clock", "img": "https://images.unsplash.com/photo-1501139083538-0139583c060f?w=400&q=80", "url": "", "knop": ""},
        
        # Seizoenen
        {"naam": f"Start Lente {lente.year}", "cat": "seizoen", "datum": lente, "icon": "fa-leaf", "img": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&q=80", "url": "", "knop": ""},
        {"naam": f"Start Zomer {zomer.year}", "cat": "seizoen", "datum": zomer, "icon": "fa-sun", "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80", "url": "", "knop": ""},
        {"naam": f"Start Herfst {herfst.year}", "cat": "seizoen", "datum": herfst, "icon": "fa-wind", "img": "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=400&q=80", "url": "", "knop": ""},
        {"naam": f"Start Winter {winter.year}", "cat": "seizoen", "datum": winter, "icon": "fa-snowflake", "img": "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?w=400&q=80", "url": "", "knop": ""},

        # Inhaakkalender
        {"naam": f"Black Friday {black_friday.year}", "cat": "inhaak", "datum": black_friday, "icon": "fa-tags", "img": "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400&q=80", "url": bol_affiliate_url, "knop": "Bekijk Acties"},
        {"naam": f"Blue Monday {blue_monday.year}", "cat": "inhaak", "datum": blue_monday, "icon": "fa-face-frown", "img": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=400&q=80", "url": bol_affiliate_url, "knop": "Vrolijk jezelf op"}
    ]

    # 4. DATABASE UPDATEN OF TOEVOEGEN
    for ev in events:
        datum_str = ev["datum"].strftime('%Y-%m-%dT00:00:00')
        
        # Checken of deze specifieke dag (met dit jaartal) al in de database staat
        cursor.execute('SELECT id FROM events WHERE naam = ? AND categorie = ?', (ev["naam"], ev["cat"]))
        bestaand = cursor.fetchone()
        
        if not bestaand:
            cursor.execute('''
                INSERT INTO events (
                    naam, categorie, icon, vlag, locatie, datum, url, afbeelding, 
                    presaleDatum, regio, urgencyStartDatum, urgencyLabel, urgencyIcon, 
                    affiliateUrl, affiliateTekst
                ) VALUES (?, ?, ?, 'NL', 'Nederland', ?, '', ?, 
                '', 'Heel Nederland', '', '', '', ?, ?)
            ''', (ev["naam"], ev["cat"], ev["icon"], datum_str, ev["img"], ev["url"], ev["knop"]))
        else:
            cursor.execute('''
                UPDATE events 
                SET datum = ?, afbeelding = ?, affiliateUrl = ?, affiliateTekst = ?
                WHERE id = ?
            ''', (datum_str, ev["img"], ev["url"], ev["knop"], bestaand[0]))

    conn.commit()
    conn.close()
    print("Kalender succesvol geüpdatet: Pasen, Seizoenen, Tijdverzettingen en Inhaakmomenten staan klaar.")

if __name__ == "__main__":
    update_database()