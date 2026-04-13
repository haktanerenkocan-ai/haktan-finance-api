import cloudscraper
import re
from flask import Flask, request

app = Flask(__name__)
# TLS parmak izini taklit eden süper motor
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod')
    if not kod:
        return "Kod eksik", 400
    
    try:
        # Doğrudan TEFAS'ın kalbine gidiyoruz
        url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod.upper()}"
        
        # Siteye "Ben Rize'den giren normal bir kullanıcıyım" diyoruz
        response = scraper.get(url, timeout=15)
        
        if response.status_code == 200:
            # HTML içinden fiyatı cımbızla (Regex) çekiyoruz
            match = re.search(r'MainContent_MainContent_LabelLastPrice">([0-9,.]+)<', response.text)
            if match:
                # 1.234,56 -> 1234.56 çevrimi
                fiyat = match.group(1).replace(".", "").replace(",", ".")
                return fiyat
        
        return "0"
    except Exception as e:
        return "0"

if __name__ == "__main__":
    app.run()
