import os
import re
import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "FVT API Karargah Online - 3. Cephe!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    # 3. Cephe: FVT Fon Detay Sayfası
    url = f"https://fvt.com.tr/fonlar/yatirim-fonlari/{kod}"
    
    try:
        # Yine gerçek bir tarayıcı (Chrome) kılığında sızıyoruz
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        res = scraper.get(url, timeout=15)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            sayfa_metni = soup.get_text()
            
            # RADAR SİSTEMİ: Sayfadaki "₺2,768049" formatındaki metinleri arıyoruz
            # ₺ işaretinden sonra boşluk olsa da olmasa da rakamları ve virgülleri yakalar
            eslesme = re.search(r'₺\s*(\d+[.,]\d+)', sayfa_metni)
            
            if eslesme:
                fiyat = eslesme.group(1) # Sadece rakam kısmını al (Örn: 2,768049)
                return fiyat.replace(",", ".") # Sistemlerin okuyabilmesi için virgülü noktaya çevir
            else:
                return f"HATA: {kod} sayfası açıldı ama ₺ formatında bir fiyat sayfada bulunamadı."
                
        elif res.status_code == 403:
            return "HATA 403: FVT kalkanları da Render IP'sini tespit edip engelledi!"
            
        elif res.status_code == 404:
            return f"HATA 404: FVT'de {kod} adında bir fon bulunamadı."
            
        else:
            return f"HATA: FVT sunucusu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
        return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
