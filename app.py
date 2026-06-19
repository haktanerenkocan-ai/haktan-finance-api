import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

TEFAS_API_URL = "https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir"

def get_tefas_data():
    """
    TEFAS resmi API'sinden veri çeker. 
    Eğer bugün için veri yoksa (hafta sonu/akşam saatleri), 
    en son geçerli güne kadar geriye doğru tarar.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Bugün dahil son 5 günü kontrol et (Hafta sonları ve tatiller için koruma)
    for i in range(5):
        hedef_tarih = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        payload = {
            "islemDurum": "1",
            "tarih": hedef_tarih,
            "fonTipi": "YAT",
            "fonturId": "",
            "baskaFonKodu": ""
        }
        
        try:
            # Hem data (Form-URLencoded) hem json olarak TEFAS'ın esnekliğine uyması için gönderiyoruz
            res = requests.post(TEFAS_API_URL, data=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                veri = res.json()
                # Eğer gelen liste boş değilse, geçerli veriyi bulduk demektir!
                if veri and isinstance(veri, list) and len(veri) > 0:
                    print(f"✅ TEFAS Verisi Başarıyla Çekildi. Kullanılan Tarih: {hedef_tarih}")
                    return veri
        except Exception as e:
            print(f"⚠️ {hedef_tarih} tarihi denenirken hata oluştu: {str(e)}")
            continue
            
    return None

@app.route('/')
def home():
    return "Karargah Akıllı TEFAS API Servisi Canlı!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0 for kod in kod_listesi}
    
    tefas_response = get_tefas_data()
    
    if tefas_response:
        for fon in tefas_response:
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
    
    tefas_response = get_tefas_data()
    
    if tefas_response:
        for fon in tefas_response:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    degisim_str = str(fon.get("GUNLUKGETIRI", "0")).replace(",", ".")
                    sonuclar[fon_kodu] = float(degisim_str) / 100
                except:
                    sonuclar[fon_kodu] = 0.0
                    
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
