import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

def get_fvt_data(kod):
    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=30)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    url = f"https://fvt.com.tr/api/funds/{kod}/prices?baslangic={baslangic}&bitis={bitis}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None

@app.route('/')
def home():
    return "Karargah API Online - Matematiksel Düzeltme Hattı!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "0"
    veri = get_fvt_data(kod)
    if veri and veri.get("success") and len(veri["data"]) > 0:
        fiyat = veri["data"][-1]["fiyat"]
        return f'"{str(fiyat).replace(".", ",")}"'
    return "0"

@app.route('/degisim')
def get_degisim():
    kod = request.args.get('kod', '').upper()
    if not kod: return "0"
    veri = get_fvt_data(kod)
    if veri and veri.get("success") and len(veri["data"]) > 0:
        # KRİTİK DÜZELTME: Gelen 0.328 değerini 100'e bölerek 0.00328 yapıyoruz
        getiri = float(veri["data"][-1]["getiri"]) / 100
        # Google Tablolar'ın anlaması için virgüle çevirip tırnaklıyoruz
        return f'"{str(getiri).replace(".", ",")}"'
    return "0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
