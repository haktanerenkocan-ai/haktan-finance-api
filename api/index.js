const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async (req, res) => {
  const { kod } = req.query;
  if (!kod) return res.status(200).send("Kod Eksik");
  const fonKodu = kod.toUpperCase();

  // 1. STRATEJİ: DÖVİZ.COM (Yurt dışı IP'lerine karşı daha esnektir)
  try {
    const dovizUrl = `https://www.doviz.com/fon/${fonKodu}`;
    const resp = await axios.get(dovizUrl, {
      timeout: 5000,
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0' }
    });
    const $ = cheerio.load(resp.data);
    let fiyat = $('.value').first().text();
    
    if (fiyat && fiyat.includes(',')) {
      const temiz = fiyat.trim().replace(/\./g, "").replace(",", ".");
      if (!isNaN(parseFloat(temiz))) return res.status(200).send(temiz);
    }
  } catch (e) {
    console.log("Döviz.com sızması başarısız.");
  }

  // 2. STRATEJİ: ZİRAAT PORTFÖY (Resmi ama bazen filtreleri gevşektir)
  try {
    const ziraatUrl = `https://www.ziraatportfoy.com.tr/tr/fonlar/${fonKodu}`;
    const resp = await axios.get(ziraatUrl, { timeout: 5000 });
    const $ = cheerio.load(resp.data);
    // Sayfa içinde fiyatın geçtiği yeri bulmaya çalışıyoruz
    let fiyat = $('span:contains(","), div:contains(",")').filter(function() {
      return $(this).text().match(/^[0-9]+,[0-9]+$/);
    }).first().text();

    if (fiyat) {
      const temiz = fiyat.trim().replace(/\./g, "").replace(",", ".");
      return res.status(200).send(temiz);
    }
  } catch (e) {
    console.log("Ziraat sızması başarısız.");
  }

  // 3. STRATEJİ: "NÜKLEER SEÇENEK" - Google Search Snippet
  // Google üzerinden fiyatı çekmeye çalışıyoruz (Google Google'ı engellemez!)
  try {
    const googleUrl = `https://www.google.com/search?q=${fonKodu}+fon+fiyatı+tefas`;
    const resp = await axios.get(googleUrl, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' }
    });
    const html = resp.data;
    const match = html.match(/([0-9]+\,[0-9]{4,})/); // "1,2345" gibi formatı arar
    if (match) {
      return res.status(200).send(match[1].replace(",", "."));
    }
  } catch (e) {
    console.log("Google sızması başarısız.");
  }

  res.status(200).send("Karargah: Tüm kaynaklar kilitli!");
};
