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
        session = requests.Session()
        session.get(f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod}", headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        
        res = session.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            # ŞARAPNEL KALKANI: Gelen yanıt gerçekten JSON mu kontrol ediyoruz
            try:
                data = res.json()
                if data.get("data") and len(data["data"]) > 0:
                    fiyat = data["data"][0]["FIYAT"]
                    return str(fiyat).replace(",", ".")
                else:
                    return "HATA: TEFAS veri döndürmedi (Bu tarih aralığında bu fon için veri yok)."
            except Exception:
                # Kod JSON okurken patlarsa, TEFAS'ın yolladığı gizli HTML/Metin yanıtının ilk 200 karakterini yazdırıyoruz
                return f"HATA: TEFAS API yerine bir web sayfası (Güvenlik Kalkanı) döndürdü. Gelen yanıt: {res.text[:200]}..."
                
        elif res.status_code == 403:
             return "HATA 403: TEFAS erişimi reddetti. (Güvenlik Duvarı Engeli)"
             
        else:
            return f"HATA: TEFAS sunucusu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
        return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
