import cloudscraper
import re
import os
from flask import Flask, request

app = Flask(__name__)
# FVT'yi kandırmak için en güncel tarayıcı taklidi
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

@app.route('/')
def home():
    return "FVT API Online!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "Kod eksik", 400
    
    try:
        # Doğrudan FVT'nin fon detay sayfasına sızıyoruz
        url = f"https://fvt.com.tr/fonlar/{kod}"
        resp = scraper.get(url, timeout=15)
        
        if resp.status_code == 200:
            html = resp.text
            # FVT veriyi 'lastPrice' adında bir değişkenin içine gizler. 
            # Onu şu regex ile yakalıyoruz:
            match = re.search(r'"lastPrice":\s*([0-9.]+)', html)
            
            if match:
                fiyat = match.group(1)
                return fiyat
            
            # Eğer yukarıdaki olmazsa, klasik yöntemle ara:
            match_alt = re.search(r'₺([0-9.,]+)', html)
            if match_alt:
                fiyat = match_alt.group(1).replace(".", "").replace(",", ".")
                return fiyat

        return "0"
    except:
        return "0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
