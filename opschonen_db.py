import sqlite3

# Maak verbinding met je database
conn = sqlite3.connect('evenementen.db')
cursor = conn.cursor()

try:
    # Vervang 'www.hoelangnogtot.nl' door 'hoelangnogtot.nl' in de kolom waar je de URL bewaart.
    # Let op: Vervang 'url' door de daadwerkelijke kolomnaam uit jouw tabel als deze anders heet.
    cursor.execute("""
        UPDATE events 
        SET url = REPLACE(url, 'https://www.hoelangnogtot.nl', 'https://hoelangnogtot.nl') 
        WHERE url LIKE '%www.hoelangnogtot.nl%';
    """)
    conn.commit()
    print("Database succesvol opgeschoond: 'www.' is overal verwijderd.")
except sqlite3.Error as e:
    print(f"Er ging iets mis: {e}")
finally:
    conn.close()
