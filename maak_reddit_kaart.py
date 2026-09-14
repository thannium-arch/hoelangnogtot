import json
import os
import sys
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

# Bepaal categorie styling
cat = ev.get("categorie", "feestdag")
afbeelding = ev.get("afbeelding", "https://images.unsplash.com/photo-1499591934245-40b55745b905?w=400&q=80")
naam = ev.get("naam", "Evenement")

# Maak de HTML pagina met jouw exacte website styling
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
        .card.sport {{ border-top-color: #3498db; }}
        .card-image-container {{ width: 100%; height: 220px; background-color: #f8fafc; border-bottom: 1px solid #f1f5f9; }}
        .card-image-container img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; display: block; }}
        .card-content {{ padding: 20px; }}
        .category-tag {{ display: inline-block; font-size: 0.7em; text-transform: uppercase; letter-spacing: 1px; padding: 4px 10px; border-radius: 12px; font-weight: bold; margin-bottom: 10px; background: #3498db; color: white; }}
        .tag-feestdag {{ background-color: #e74c3c; }}
        .tag-cultuur {{ background-color: #9b59b6; }}
        h3 {{ margin: 0 0 15px 0; font-size: 1.6em; color: #1e293b; }}
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
            <div class="watermerk">HOELANGNOGTOT.NL</div>
        </div>
    </div>
</body>
</html>
"""

# Maak een screenshot met Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 600, "height": 600})
    page.set_content(html_content)
    
    # Selecteer specifiek de kaart en maak een foto met transparante achtergrond
    card_element = page.locator("#reddit-card")
    card_element.screenshot(path="reddit_kaart.png", omit_background=True)
    
    browser.close()
    print("Afbeelding succesvol gegenereerd: reddit_kaart.png")
