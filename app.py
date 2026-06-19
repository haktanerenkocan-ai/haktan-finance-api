import os
from flask import Flask, request, jsonify
from curl_cffi import requests
from fake_useragent import UserAgent

app = Flask(__name__)
ua = UserAgent()

def get_tefas_data():
    # Cloudflare'i kör eden asıl uç nokta
    url = "https://www.tefas.gov.tr/api/funds/fonGetiriBazliBilgiGetir"
    
    # Haktan'ın deşifre ettiği kusursuz TEFAS parametreleri
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

    # Her istekte farklı bir tarayıcı gibi davranıyoruz
    headers = {
        "User-Agent": ua.chrome,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/fon-getirileri"
    }

    try:
        # impersonate="chrome110" komutu, Render sunucusunun kimliğini gerçek bir Chrome'a dönüştürür.
        res = requests.post(url, json=payload, headers=headers, impersonate="chrome110", timeout=15)
        
        if res.status_code == 200:
            return res.json()
        else:
            print(f"TEFAS Engeli: {res.status_code}")
    except Exception as e:
        print("Bypass Hatası:", str(e))
        
    return None

@app.route('/')
def home():
    return "Karargah V4.3 Ultimate Bypass Modülü Aktif!"

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
