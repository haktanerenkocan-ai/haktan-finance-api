import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Senin bulduğun gerçek TEFAS uç noktası!
TEFAS_API_URL = "https://www.tefas.gov.tr/api/funds/fonGetiriBaziBilgiGetir"

def get_tefas_data():
    # requests.Session() kullanarak tarayıcı gibi davranıyoruz (Çerezleri otomatik hafızada tutar)
    session = requests.Session()
    
    # 1. AŞAMA: Kimlik Gizleme ve Taze Cookie (Çerez) Alma
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        # Önce TEFAS ana sayfasına girip bizi "insan" sanmalarını ve taze cookie vermelerini sağlıyoruz
        session.get("https://www.tefas.gov.tr/fon-getirileri", headers=headers, timeout=10)
    except:
        pass

    # 2. AŞAMA: Senin Deşifre Ettiğin Payload (Veri Yükü)
    payload = {
        "calismaTipi": 2,
        "dil": "TR",
        "fonTipi": "YAT",
        "islem": 1,
        "donemGetiri1a": "1",
        "donemGetiri1y": "1",
        "donemGetiri3a": "1",
        "donemGetiri3y": "1",
        "donemGetiri5y": "1",
        "donemGetiri6a": "1",
        "donemGetiriyb": "1",
        "fonGrubu": None,
        "fonTurAciklama": None,
        "fonTurKod": None,
        "kurucuKodu": None,
        "sfonTurKod": None,
        "basTarih": None,
        "bitTarih": None
    }

    # API'ye özel istek başlıkları (İşte bütün sır buradaki Content-Type ayarında)
    api_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json", # Eski kodda bu yoktu, sistem bizi bu yüzden reddetti!
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/fon-getirileri"
    }

    try:
        # Eski koddaki 'data=payload' kısmını 'json=payload' yaptık. TEFAS'ın istediği dil bu.
        res = session.post(TEFAS_API_URL, json=payload, headers=api_headers, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("API Hatası:", e)
    return None

@app.route('/')
def home():
    return "Karargah Akıllı TEFAS API Servisi (Hayalet Mod) Canlı!"

@app.route('/toplu_fiyat')
def get_toplu_fiyat():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0 for kod in kod_listesi}
    
    veri = get_tefas_data()
    if veri and isinstance(veri, list):
        for fon in veri:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    fiyat_str = str(fon.get("FIYAT", "0")).replace(",", ".")
                    sonuclar[fon_kodu] = float(fiyat_str)
                except:
                    sonuclar[fon_kodu] = 0
                    
    return jsonify(sonuclar)

@app.route('/toplu_degisim')
def get_toplu_degisim():
    kodlar_str = request.args.get('kodlar', '').upper()
    if not kodlar_str: return jsonify({})
    
    kod_listesi = [k.strip() for k in kodlar_str.split(',') if k.strip()]
    sonuclar = {kod: 0.0 for kod in kod_listesi}
    
    veri = get_tefas_data()
    if veri and isinstance(veri, list):
        for fon in veri:
            fon_kodu = fon.get("FONKODU", "").upper().strip()
            if fon_kodu in sonuclar:
                try:
                    # Günlük getiri anahtarını garantilemek için iki olasılığı da ekledik
                    degisim_str = str(fon.get("GUNLUKGETIRI", fon.get("GETIRI1G", "0"))).replace(",", ".")
                    sonuclar[fon_kodu] = float(degisim_str) / 100
                except:
                    sonuclar[fon_kodu] = 0.0
                    
    return jsonify(sonuclar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
