import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from tefas import Crawler
import pandas as pd

app = Flask(__name__)
crawler = Crawler()

@app.route('/')
def home():
    return "Karargah TEFAS Crawler Kütüphanesi Canlı!"

def get_tefas_verisi(kodlar):
    bugun = datetime.now()
    # Hafta sonu ve tatil boşluklarını kapatmak için son 7 günü çekiyoruz
    baslangic = (bugun - timedelta(days=7)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    
    sonuclar_fiyat = {}
    sonuclar_degisim = {}
    
    try:
        # TEFAS kütüphanesi tüm bağlantıları, çerezleri ve tablo yapısını kendisi çözer
        df = crawler.fetch(start_date=baslangic, end_date=bitis, name=kodlar, columns=["code", "date", "price", "daily_return"])
        
        if df is not None and not df.empty:
            # Gelen veriyi tarihe göre sıralıyoruz (En güncel fiyat en sonda kalsın)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date', ascending=True)
            
            for kod in kodlar:
                # Sadece ilgili fonun geçmişini al
                fon_df = df[df['code'] == kod]
                if not fon_df.empty:
                    son_kayit = fon_df.iloc[-1] # En güncel günün satırı
                    sonuclar_fiyat[kod] = float(son_kayit['price'])
                    sonuclar_degisim[kod] = float(son_kayit['daily_return']) / 100
                else:
                    sonuclar_fiyat[kod] = 0.0
                    sonuclar_degisim[kod] = 0.0
        else:
            for kod in kodlar:
                sonuclar_fiyat[kod] = 0.0
                sonuclar_degisim[kod] = 0.0
                
    except Exception as e:
        print("Crawler Hatası:", str(e))
        for kod in kodlar:
            sonuclar_fiyat[kod] = 0.0
            sonuclar_degisim[kod] = 0.0
            
    return sonuclar_fiyat, sonuclar_degisim

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    
    fiyatlar, _ = get_tefas_verisi(kod_listesi)
    return jsonify(fiyatlar)

@app.route('/toplu_degisim')
def get_toplu_degisim():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    
    _, degisimler = get_tefas_verisi(kod_listesi)
    return jsonify(degisimler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
