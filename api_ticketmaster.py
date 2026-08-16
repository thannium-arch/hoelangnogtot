import sqlite3
import requests
import time

# Vul hier jouw Ticketmaster Consumer Key in
API_KEY = 'GOifHJA3hTl1AJLl1Neck5dcEMnKlqfX' 

def haal_events_op_per_zaal(venue_keyword):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        'apikey': API_KEY,
        'keyword': venue_keyword,
        'countryCode': 'NL',
        'sort': 'date,asc',
        'size': 50
    }
    
    print(f"Zoeken naar evenementen voor: {venue_keyword}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if '_embedded' in data and 'events' in data['_embedded']:
            return data['_embedded']['events']
    else:
        print(f"Fout bij ophalen {venue_keyword}: {response.status_code}")
    
    return []

def haal_alle_festivals_op():
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        'apikey': API_KEY,
        'countryCode': 'NL',
        'classificationName': 'Festival',
        'sort': 'date,asc',
        'size': 100 # Haalt de komende 100 festivals op
    }
    
    print("Zoeken naar alle festivals in Nederland...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if '_embedded' in data and 'events' in data['_embedded']:
            return data['_embedded']['events']
    else:
        print(f"Fout bij ophalen festivals: {response.status_code}")
    
    return []

def verwerk_events(events, standaard_locatie, categorie, icon):
    conn = sqlite3.connect('evenementen.db')
    cursor = conn.cursor()
    
    aantal_toegevoegd = 0
    aantal_geupdate = 0
    
    for event in events:
        naam = event.get('name')
        
        # Haal de startdatum op
        dates = event.get('dates', {}).get('start', {})
        datum = dates.get('dateTime') 
        if not datum:
            continue 
        
        url = event.get('url', '#')
        
        # Bepaal de locatie
        locatie_naam = standaard_locatie
        venues = event.get('_embedded', {}).get('venues', [])
        if venues and 'name' in venues[0]:
            locatie_naam = venues[0]['name']
            city = venues[0].get('city', {}).get('name', '')
            if city and city.lower() not in locatie_naam.lower():
                locatie_naam = f"{locatie_naam}, {city}"
        
        # Haal de afbeelding op
        afbeelding = ''
        images = event.get('images', [])
        if images:
            afbeelding = images[0].get('url', '')
        
        # Controleer voorverkoop logica
        presale_datum = ''
        sales = event.get('sales', {})
        
        if 'public' in sales and 'startDateTime' in sales['public']:
            presale_datum = sales['public']['startDateTime']
        elif 'presales' in sales and len(sales['presales']) > 0:
            presale_datum = sales['presales'][0].get('startDateTime', '')

        affiliate_url = url
        affiliate_tekst = "Bestel Tickets"

        cursor.execute('SELECT id FROM events WHERE naam = ? AND datum = ?', (naam, datum))
        bestaand_event = cursor.fetchone()

        if not bestaand_event:
            cursor.execute('''
                INSERT INTO events (naam, categorie, icon, vlag, locatie, datum, url, afbeelding, presaleDatum, regio, urgencyStartDatum, urgencyLabel, urgencyIcon, affiliateUrl, affiliateTekst)
                VALUES (?, ?, ?, 'nl', ?, ?, ?, ?, ?, '', '', '', '', ?, ?)
            ''', (naam, categorie, icon, locatie_naam, datum, url, afbeelding, presale_datum, affiliate_url, affiliate_tekst))
            aantal_toegevoegd += 1
        else:
            cursor.execute('''
                UPDATE events 
                SET url = ?, afbeelding = ?, presaleDatum = ?, affiliateUrl = ?, affiliateTekst = ?, locatie = ?
                WHERE id = ?
            ''', (url, afbeelding, presale_datum, affiliate_url, affiliate_tekst, locatie_naam, bestaand_event[0]))
            aantal_geupdate += 1
            
    conn.commit()
    conn.close()
    
    if standaard_locatie == "Nederland":
        print(f"Festivals: {aantal_toegevoegd} nieuwe toegevoegd, {aantal_geupdate} geüpdatet.")
    else:
        print(f"{standaard_locatie}: {aantal_toegevoegd} nieuwe toegevoegd, {aantal_geupdate} geüpdatet.")

if __name__ == "__main__":
    # DEEL 1: Specifieke zalen verwerken
    zalen = [
        "Ziggo Dome", 
        "AFAS Live", 
        "Het Concertgebouw", 
        "De Doelen", 
        "TivoliVredenburg", 
        "Paradiso", 
        "013 Popcentrum", 
        "Paard van Troje", 
        "Bird Rotterdam", 
        "Doornroosje"
    ]
    
    for zaal in zalen:
        gevonden_events = haal_events_op_per_zaal(zaal)
        if gevonden_events:
            verwerk_events(gevonden_events, standaard_locatie=zaal, categorie='concert', icon='fa-music')
        
        # Korte pauze om de API niet te overbelasten
        time.sleep(1)
        
    # DEEL 2: Alle landelijke festivals verwerken
    festivals = haal_alle_festivals_op()
    if festivals:
        verwerk_events(festivals, standaard_locatie="Nederland", categorie='festival', icon='fa-tent')
        
    print("Klaar! Je database is weer helemaal up-to-date met concerten én festivals.")