import requests
import os
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "TEFAS API Karargah Online ve Pusuda!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "Kod eksik", 400
    
    # TEFAS'ın doğrudan veri damarı
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryData"
    tarih = datetime.now().strftime("%d.%m.%Y")
    
    # Sistemin beklediği paket
    payload = {
        "fontip": "YAT",
        "sfontip": "YAT",
        "fongrup": "",
        "fonkod": kod,
        "bastarih": tarih,
        "bittarih": tarih,
        "isin": ""
    }
    
    # TEFAS'ı "Gerçek bir insan" olduğumuza ikna eden Ağır Zırh
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod}"
    }

    try:
        # Kapıyı çalıyoruz
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            # İçeride veri varsa al ve Excel için noktaya çevir
            if data.get("data") and len(data["data"]) > 0:
                fiyat = data["data"][0]["FIYAT"]
                return str(fiyat).replace(",", ".")
                
        # Kapı duvar olursa sessizce 0 dön
        return "0"
        
    except Exception:
        # Bağlantı koparsa sessizce 0 dön
        return "0"

if __name__ == "__main__":
    # Render'ın verdiği portu otomatik yakala
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
