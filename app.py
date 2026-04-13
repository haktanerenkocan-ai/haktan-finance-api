import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "Karargah Online - FVT Canlı Veri Hattı Aktif!"

@app.route('/fiyat')
def get_fiyat():
    # Kullanıcının gönderdiği fon kodunu al (Örn: TLY, PHE, MAC)
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    # TARİH AYARI: Linkin bayatlamaması için tarihleri otomatik hesaplıyoruz
    bugun = datetime.now()
    otuz_gun_once = bugun - timedelta(days=30)
    
    bitis_tarihi = bugun.strftime("%Y-%m-%d")
    baslangic_tarihi = otuz_gun_once.strftime("%Y-%m-%d")
    
    # Senin bulduğun linki "Dinamik" hale getirdik:
    # {kod} kısmına PHE, TLY vb. gelecek. Tarihler de her gün güncellenecek.
    url = f"https://fvt.com.tr/api/funds/{kod}/prices?baslangic={baslangic_tarihi}&bitis={bitis_tarihi}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://fvt.com.tr/"
    }

    try:
        # Doğrudan FVT'nin veri damarına (API) bağlanıyoruz
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            veri = res.json()
            
            # JSON paketinin içinde veri var mı kontrol et
            if veri.get("success") and veri.get("data") and len(veri["data"]) > 0:
                
                # [-1] komutu listenin EN SONUNDAKİ (yani en güncel) fiyatı alır
                fiyat = veri["data"][-1]["fiyat"] 
                
                # Excel/Google Tablolar için virgülü noktaya çevirip metin olarak dönüyoruz
                return str(fiyat).replace(",", ".")
            else:
                return f"HATA: {kod} fonu için veri paketi boş geldi. Kodun doğruluğunu kontrol et."
                
        elif res.status_code == 403:
            return "HATA 403: FVT API erişimi reddetti! (IP Engeli olabilir)"
        else:
            return f"HATA: FVT sunucusu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
         return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    # Render veya VDS portunu ayarla
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
