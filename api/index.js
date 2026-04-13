const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async (req, res) => {
  const { kod } = req.query;
  if (!kod) return res.status(200).send("Kod Eksik");
  const fonKodu = kod.toUpperCase();

  // STRATEJİ 1: MYNET (Hassas Konumlandırma)
  try {
    const mynetUrl = `https://finans.mynet.com/yatirimfonlari/${fonKodu}`;
    const resp = await axios.get(mynetUrl, { timeout: 4000 });
    const $ = cheerio.load(resp.data);
    
    // Sadece ana fiyat kutusuna odaklan (fn-detail-price)
    let fiyat = $('.fn-detail-price').find('span').first().text() || 
                $('.fn-detail-price').text();

    if (fiyat && fiyat.includes(',')) {
      const temiz = fiyat.trim().split(' ')[0].replace(/\./g, "").replace(",", ".");
      if (parseFloat(temiz) > 0.0001) return res.status(200).send(temiz);
    }
  } catch (e) {}

  // STRATEJİ 2: BLOOMBERG HT (Alternatif Hedef)
  try {
    const bloombergUrl = `https://www.bloomberght.com/yatirim-fonlari/fon-detay/${fonKodu}`;
    const resp = await axios.get(bloombergUrl, { timeout: 4000 });
    const $ = cheerio.load(resp.data);
    
    // class="value" olan ama "lastPrice" ile ilişkili olanı çek
    let fiyat = $('span[class*="value"]').first().text();
    
    if (fiyat && fiyat.includes(',')) {
      const temiz = fiyat.trim().replace(/\./g, "").replace(",", ".");
      if (parseFloat(temiz) > 0.0001) return res.status(200).send(temiz);
    }
  } catch (e) {}

  // STRATEJİ 3: DOVIZ.COM (Hızlı Sızma)
  try {
    const dovizUrl = `https://www.doviz.com/fon/${fonKodu}`;
    const resp = await axios.get(dovizUrl, { timeout: 4000 });
    const $ = cheerio.load(resp.data);
    let fiyat = $('.value').first().text();
    
    if (fiyat && fiyat.includes(',')) {
      const temiz = fiyat.trim().replace(/\./g, "").replace(",", ".");
      if (parseFloat(temiz) > 0.0001) return res.status(200).send(temiz);
    }
  } catch (e) {}

  res.status(200).send("Veri Bulunamadı");
};
