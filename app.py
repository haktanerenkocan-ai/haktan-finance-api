import cloudscraper
import re
import os
from flask import Flask, request

app = Flask(__name__)

# Kendimizi iPhone 15'ten giren bir kullanıcı gibi tanıtıyoruz
stealth_options = {
    'browser': 'chrome',
    'platform': 'ios',
    'mobile': True
}
scraper = cloudscraper.create_scraper(browser=stealth_options)

@app.route('/fiyat')
def get_fiyat():
    kod = request.args.get('kod', '').upper()
    if not kod: return "Kod eksik", 400
    
    # Alternatif kaynak listesi (Eğer biri kapatırsa diğeri denenecek)
    sources = [
        f"https://www.doviz.com/fon/{kod}",
        f"https://finans.mynet.com/yatirimfonlari/{kod}"
    ]
    
    for url in sources:
        try:
            # 10 saniye bekleyip veriyi çekmeye çalışıyoruz
            resp = scraper.get(url, timeout=10)
            if resp.status_code == 200:
                # Sayfa içindeki ilk virgüllü sayıya odaklanıyoruz (Genelde fiyattır)
                # Döviz.com ve Mynet için genel bir regex
                match = re.search(r'([0-9]+\,[0-9]{4,})', resp.text)
                if match:
                    fiyat = match.group(1).replace(",", ".")
                    return fiyat
        except:
            continue
            
    return "Hala engelleniyoruz, lokasyon değiştirmelisin."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
