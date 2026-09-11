import os

BESTAND = 'wensenlijst.txt'

def verwerk_lijst():
    if not os.path.exists(BESTAND):
        print("Geen wensenlijst gevonden.")
        return

    with open(BESTAND, 'r', encoding='utf-8') as f:
        regels = f.readlines()

    if not regels:
        print("Wensenlijst is leeg.")
        return

    nieuwe_items_toegevoegd = False

    for regel in regels:
        regel = regel.strip()
        if not regel or ':' not in regel:
            continue

        categorie, zoekterm = regel.split(':', 1)
        categorie = categorie.strip().lower()
        zoekterm = zoekterm.strip()

        print(f"Zoeken naar {categorie}: {zoekterm}")

        # Hier sturen we de zoekterm naar jouw bestaande logica
        if categorie == 'film':
            # Voeg hier de aanroep naar je TMDB script toe voor deze specifieke zoekterm
            print(f"TMDB API wordt aangeroepen voor {zoekterm}")
            nieuwe_items_toegevoegd = True
            
        elif categorie == 'game':
            # Voeg hier de aanroep naar je IGDB script toe voor deze specifieke zoekterm
            print(f"IGDB API wordt aangeroepen voor {zoekterm}")
            nieuwe_items_toegevoegd = True
            
        elif categorie == 'concert':
            # Voeg hier de aanroep naar je Ticketmaster script toe voor deze specifieke zoekterm
            print(f"Ticketmaster API wordt aangeroepen voor {zoekterm}")
            nieuwe_items_toegevoegd = True

    # Leeg het bestand na succesvolle verwerking zodat we morgen niet dubbel zoeken
    if nieuwe_items_toegevoegd:
        with open(BESTAND, 'w', encoding='utf-8') as f:
            f.write("")
        print("Wensenlijst succesvol verwerkt en geleegd.")

if __name__ == "__main__":
    verwerk_lijst()
