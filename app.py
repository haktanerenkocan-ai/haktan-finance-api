import os
import re
import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "FVT API Karargah Online - Surlar Aşıldı!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    url = f"https://fvt.com.tr/fonlar/yatirim-fonlari/{kod}"
    
    try:
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        res = scraper.get(url, timeout=15)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            sayfa_metni = soup.get_text()
            
            # YENİ RADAR: ₺ simgesini boş ver. Fon fiyatının imzasını arıyoruz: 
            # Birkaç rakam + virgül/nokta + TAM 6 RAKAM (Örn: 2,768049)
            eslesmeler = re.findall(r'(\d{1,5}[.,]\d{6})', sayfa_metni)
            
            if eslesmeler:
                # Sayfada 6 haneli birden fazla rakam olabilir, grafiğin tepesindeki ana fiyat genelde ilk sıradadır
                fiyat = eslesmeler[0] 
                return fiyat.replace(",", ".")
            else:
                # Sayfada hiç 6 haneli rakam yoksa, sitenin arka planı boş mu (JavaScript mi) kontrol edelim
                # Fazla boşlukları temizleyip ilk 300 karakteri karargaha yolla
                temiz_metin = re.sub(r'\s+', ' ', sayfa_metni).strip()
                return f"HATA: Fiyat formatı bulunamadı. Sitenin arka planda gördüğü metin şu: {temiz_metin[:300]}..."
                
        elif res.status_code == 403:
            return "HATA 403: FVT kalkanları Render IP'sini engelledi!"
        elif res.status_code == 404:
            return f"HATA 404: FVT'de {kod} adında bir fon bulunamadı."
        else:
            return f"HATA: FVT sunucusu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
        return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
