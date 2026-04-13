import requests
import re
from flask import Flask, request

app = Flask(__name__)

def fiyat_getir(kod):
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={kod}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tefas.gov.tr/"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        html = res.text

        # Fiyatı yakala
        match = re.search(r'font-weight-bold">([\d,]+)', html)

        if match:
            fiyat = match.group(1)
            return float(fiyat.replace(",", "."))
    except:
        pass

    return 0


@app.route("/")
def home():
    return "OK"

@app.route("/fiyat")
def fiyat():
    kod = request.args.get("kod", "")
    if not kod:
        return "Kod gir", 400

    return str(fiyat_getir(kod))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
