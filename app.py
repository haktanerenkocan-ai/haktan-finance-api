import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import cloudscraper

app = Flask(__name__)

def get_fvt_data(kod):
    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=10)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    url = f"https://fvt.com.tr/api/funds/{kod}/prices?baslangic={baslangic}&bitis={bitis}"
    
    # Cloudscraper ile kendimizi gerçek bir Chrome tarayıcısı gibi gösteriyoruz
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # FVT'yi ikna edecek ekstra insan başlıkları
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://fvt.com.tr",
        "Referer": f"https://fvt.com.tr/fonlar/yatirim-fonlari/{kod}"
    }
    
    try:
        # FVT sunucularına hayalet isteğimizi atıyoruz
        res = scraper.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"FVT Engeli veya Hatası: {res.status_code} - {kod}")
    except Exception as e:
        print(f"Bağlantı Hatası ({kod}): {str(e)}")
        
    return None

@app.route('/')
def home():
    return "Karargah FVT (Cloudscraper) Modülü Çevrimiçi!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0 for kod in kod_listesi}
    
    for kod in kod_listesi:
        veri = get_fvt_data(kod)
        if veri and veri.get("success") and len(veri["data"]) > 0:
            sonuclar[kod] = float(veri["data"][-1]["fiyat"])
            
    return jsonify(sonuclar)

@app.route('/toplu_degisim')
def get_toplu_degisim():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0.0 for kod in kod_listesi}
    
    for kod in kod_listesi:
        veri = get_fvt_data(kod)
        if veri and veri.get("success") and len(veri["data"]) > 0:
            getiri = float(veri["data"][-1]["getiri"]) / 100
            sonuclar[kod] = getiri
            
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
