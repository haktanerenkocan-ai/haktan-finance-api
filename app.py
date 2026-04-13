import cloudscraper
import re
import os
from flask import Flask, request

app = Flask(__name__)
# TLS parmak izini taklit eden motor
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod')
    if not kod:
        return "Kod eksik", 400
    
    try:
        url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod.upper()}"
        response = scraper.get(url, timeout=15)
        
        if response.status_code == 200:
            match = re.search(r'MainContent_MainContent_LabelLastPrice">([0-9,.]+)<', response.text)
            if match:
                fiyat = match.group(1).replace(".", "").replace(",", ".")
                return fiyat
        return "0"
    except Exception:
        return "0"

if __name__ == "__main__":
    # Render'ın verdiği portu otomatik yakalar
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
