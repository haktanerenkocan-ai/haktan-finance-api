import os
import json
import re
import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Fintables API Karargah Online - Cephe Değiştirildi!"

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: 
        return "Kod eksik", 400
    
    # Yeni Hedef: Fintables Fon Detay Sayfası
    url = f"https://fintables.com/fonlar/{kod}"
    
    try:
        # Fintables'ın Cloudflare korumasını aşmak için yine Cloudscraper kullanıyoruz
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        # Sayfaya taarruz
        res = scraper.get(url, timeout=15)
        
        if res.status_code == 200:
            # HTML'i parçalamak için BeautifulSoup'u devreye sokuyoruz
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Fintables verileri sayfanın içindeki gizli bir script etiketinde tutar (__NEXT_DATA__)
            # Bu etiketi bulup içindeki JSON verisini avlıyoruz
            script_tag = soup.find('script', id='__NEXT_DATA__')
            
            if script_tag:
                try:
                    # JSON verisini sözlüğe çevir
                    data = json.loads(script_tag.string)
                    
                    # Fintables'ın veri labirentinde fiyatın bulunduğu odaya iniyoruz
                    # Not: Bu yol Fintables'ın veri yapısına göredir
                    fon_detaylari = data.get('props', {}).get('pageProps', {}).get('fund', {})
                    fiyat = fon_detaylari.get('price')
                    
                    if fiyat:
                        return str(fiyat).replace(",", ".")
                    else:
                        return f"HATA: {kod} fonu bulundu ama fiyat verisi okunamadı."
                        
                except Exception as e:
                    return f"HATA: Veri ayrıştırma başarısız. (JSON Hatası) - {str(e)}"
            else:
                return "HATA: Fintables sayfa yapısını değiştirmiş, hedef veri paketi bulunamadı."
                
        elif res.status_code == 404:
            return f"HATA 404: Fintables'ta {kod} adında bir fon bulunamadı."
            
        elif res.status_code == 403:
            return "HATA 403: Fintables da Render IP'sini engelledi! (Cloudflare WAF)"
            
        else:
            return f"HATA: Fintables sunucusu yanıt vermedi. Durum Kodu: {res.status_code}"
            
    except Exception as e:
        return f"SİSTEM HATASI: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
