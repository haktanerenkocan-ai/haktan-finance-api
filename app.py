import os
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Karargah Online - FVT Ana Veri Damarı (API) Devrede!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    # DİKKAT: Senin kopyaladığın o uzun linki buraya yapıştırıyoruz!
    # Linkin içindeki "PHE" yazan kısmı silip yerine {kod} yazıyoruz ki tüm fonları arayabilelim.
    # Örnek: "https://fvt.com.tr/api/fon/prices?fund={kod}&baslangic=2026-03-13..."
    # (Linkin orijinal halini bozmadan sadece fon adını değiştir).
    url = f"https://fvt.com.tr/api/funds/PHE/prices?baslangic=2026-03-13&bitis=2026-04-13"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    try:
        # Doğrudan API'yi vuruyoruz
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            veri = res.json()
            
            # Veri paketinin içi dolu mu kontrol et
            if veri.get("success") and veri.get("data") and len(veri["data"]) > 0:
                
                # İŞTE SIR BURADA: [-1] diyerek listenin en sonundaki, yani bugünkü güncel fiyatı alıyoruz!
                fiyat = veri["data"][-1]["fiyat"] 
                
                return str(fiyat).replace(",", ".")
            else:
                return f"HATA: {kod} fonu için veri paketi geldi ama içi boş."
                
        elif res.status_code == 403:
            return "HATA 403: FVT API kalkanı isteği reddetti!"
        else:
            return f"HATA: Sunucu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
         return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
