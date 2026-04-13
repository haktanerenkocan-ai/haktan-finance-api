const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async (req, res) => {
  const { kod } = req.query;
  if (!kod) return res.status(200).send("Kod Eksik");

  const fonKodu = kod.toUpperCase();
  
  // 1. STRATEJİ: MYNET FİNANS (Vercel IP'lerine genelde daha nazik davranır)
  try {
    const mynetUrl = `https://finans.mynet.com/yatirimfonlari/${fonKodu}`;
    const response = await axios.get(mynetUrl, {
      timeout: 4000,
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0' }
    });
    
    const $ = cheerio.load(response.data);
    // Mynet'teki fiyat etiketini yakalıyoruz
    let fiyat = $('.fn-detail-price').first().text() || $('.flex.items-center span').eq(1).text();
    
    if (fiyat && fiyat.length > 2) {
      const temizFiyat = fiyat.trim().replace(/\./g, "").replace(",", ".");
      if(!isNaN(parseFloat(temizFiyat))) return res.status(200).send(temizFiyat);
    }
  } catch (e) {
    console.log("Mynet denemesi başarısız.");
  }

  // 2. STRATEJİ: BLOOMBERG HT (Yedek)
  try {
    const bloombergUrl = `https://www.bloomberght.com/yatirim-fonlari/fon-detay/${fonKodu}`;
    const response = await axios.get(bloombergUrl, { timeout: 4000 });
    const $ = cheerio.load(response.data);
    let fiyat = $('span.value.lastPrice').text();
    
    if (fiyat) {
      const temizFiyat = fiyat.trim().replace(/\./g, "").replace(",", ".");
      if(!isNaN(parseFloat(temizFiyat))) return res.status(200).send(temizFiyat);
    }
  } catch (e) {
    console.log("Bloomberg denemesi başarısız.");
  }

  // Her şey patlarsa
  res.status(200).send("Veri Bulunamadı");
};
