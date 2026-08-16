import sqlite3
import requests
import datetime

# Vul hier jouw TMDB API Key in
API_KEY = '28e96abff420de37f09fca90726e907a'

def haal_grote_films_op():
    vandaag = datetime.date.today().isoformat()
    eind_datum = (datetime.date.today() + datetime.timedelta(days=500)).isoformat()
    
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        'api_key': API_KEY,
        'language': 'nl-NL',
        'region': 'NL', 
        'primary_release_date.gte': vandaag,
        'primary_release_date.lte': eind_datum,
        'sort_by': 'popularity.desc', 
        'include_adult': 'false',
        'with_original_language': 'en|nl', 
        'page': 1
    }
    
    print("Zoeken naar de grootste aankomende bioscoopfilms...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])[:25]
    else:
        print(f"Fout bij ophalen films: {response.status_code}")
        return []

def haal_grote_series_op():
    vandaag = datetime.date.today().isoformat()
    eind_datum = (datetime.date.today() + datetime.timedelta(days=500)).isoformat()
    
    url = "https://api.themoviedb.org/3/discover/tv"
    
    # 1. Internationale hit-series (zonder reality, soaps, talkshows)
    params_int = {
        'api_key': API_KEY,
        'language': 'nl-NL',
        'air_date.gte': vandaag,
        'air_date.lte': eind_datum,
        'sort_by': 'popularity.desc',
        'with_original_language': 'en|es|ko|de', 
        'without_genres': '10766,10764,10767', # Geen soaps, reality of talkshows
        'page': 1
    }
    
    # 2. Nederlandse series (inclusief reality, exclusief soaps/talkshows)
    params_nl = {
        'api_key': API_KEY,
        'language': 'nl-NL',
        'air_date.gte': vandaag,
        'air_date.lte': eind_datum,
        'sort_by': 'popularity.desc',
        'with_original_language': 'nl', 
        'without_genres': '10766,10767', # Reality is hier WEL toegestaan!
        'page': 1
    }
    
    print("Zoeken naar de grootste aankomende tv-series (inclusief NL reality)...")
    
    resp_int = requests.get(url, params=params_int)
    resp_nl = requests.get(url, params=params_nl)
    
    alle_ruwe_series = []
    
    if resp_int.status_code == 200:
        alle_ruwe_series.extend(resp_int.json().get('results', []))
    if resp_nl.status_code == 200:
        alle_ruwe_series.extend(resp_nl.json().get('results', []))
        
    # Sorteer de gecombineerde lijst op populariteit en pak de top 25
    gesorteerde_series = sorted(alle_ruwe_series, key=lambda x: x.get('popularity', 0), reverse=True)[:25]
    
    aankomende_series = []
    
    for serie in gesorteerde_series:
        serie_id = serie.get('id')
        serie_naam = serie.get('name')
        
        detail_url = f"https://api.themoviedb.org/3/tv/{serie_id}"
        detail_params = {'api_key': API_KEY, 'language': 'nl-NL'}
        detail_response = requests.get(detail_url, params=detail_params)
        
        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            next_ep = detail_data.get('next_episode_to_air')
            
            if next_ep and next_ep.get('air_date'):
                air_date = next_ep.get('air_date')
                seizoen = next_ep.get('season_number')
                
                aankomende_series.append({
                    'title': f"{serie_naam} (Seizoen {seizoen})",
                    'release_date': air_date,
                    'poster_path': serie.get('poster_path')
                })
                
    return aankomende_series

def verwerk_producties(producties, icoon, locatie_tekst):
    conn = sqlite3.connect('evenementen.db')
    cursor = conn.cursor()
    
    aantal_toegevoegd = 0
    aantal_geupdate = 0
    
    for prod in producties:
        naam = prod.get('title')
        release_date = prod.get('release_date')
        
        if not release_date or not naam:
            continue
            
        datum_iso = f"{release_date}T00:00:00"
        
        poster_path = prod.get('poster_path')
        afbeelding = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''
        
        zoek_term = naam.replace(" ", "+")
        trailer_url = f"https://www.youtube.com/results?search_query={zoek_term}+trailer+nl"
        
        cursor.execute('SELECT id FROM events WHERE naam = ? AND categorie = "film"', (naam,))
        bestaand = cursor.fetchone()
        
        if not bestaand:
            cursor.execute('''
                INSERT INTO events (
                    naam, categorie, icon, vlag, locatie, datum, url, afbeelding, 
                    presaleDatum, regio, urgencyStartDatum, urgencyLabel, urgencyIcon, 
                    affiliateUrl, affiliateTekst
                ) VALUES (?, 'film', ?, 'globe', ?, ?, ?, ?, 
                '', 'Wereldwijd', '', '', '', ?, 'Bekijk Trailer')
            ''', (naam, icoon, locatie_tekst, datum_iso, trailer_url, afbeelding, trailer_url))
            aantal_toegevoegd += 1
        else:
            cursor.execute('''
                UPDATE events 
                SET datum = ?, afbeelding = ?, url = ?, affiliateUrl = ?
                WHERE id = ?
            ''', (datum_iso, afbeelding, trailer_url, trailer_url, bestaand[0]))
            aantal_geupdate += 1
            
    conn.commit()
    conn.close()
    return aantal_toegevoegd, aantal_geupdate

if __name__ == "__main__":
    komende_films = haal_grote_films_op()
    if komende_films:
        nw, up = verwerk_producties(komende_films, 'fa-film', 'Bioscoop / Streaming')
        print(f"Grote films succesvol verwerkt: {nw} nieuw, {up} geüpdatet.\n")
        
    komende_series = haal_grote_series_op()
    if komende_series:
        nw, up = verwerk_producties(komende_series, 'fa-tv', 'Streamingdiensten')
        print(f"Grote series succesvol verwerkt: {nw} nieuw, {up} geüpdatet.")