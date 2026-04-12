const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async (req, res) => {
  const { kod } = req.query;
  if (!kod) return res.status(400).send("Fon kodu eksik!");

  try {
    // Takasbank'a ajan girişi yapıyoruz
    const url = `https://tefas.takasbank.com.tr/tr/fon-analiz?fonkod=${kod.toUpperCase()}`;
    const { data } = await axios.get(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
    });
    
    const $ = cheerio.load(data);
    
    // Fiyatı HTML içinden söküp alıyoruz
    const fiyat = $('#MainContent_MainContent_LabelLastPrice').text() || 
                  $('.font-weight-bold').first().text();
    
    if (!fiyat) throw new Error("Fiyat bulunamadı");

    // "1.234,56" formatını "1234.56" sayı formatına çevir
    const temizFiyat = fiyat.trim().replace(/\./g, "").replace(",", ".");
    
    res.status(200).send(temizFiyat);
  } catch (e) {
    res.status(200).send("0"); // Hata olursa 0 döner ki tablo patlamasın
  }
};
