import cloudscraper
import re
import os
from flask import Flask, request

app = Flask(__name__)
# iPhone taklidi yapan, zırh delici motor
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'ios', 'mobile': True})

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "Kod eksik", 400
    
    # STRATEJİ LİSTESİ: Sırasıyla bu noktaları vuracağız
    targets = [
        {
            "name": "FVT (Fintables)",
            "url": f"https://fvt.com.tr/fonlar/{kod}",
            "regex": r'₺([0-9.,]+)' # Fiyatın önünde TL simgesi olan her şeyi yakalar
        },
        {
            "name": "Yatirimim",
            "url": f"https://www.yatirimim.com/fonlar/{kod}",
            "regex": r'([0-9]+\,[0-9]{4,})'
        },
        {
            "name": "Doviz.com",
            "url": f"https://www.doviz.com/fon/{kod}",
            "regex": r'([0-9]+\,[0-9]{4,})'
        }
    ]
    
    for target in targets:
        try:
            resp = scraper.get(target["url"], timeout=12)
            if resp.status_code == 200:
                # Sayfada fiyat formatını ara
                match = re.search(target["regex"], resp.text)
                if match:
                    # 1.371,43 formatını 1371.43 formatına çevir
                    fiyat_ham = match.group(1).replace(".", "").replace(",", ".")
                    # Eğer fvt'den 1.371 gibi gelirse noktaları ve virgülleri düzgün temizle
                    fiyat_temiz = "".join(c for c in fiyat_ham if c.isdigit() or c == '.')
                    return fiyat_temiz
        except:
            continue
            
    return "0"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
