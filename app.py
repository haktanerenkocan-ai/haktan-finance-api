import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# TEFAS'ın resmi API servis adresi
TEFAS_API_URL = "https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir"

def get_tefas_data():
    """
    TEFAS resmi API'sinden tüm aktif fonların anlık fiyat 
    ve getiri bilgilerini tek seferde çeker.
    """
    bugun = datetime.now().strftime("%Y-%m-%d")
    
    # TEFAS API'sinin beklediği zorunlu parametreler
    payload = {
        "islemDurum": "1",          # Aktif işlem gören fonlar
        "tarih": bugun,             # Güncel tarih
        "fonTipi": "YAT",           # Yatırım fonları (YAT / EMK / BYF)
        "fonturId": "",
        "baskaFonKodu": ""
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/"
    }
    
    try:
        # TEFAS sunucularına doğrudan güvenli bağlantı isteği atıyoruz
        res = requests.post(TEFAS_API_URL, data=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"TEFAS API Bağlantı Hatası: {str(e)}")
        return None
    return None

@app.route('/')
def home():
    return "Karargah Resmi TEFAS API Servisi Canlı!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0 for kod in kod_listesi}
    
    tefas_response = get_tefas_data()
    
    # TEFAS verisi geldiyse içinden bizim fonları ayıklıyoruz
    if tefas_response and isinstance(tefas_response, list):
        for fon in tefas_response:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    # Virgüllü gelebilecek fiyatı float sayıya çeviriyoruz
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
    
    tefas_response = get_tefas_data()
    
    if tefas_response and isinstance(tefas_response, list):
        for fon in tefas_response:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    # Günlük getiri oranını alıp Google Sheets formatına (%0.00) uyduruyoruz
                    degisim_str = str(fon.get("GUNLUKGETIRI", "0")).replace(",", ".")
                    sonuclar[fon_kodu] = float(degisim_str) / 100
                except:
                    sonuclar[fon_kodu] = 0.0
                    
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
