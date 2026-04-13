const axios = require('axios');

module.exports = async (req, res) => {
  const { kod } = req.query;
  if (!kod) return res.status(200).send("Kod Eksik");
  const fonKodu = kod.toUpperCase();

  // Denenecek Kaynaklar ve URL Yapıları
  const kaynaklar = [
    {
      name: 'Mynet',
      url: `https://finans.mynet.com/yatirimfonlari/fon-detay/${fonKodu}/`,
      regex: /"lastPrice":\s*"([0-9,.]+)"/  // JSON verisinden yakalamaya çalışır
    },
    {
      name: 'Bloomberg',
      url: `https://www.bloomberght.com/yatirim-fonlari/fon-detay/${fonKodu}`,
      regex: /class="value[^"]*">([0-9,.]+)</
    },
    {
      name: 'TEFAS_Alternatif',
      url: `https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=${fonKodu}`,
      regex: /MainContent_MainContent_LabelLastPrice">([0-9,.]+)</
    }
  ];

  for (let kaynak of kaynaklar) {
    try {
      const response = await axios.get(kaynak.url, {
        timeout: 5000,
        headers: { 
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
          'Accept-Language': 'tr-TR,tr;q=0.9'
        }
      });

      const html = response.data;
      const match = html.match(kaynak.regex);

      if (match && match[1]) {
        const temizFiyat = match[1].trim().replace(/\./g, "").replace(",", ".");
        if (!isNaN(parseFloat(temizFiyat)) && parseFloat(temizFiyat) > 0) {
          return res.status(200).send(temizFiyat);
        }
      }
    } catch (e) {
      console.log(`${kaynak.name} denemesi başarısız.`);
    }
  }

  res.status(200).send("Veri Bulunamadı");
};
