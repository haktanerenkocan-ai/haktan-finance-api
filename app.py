import os
from flask import Flask, request, jsonify
import cloudscraper

app = Flask(__name__)

def get_tefas_data():
    # Cloudscraper, TEFAS'ın bot korumasını aşmak için kendini gerçek bir Chrome gibi gösterir
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # Haktan'ın deşifre ettiği TEFAS JSON parametreleri
    payload = {
        "calismaTipi": 2,
        "dil": "TR",
        "fonTipi": "YAT",
        "islem": 1,
        "donemGetiri1a": "1",
        "donemGetiri1y": "1",
        "donemGetiri3a": "1",
        "donemGetiri3y": "1",
        "donemGetiri5y": "1",
        "donemGetiri6a": "1",
        "donemGetiriyb": "1",
        "fonGrubu": None,
        "fonTurAciklama": None,
        "fonTurKod": None,
        "kurucuKodu": None,
        "sfonTurKod": None,
        "basTarih": None,
        "bitTarih": None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/fon-getirileri"
    }

    try:
        # Önce anasayfaya gidip giriş biletimizi (Cookie) alıyoruz
        scraper.get("https://www.tefas.gov.tr/fon-getirileri", timeout=10)
        
        # Sonra senin bulduğun o büyük veritabanı uç noktasına JSON yükümüzü ateşliyoruz
        res = scraper.post("https://www.tefas.gov.tr/api/funds/fonGetiriBaziBilgiGetir", json=payload, headers=headers, timeout=15)
        
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("Cloudscraper Engeli:", str(e))
        
    return None

@app.route('/')
def home():
    return "Karargah Cloudscraper Modülü Çevrimiçi!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0 for kod in kod_listesi}
    
    veri = get_tefas_data()
    if veri and isinstance(veri, list):
        for fon in veri:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    fiyat_str = str(fon.get("FIYAT", "0")).replace(",", ".")
                    sonuclar[fon_kodu] = float(fiyat_str)
                except:
                    sonuclar[fon_kodu] = 0
                    
    return jsonify(sonuclar)

@app.route('/toplu_degisim')
def get_toplu_degisim():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0.0 for kod in kod_listesi}
    
    veri = get_tefas_data()
    if veri and isinstance(veri, list):
        for fon in veri:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    degisim_str = str(fon.get("GUNLUKGETIRI", fon.get("GETIRI1G", "0"))).replace(",", ".")
                    sonuclar[fon_kodu] = float(degisim_str) / 100
                except:
                    sonuclar[fon_kodu] = 0.0
                    
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
