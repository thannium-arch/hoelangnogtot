import sqlite3
import requests
import datetime
import time
import urllib.parse

# Vul hier jouw Twitch Developer gegevens in
CLIENT_ID = '939r9khzld2vw6c7pxygkyl8v4vzj0'
CLIENT_SECRET = 'wkj9fvpcuzcssy1ilur9cu2yfsy3gx'

def haal_twitch_token_op():
    url = f"https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("Fout bij het ophalen van het Twitch token.")
        return None

def haal_grote_games_op(token):
    url = "https://api.igdb.com/v4/games"
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'text/plain'
    }
    
    vandaag_timestamp = int(time.time())
    
    query = f"fields name, first_release_date, cover.image_id, platforms.name, category, hypes, follows; where first_release_date > {vandaag_timestamp} & follows != null; sort follows desc; limit 100;"
    
    response = requests.post(url, headers=headers, data=query.encode('utf-8'))
    
    if response.status_code == 200:
        games = response.json()
        print(f"Succes! Er zijn {len(games)} titels binnengehaald om lokaal te filteren.")
        return games
    else:
        print(f"Fout bij ophalen games. Status code: {response.status_code}")
        print(f"Foutmelding vanuit Twitch: {response.text}")
        return []

def verwerk_games(games):
    conn = sqlite3.connect('evenementen.db')
    cursor = conn.cursor()
    
    aantal_toegevoegd = 0
    aantal_geupdate = 0
    
    for game in games:
        naam = game.get('name')
        release_timestamp = game.get('first_release_date')
        
        if not release_timestamp or not naam:
            continue
            
        hypes = game.get('hypes', 0)
        follows = game.get('follows', 0)
        
        if hypes < 25 and follows < 25:
            continue
            
        release_date = datetime.datetime.fromtimestamp(release_timestamp).strftime('%Y-%m-%dT00:00:00')
        
        afbeelding = ""
        if 'cover' in game and 'image_id' in game['cover']:
            afbeelding = f"https://images.igdb.com/igdb/image/upload/t_1080p/{game['cover']['image_id']}.jpg"
        else:
            afbeelding = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500&q=80"
            
        platforms = game.get('platforms', [])
        platform_namen = [p.get('name') for p in platforms if 'name' in p]
        
        locatie_tekst = ", ".join(platform_namen[:3]) if platform_namen else "Spelcomputers / PC"
        if len(platform_namen) > 3:
            locatie_tekst += " e.a."
            
        zoek_term_youtube = naam.replace(" ", "+")
        zoek_term_webshop = urllib.parse.quote_plus(naam + " game")
        
        # De reguliere URL blijft de YouTube trailer
        trailer_url = f"https://www.youtube.com/results?search_query={zoek_term_youtube}+official+trailer"
        
        # De affiliate URL is de webshop link
        affiliate_url = f"https://www.bol.com/nl/nl/s/?searchtext={zoek_term_webshop}"
        affiliate_tekst = "Bestel / Pre-order"
        
        cursor.execute('SELECT id FROM events WHERE naam = ? AND categorie = "gaming"', (naam,))
        bestaand = cursor.fetchone()
        
        if not bestaand:
            cursor.execute('''
                INSERT INTO events (
                    naam, categorie, icon, vlag, locatie, datum, url, afbeelding, 
                    presaleDatum, regio, urgencyStartDatum, urgencyLabel, urgencyIcon, 
                    affiliateUrl, affiliateTekst
                ) VALUES (?, 'gaming', 'fa-gamepad', 'globe', ?, ?, ?, ?, 
                '', 'Wereldwijd', '', '', '', ?, ?)
            ''', (naam, locatie_tekst, release_date, trailer_url, afbeelding, affiliate_url, affiliate_tekst))
            aantal_toegevoegd += 1
        else:
            cursor.execute('''
                UPDATE events 
                SET datum = ?, afbeelding = ?, locatie = ?, url = ?, affiliateUrl = ?, affiliateTekst = ?
                WHERE id = ?
            ''', (release_date, afbeelding, locatie_tekst, trailer_url, affiliate_url, affiliate_tekst, bestaand[0]))
            aantal_geupdate += 1
            
    conn.commit()
    conn.close()
    
    print(f"Klaar! {aantal_toegevoegd} games toegevoegd en {aantal_geupdate} geüpdatet met zowel trailer- als pre-orderlink.")

if __name__ == "__main__":
    print("Stap 1: Inloggen bij Twitch...")
    token = haal_twitch_token_op()
    
    if token:
        print("Stap 2: Zoeken naar de grootste aankomende games via IGDB...")
        komende_games = haal_grote_games_op(token)
        
        if komende_games:
            print("Stap 3: Games filteren en wegschrijven naar de database...")
            verwerk_games(komende_games)
        else:
            print("Stap 3 overgeslagen: Geen nieuwe games gevonden om te verwerken.")
    else:
        print("Script afgebroken: Geen geldige inloggegevens ontvangen.")