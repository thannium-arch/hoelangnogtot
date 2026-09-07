import os
from datetime import datetime

BASE_URL = "https://hoelangnogtot.nl"
SITEMAP_FILE = "sitemap.xml"

def genereer_sitemap():
    # Zoek alle HTML bestanden in de huidige map
    html_bestanden = [f for f in os.listdir('.') if f.endswith('.html')]
    
    # XML opbouw starten
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    vandaag = datetime.now().strftime('%Y-%m-%d')
    
    for bestand in html_bestanden:
        # Bepaal de URL, prioriteit en frequentie
        if bestand == "index.html":
            url = f"{BASE_URL}/"
            prioriteit = "1.0"
            frequentie = "daily"
        else:
            url = f"{BASE_URL}/{bestand}"
            prioriteit = "0.8"
            frequentie = "weekly"
            
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url}</loc>\n'
        xml_content += f'    <lastmod>{vandaag}</lastmod>\n'
        xml_content += f'    <changefreq>{frequentie}</changefreq>\n'
        xml_content += f'    <priority>{prioriteit}</priority>\n'
        xml_content += '  </url>\n'
        
    xml_content += '</urlset>'
    
    # Sla het bestand op (dit overschrijft de oude sitemap)
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)
        
    print(f"Sitemap succesvol gegenereerd met {len(html_bestanden)} pagina's.")

if __name__ == "__main__":
    genereer_sitemap()
