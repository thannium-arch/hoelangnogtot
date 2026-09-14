import json
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

evenement_naam = os.environ.get("EVENEMENT_NAAM")
if not evenement_naam:
    print("Geen evenement opgegeven.")
    sys.exit(1)

# Laad de database
with open("evenementen.json", "r", encoding="utf-8") as f:
    evenementen = json.load(f)

# Zoek het evenement
ev = next((e for e in evenementen if evenement_naam.lower() in e["naam"].lower()), None)
if not ev:
    print(f"Evenement '{evenement_naam}' niet gevonden in evenementen.json")
    sys.exit(1)

# Bepaal categorie, afbeelding en naam
cat = ev.get("categorie", "feestdag")
afbeelding = ev.get("afbeelding", "https://images.unsplash.com/photo-1499591934245-40b55745b905?w=400&q=80")
naam = ev.get("naam", "Evenement")
datum_str = ev.get("datum", "2027-01-01")

# Bereken de dagen en maak de datum leesbaar
try:
    ev_datum = datetime.strptime(datum_str, "%Y-%m-%d")
    nu = datetime.now()
    verschil_dagen = (ev_datum - nu).days
    
    if verschil_dagen > 0:
        countdown_tekst = f"Nog {verschil_dagen} dagen"
    elif verschil_dagen == 0:
        countdown_tekst = "Vandaag is het zover!"
    else:
        countdown_tekst = "Evenement is afgelopen"

    maanden = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
    leesbare_datum = f"{ev_datum.day} {maanden[ev_datum.month - 1]} {ev_datum.year}"
except:
    countdown_tekst = "Datum onbekend"
    leesbare_datum = datum_str

# Maak de HTML pagina met jouw exacte website styling, inclusief de klok
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: transparent; padding: 20px; display: flex; justify-content: center; }}
        .card {{ background: white; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; width: 400px; border-top: 5px solid #3498db; }}
        
        .card.feestdag {{ border-top-color: #e74c3c; }}
        .card.cultuur {{ border-top-color: #9b59b6; }}
        .card.festival {{ border-top-color: #fd79a8; }}
        .card.sport {{ border-top-color: #3498db; }}
        .card.film {{ border-top-color: #f1c40f; }}
        .card.gaming {{ border-top-color: #2ecc71; }}
        .card.concert {{ border-top-color: #e67e22; }}
        
        .card-image-container {{ width: 100%; height: 220px; background-color: #f8fafc; border-bottom: 1px solid #f1f5f9; }}
        .card-image-container img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; display: block; }}
        .card-content {{ padding: 20px; }}
        
        .category-tag {{ display: inline-block; font-size: 0.7em; text-transform: uppercase; letter-spacing: 1px; padding: 4px 10px; border-radius: 12px; font-weight: bold; margin-bottom: 10px; color: white; }}
        .tag-feestdag {{ background-color: #e74c3c; }}
        .tag-cultuur {{ background-color: #9b59b6; }}
        .tag-festival {{ background-color: #fd79a8; }}
        .tag-sport {{ background-color: #3498db; }}
        .tag-film {{ background-color: #f1c40f; color: #333; }}
        .tag-gaming {{ background-color: #2ecc71; }}
        .tag-concert {{ background-color: #e67e22; }}
        
        h3 {{ margin: 0 0 15px 0; font-size: 1.6em; color: #1e293b; }}
        
        .event-date {{ font-size: 0.95em; color: #64748b; margin-bottom: 15px; display: flex; align-items: center; gap: 6px; font-weight: 500; }}
        
        .countdown {{ font-size: 1.3em; font-weight: bold; padding: 15px; border-radius: 8px; margin-bottom: 15px; text-align: center; }}
        .cd-feestdag {{ color: #e74c3c; background: #fef2f2; }}
        .cd-cultuur {{ color: #9b59b6; background: #f9f2fd; }}
        .cd-festival {{ color: #fd79a8; background: #fff0f5; }}
        .cd-sport {{ color: #3498db; background: #f0f8ff; }}
        .cd-film {{ color: #f39c12; background: #fcf3cf; }}
        .cd-gaming {{ color: #27ae60; background: #eafaf1; }}
        .cd-concert {{ color: #d35400; background: #fdf2e9; }}

        .watermerk {{ margin-top: 15px; font-size: 0.8em; color: #94a3b8; font-weight: bold; text-align: center; }}
    </style>
</head>
<body>
    <div class="card {cat}" id="reddit-card">
        <div class="card-image-container">
            <img src="{afbeelding}">
        </div>
        <div class="card-content">
            <span class="category-tag tag-{cat}">{cat}</span>
            <h3>{naam}</h3>
            <div class="event-date"><i class="fa-regular fa-calendar"></i> {leesbare_datum}</div>
            <div class="countdown cd-{cat}">{countdown_tekst}</div>
            <div class="watermerk">HOELANGNOGTOT.NL</div>
        </div>
    </div>
</body>
</html>
"""

# Maak een screenshot met Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 600, "height": 700})
    page.set_content(html_content)
    
    card_element = page.locator("#reddit-card")
    card_element.screenshot(path="reddit_kaart.png", omit_background=True)
    
    browser.close()
    print("Afbeelding succesvol gegenereerd: reddit_kaart.png")
