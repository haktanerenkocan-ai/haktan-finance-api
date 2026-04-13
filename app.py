import requests
import os
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "TEFAS API Karargah Online!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryData"
    
    # Tatil/Hafta sonu boşluğuna düşmemek için sadece bugünü değil, son 7 günü tarıyoruz
    bitis_tarihi = datetime.now()
    baslangic_tarihi = bitis_tarihi - timedelta(days=7)
    
    payload = {
        "fontip": "YAT",
        "sfontip": "YAT",
        "fongrup": "",
        "fonkod": kod,
        "bastarih": baslangic_tarihi.strftime("%d.%m.%Y"),
        "bittarih": bitis_tarihi.strftime("%d.%m.%Y"),
        "isin": ""
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod}",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    try:
        # Oturum başlatıyoruz
        session = requests.Session()
        
        # 1. ADIM: Güvenlik çerezlerini (cookie) almak için fonun sayfasına normal bir giriş yapıyoruz
        session.get(f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod}", headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        
        # 2. ADIM: Çerezlerle birlikte arka kapıdan (API) veriyi çekiyoruz
        res = session.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get("data") and len(data["data"]) > 0:
                # Veriler tarihe göre sıralı gelir, 0. indeks en güncel fiyattır
                fiyat = data["data"][0]["FIYAT"]
                return str(fiyat).replace(",", ".")
            else:
                return "HATA: TEFAS veri döndürmedi (Bu tarih aralığında bu fon için veri yok)."
        
        elif res.status_code == 403:
             return "HATA 403: TEFAS erişimi reddetti. (Güvenlik Duvarı Engeli)"
             
        else:
            return f"HATA: TEFAS sunucusu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
        return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    # Render'ın atadığı portu dinamik olarak yakalar, lokalde çalıştırırsan 5000 kullanır
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
