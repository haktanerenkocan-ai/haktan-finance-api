import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pytefas import Crawler

app = Flask(__name__)
# Yeni nesil hafif tarayıcımızı başlatıyoruz
tefas_crawler = Crawler()

def get_pytefas_data(kodlar):
    bugun = datetime.now()
    # Hafta sonu boşluğunu atlamak için son 5 günü tarıyoruz
    baslangic = (bugun - timedelta(days=5)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    
    sonuclar_fiyat = {}
    sonuclar_degisim = {}
    
    try:
        # Tek hamlede veriyi yapısal JSON olarak çekiyoruz (Chrome gerektirmez!)
        df = tefas_crawler.fetch(start=baslangic, end=bitis, kind="YAT")
        
        if df is not None and not df.empty:
            # Tarihe göre sırala ki en yeni veri en sona gelsin
            df = df.sort_values(by='date', ascending=True)
            
            for kod in kodlar:
                # Sadece istediğimiz fonun satırlarını filtrele
                fon_df = df[df['fund_code'] == kod]
                if not fon_df.empty:
                    # En son günün verisini al
                    son_kayit = fon_df.iloc[-1]
                    sonuclar_fiyat[kod] = float(son_kayit['price'])
                    
                    # Eğer pytefas günlük getiriyi doğrudan vermiyorsa, 
                    # manuel hesaplama gerektirebilir ama şimdilik fiyatı garantileyelim.
                    # (pytefas 'info' kolonlarında price dönüyor, degisim için ekstra işlem gerekebilir)
                    # Şimdilik değişimi 0 dönelim, fiyatın çalışıp çalışmadığını test edelim.
                    sonuclar_degisim[kod] = 0.0 
                else:
                    sonuclar_fiyat[kod] = 0.0
                    sonuclar_degisim[kod] = 0.0
        else:
            for kod in kodlar:
                sonuclar_fiyat[kod] = 0.0
                sonuclar_degisim[kod] = 0.0
                
    except Exception as e:
        print(f"pytefas Hatası: {str(e)}")
        for kod in kodlar:
            sonuclar_fiyat[kod] = 0.0
            sonuclar_degisim[kod] = 0.0
            
    return sonuclar_fiyat, sonuclar_degisim

@app.route('/')
def home():
    return "Karargah V5.0 (PyTefas Modülü) Çevrimiçi!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    
    fiyatlar, _ = get_pytefas_data(kod_listesi)
    return jsonify(fiyatlar)

@app.route('/toplu_degisim')
def get_toplu_degisim():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    
    _, degisimler = get_pytefas_data(kod_listesi)
    return jsonify(degisimler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
