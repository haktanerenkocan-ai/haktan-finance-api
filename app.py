import os
import requests
from flask import Flask, request, jsonify # jsonify eklendi
from datetime import datetime, timedelta

app = Flask(__name__)

def get_fvt_data(kod):
    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=10)).strftime("%Y-%m-%d") # 30 gün yerine 10 gün yeterli, hız artar
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
    return "Karargah API Online - Toplu İşlem Modu Aktif!"

# --- MEVCUT TEKLİ ROTALAR (ESKİ SİSTEM BOZULMASIN DİYE DURSUN) ---
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
        getiri = float(veri["data"][-1]["getiri"]) / 100
        return f'"{str(getiri).replace(".", ",")}"'
    return "0"

# --- YENİ TOPLU ROTALAR (BULK SİSTEMİ) ---

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = kodlar_str.split(',')
    sonuclar = {}
    
    for kod in kod_listesi:
        veri = get_fvt_data(kod.strip())
        if veri and veri.get("success") and len(veri["data"]) > 0:
            sonuclar[kod] = veri["data"][-1]["fiyat"]
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
            getiri = float(veri["data"][-1]["getiri"]) / 100
            sonuclar[kod] = getiri
        else:
            sonuclar[kod] = 0
            
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
