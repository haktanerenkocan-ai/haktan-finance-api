import requests
import os
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "TEFAS API Karargah Online!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "Kod eksik", 400
    
    # TEFAS'ın veri servis adresi
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryData"
    # Bugünün tarihini alıyoruz
    tarih = datetime.now().strftime("%d.%m.%Y")
    
    # TEFAS'ın beklediği teknik paket (Payload)
    payload = {
        "fontip": "YAT",
        "sfontip": "YAT",
        "fongrup": "",
        "fonkod": kod,
        "bastarih": tarih,
        "bittarih": tarih,
        "isin": ""
    }
    
    # Siteyi "bizden biri" olduğuna ikna eden başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod}"
    }

    try:
        # Doğrudan API'ye POST isteği atıyoruz
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get("data") and len(data["data"]) > 0:
                # Fiyatı al ve Excel'in anlayacağı nokta formatına çevir
                fiyat = data["data"][0]["FIYAT"]
                return str(fiyat).replace(",", ".")
            
        # Eğer veri gelmezse 0 dön
        return "0"
        
    except Exception:
        # Bağlantı koparsa veya bloklanırsak 0 dön
        return "0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
