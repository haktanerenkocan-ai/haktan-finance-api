import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def get_fvt_data(kod):
    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=10)).strftime("%Y-%m-%d")
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
    return "Karargah API Online - Toplu Islem Modu Aktif!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    kod_listesi = kodlar_str.split(',')
    sonuclar = {}
    for kod in kod_listesi:
        veri = get_fvt_data(kod.strip())
        if veri and veri.get("success") and len(veri["data"]) > 0:
            sonuclar[kod] = float(veri["data"][-1]["fiyat"])
        else:
            sonuclar[kod] = 0
    return jsonify(sonuclar)

@app.route('/toplu_degisim')
def get_toplu_degisim():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    kod_listesi = kodlar_str.split(',')
    sonuclar = {}
    for kod in kod_listesi:
        veri = get_fvt_data(kod.strip())
        if veri and veri.get("success") and len(veri["data"]) > 0:
            # Getiri orani doğrudan sayı olarak gider (0.0032 gibi)
            getiri = float(veri["data"][-1]["getiri"]) / 100
            sonuclar[kod] = getiri
        else:
            sonuclar[kod] = 0
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
