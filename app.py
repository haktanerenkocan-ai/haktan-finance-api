import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pytefas import Crawler

app = Flask(__name__)
tefas_crawler = Crawler()

def get_pytefas_data(kodlar):
    bugun = datetime.now()
    # Değişimi hesaplamak için dünün de verisine ihtiyacımız var, hafta sonlarını atlamak için 7 gün çekiyoruz
    baslangic = (bugun - timedelta(days=7)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")
    
    sonuclar_fiyat = {}
    sonuclar_degisim = {}
    
    try:
        df = tefas_crawler.fetch(start=baslangic, end=bitis, kind="YAT")
        
        if df is not None and not df.empty:
            df = df.sort_values(by='date', ascending=True)
            
            for kod in kodlar:
                fon_df = df[df['fund_code'] == kod]
                if not fon_df.empty:
                    # 1. Aşama: En güncel fiyatı çekiyoruz
                    son_fiyat = float(fon_df.iloc[-1]['price'])
                    sonuclar_fiyat[kod] = son_fiyat
                    
                    # 2. Aşama: Değişim Hesabı (Eğer en az 2 günlük veri varsa hesaplar)
                    if len(fon_df) >= 2:
                        onceki_fiyat = float(fon_df.iloc[-2]['price'])
                        if onceki_fiyat > 0:
                            degisim = (son_fiyat - onceki_fiyat) / onceki_fiyat
                            sonuclar_degisim[kod] = degisim
                        else:
                            sonuclar_degisim[kod] = 0.0
                    else:
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
    return "Karargah V5.1 (PyTefas Tam Sürüm) Çevrimiçi!"

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
