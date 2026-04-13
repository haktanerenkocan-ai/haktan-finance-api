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
    if not kod: return "Kod eksik", 400
    
    try:
        url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod.upper()}"
        # Tarayıcı taklidini daha da güçlendirelim
        response = scraper.get(url, timeout=15)
        
        # TANI 1: Eğer site bizi blokladıysa durum kodunu görelim
        if response.status_code != 200:
            return f"Hata: Site kapıyı kapattı (Durum Kodu: {response.status_code})"

        # TANI 2: Sayfanın içinde fiyat etiketi var mı bakalım
        match = re.search(r'MainContent_MainContent_LabelLastPrice">([0-9,.]+)<', response.text)
        
        if match:
            fiyat = match.group(1).replace(".", "").replace(",", ".")
            return fiyat
        else:
            # Eğer fiyat bulunamadıysa sayfanın ilk 100 karakterini görelim (Blok sayfası mı?)
            return f"Hata: Fiyat etiketi bulunamadı. Sayfa içeriği: {response.text[:100]}"
            
    except Exception as e:
        return f"Sistem Hatası: {str(e)}"
