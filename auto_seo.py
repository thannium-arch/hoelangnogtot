import os
import re

def voeg_seo_toe():
    # Zoek alle HTML bestanden
    html_bestanden = [f for f in os.listdir('.') if f.endswith('.html')]

    for bestand in html_bestanden:
        with open(bestand, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check of SEO tags al aanwezig zijn om dubbelingen te voorkomen
        if 'name="description"' in content and 'property="og:title"' in content:
            continue

        # Haal de huidige titel van de pagina op
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        titel = title_match.group(1) if title_match else "Aftellen tot je favoriete evenement"
        
        # Maak de titel schoon voor WhatsApp en Facebook
        schone_titel = titel.replace(" | hoelangnogtot.nl", "").strip()
        beschrijving = f"Tel live af naar {schone_titel}. Bekijk direct hoeveel dagen, uren en minuten het nog duurt en bereid je voor!"

        seo_tags = f"""
    <!-- Automatisch Toegevoegde SEO Tags -->
    <meta name="description" content="{beschrijving}">
    <meta property="og:title" content="{schone_titel}">
    <meta property="og:description" content="{beschrijving}">
    <meta property="og:url" content="https://hoelangnogtot.nl/{bestand}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://hoelangnogtot.nl/images/standaard-preview.jpg">"""

        # Injecteer de tags vlak voor de </head> tag
        content = re.sub(r'(</head>)', rf'{seo_tags}\n\1', content, flags=re.IGNORECASE)

        with open(bestand, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"SEO tags automatisch toegevoegd aan {bestand}")

if __name__ == "__main__":
    voeg_seo_toe()
