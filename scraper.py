import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

def get_zabka_promos():
    promos = []
    
    # 1. Statyczne promki które są zawsze w Żappce - aktualizuj ręcznie daty
    promos.extend([
        {
            "nazwa": "Pinsa za 1 żappsa",
            "opis": "Pinsa Pesto lub Salsiccia za 1 punkt w Żappce",
            "waznosc": "09.06.2026",
            "zrodlo": "Żappka",
            "status": "ok"
        },
        {
            "nazwa": "Menu Gift Card +40%",
            "opis": "Doładuj kartę Żabka Menu min. 50zł, dostajesz +40% salda",
            "waznosc": "23.06.2026",
            "zrodlo": "zabka.pl",
            "status": "ok"
        }
    ])
    
    # 2. Scrapowanie gazetki Żabki
    try:
        headers = {'User-Agent': 'Mozilla/5.0 GitHub Action Bot'}
        url = 'https://www.zabka.pl/gazetki-promocyjne'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Szukaj banerów z datami ważności
        for banner in soup.select('.promo-banner, .gazetka-item'):
            text = banner.get_text()
            # Wyciągnij "Drugi produkt za 1zł"
            if 'drugi' in text.lower() and '1 zł' in text.lower():
                promos.append({
                    "nazwa": "Drugi produkt za 1zł",
                    "opis": "Automatycznie przy kasie na oznaczonych produktach",
                    "waznosc": "Do odwołania",
                    "zrodlo": "gazetka",
                    "status": "ok"
                })
            # Wyciągnij "Hot Ceny" z datą
            match = re.search(r'Hot Ceny.*?(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                promos.append({
                    "nazwa": "Hot Ceny -25%",
                    "opis": "Kupon w Żappce na wybrane produkty",
                    "waznosc": match.group(1).replace('.','-'),
                    "zrodlo": "Żappka",
                    "status": "ok"
                })
    except Exception as e:
        print(f"Błąd scrapowania gazetki: {e}")
    
    # 3. Usuń duplikaty po nazwie
    seen = set()
    unique_promos = []
    for p in promos:
        if p['nazwa'] not in seen:
            seen.add(p['nazwa'])
            unique_promos.append(p)
    
    return unique_promos

if __name__ == "__main__":
    promos = get_zabka_promos()
    
    # Dodaj timestamp aktualizacji
    output = {
        "last_update": datetime.now().isoformat(),
        "promos": promos
    }
    
    with open('promos.json', 'w', encoding='utf-8') as f:
        json.dump(promos, f, ensure_ascii=False, indent=2)
    
    print(f"Zapisano {len(promos)} promocji do promos.json")