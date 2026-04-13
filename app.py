import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

# --- FİYAT HATTI ---
@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "0"
    
    # Bugünün ve 30 gün öncesinin tarihini otomatik alıyoruz
    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=30)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    
    url = f"https://fvt.com.tr/api/funds/{kod}/prices?baslangic={baslangic}&bitis={bitis}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            veri = res.json()
            if veri.get("success") and len(veri["data"]) > 0:
                # En güncel (son) fiyatı al ve tırnakla paketle
                fiyat = veri["data"][-1]["fiyat"]
                return f'"{str(fiyat).replace(".", ",")}"'
        return "0"
    except: return "0"

# --- GÜNLÜK DEĞİŞİM HATTI ---
@app.route('/degisim')
def get_degisim():
    kod = request.args.get('kod', '').upper()
    if not kod: return "0"
    
    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=30)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    
    url = f"https://fvt.com.tr/api/funds/{kod}/prices?baslangic={baslangic}&bitis={bitis}"

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200:
            veri = res.json()
            if veri.get("success") and len(veri["data"]) > 0:
                # Listenin sonundaki "getiri" değerini al
                degisim = veri["data"][-1]["getiri"]
                return f'"{str(degisim).replace(".", ",")}"'
        return "0"
    except: return "0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
