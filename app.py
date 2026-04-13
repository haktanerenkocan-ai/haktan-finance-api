import requests
from datetime import datetime, timedelta

def fiyat_getir(kod):
    kod = kod.upper().strip()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tefas.gov.tr/"
    }

    # 1️⃣ Önce en sağlam endpoint (Comparison)
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

    # 2️⃣ Olmazsa geçmiş veriden çek (7 gün geriye bakar)
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

    # 3️⃣ Hiçbir şey çalışmazsa
    return 0


# TEST
print(fiyat_getir("AFT"))
