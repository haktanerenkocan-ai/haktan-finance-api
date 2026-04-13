const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async (req, res) => {
  const { kod } = req.query;
  if (!kod) return res.status(200).send("Kod Eksik");

  // Birinci hedef: TEFAS Analiz Sayfası (Daha az korumalı olabilir)
  const url = `https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=${kod.toUpperCase()}`;

  try {
    const { data } = await axios.get(url, {
      timeout: 5000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
        'Cache-Control': 'no-cache'
      }
    });

    const $ = cheerio.load(data);
    
    // TEFAS'ın içinden fiyatı söküyoruz (Farklı etiketleri deniyoruz)
    let fiyat = $('.top-list li span').first().text() || 
                $('#MainContent_MainContent_LabelLastPrice').text() ||
                $('.font-weight-bold').text();

    if (!fiyat || fiyat.length < 2) {
       return res.status(200).send("0");
    }

    // "1.234,5678" -> "1234.5678"
    const temizFiyat = fiyat.trim().replace(/\./g, "").replace(",", ".");
    res.status(200).send(temizFiyat);

  } catch (error) {
    // Hata durumunda nedenini anlamak için 0 yerine bir hata kodu gönderelim (Geçici olarak)
    res.status(200).send("Veri Çekilemedi"); 
  }
};
