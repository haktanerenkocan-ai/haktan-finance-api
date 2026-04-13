import requests
from datetime import datetime, timedelta
from flask import Flask, request

app = Flask(__name__)

def fiyat_getir(kod):
    kod = kod.upper().strip()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tefas.gov.tr/"
    }

    # 1️⃣ Comparison endpoint
    try:
        url = "https://www.tefas.gov.tr/api/DB/BindComparisonFundReturns"
        payload = {
            "fontip": "YAT",
            "fonkod": kod
        }

        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json()

        if data.get("data"):
            fiyat = data["data"][0].get("lastprice")
            if fiyat:
                return float(str(fiyat).replace(",", "."))
    except:
        pass

    # 2️⃣ History endpoint (7 gün geriye)
    try:
        url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

        for i in range(7):
            tarih = (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")

            payload = {
                "fontip": "YAT",
                "bastarih": tarih,
                "bittarih": tarih,
                "fonkod": kod
            }

            res = requests.post(url, json=payload, headers=headers, timeout=10)
            data = res.json()

            if data.get("data"):
                fiyat = data["data"][0].get("price")
                if fiyat:
                    return float(str(fiyat).replace(",", "."))
    except:
        pass

    return 0


@app.route("/")
def home():
    return "API Çalışıyor"

@app.route("/fiyat")
def fiyat():
    kod = request.args.get("kod", "")
    if not kod:
        return "Kod gir", 400

    sonuc = fiyat_getir(kod)
    return str(sonuc)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
