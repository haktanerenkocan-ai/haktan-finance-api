import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "Karargah Online - Google Tablolar Uyumlu Veri Hattı!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    # Tarihleri her gün güncel tutmak için otomatik hesaplıyoruz
    bugun = datetime.now()
    otuz_gun_once = bugun - timedelta(days=30)
    
    bitis_tarihi = bugun.strftime("%Y-%m-%d")
    baslangic_tarihi = otuz_gun_once.strftime("%Y-%m-%d")
    
    # Senin bulduğun o altın değerindeki link:
    url = f"https://fvt.com.tr/api/funds/{kod}/prices?baslangic={baslangic_tarihi}&bitis={bitis_tarihi}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://fvt.com.tr/"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            veri = res.json()
            
            if veri.get("success") and veri.get("data") and len(veri["data"]) > 0:
                # En güncel fiyatı çekiyoruz
                fiyat = veri["data"][-1]["fiyat"] 
                
                # KRİTİK HAMLE: Noktayı virgüle çeviriyoruz ki Google Tablolar (Türkçe) rakamı doğru anlasın.
                return str(fiyat).replace(".", ",")
            else:
                return "0"
                
        return "0"
            
    except Exception:
         return "0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
