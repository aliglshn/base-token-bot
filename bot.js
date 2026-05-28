const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

cron.schedule('*/7 * * * *', async () => {   // هر ۷ دقیقه یکبار (ایمن)
  console.log("Checking for new tokens on Base...");

  try {
    // آدرس درست برای جستجو
    const response = await axios.get('https://api.dexscreener.com/latest/dex/search?q=base', {
      timeout: 15000
    });

    const pairs = response.data.pairs || [];
    console.log(`Total pairs found: ${pairs.length}`);

    // فیلتر توکن‌های جدید و خوب
    const newInteresting = pairs.filter(p => {
      if (!p.liquidity || !p.liquidity.usd) return false;
      if (p.liquidity.usd < 8000) return false;

      const ageMinutes = (Date.now() - new Date(p.pairCreatedAt).getTime()) / (1000 * 60);
      return ageMinutes < 45; // توکن‌های حداکثر ۴۵ دقیقه عمر
    });

    console.log(`Interesting new tokens: ${newInteresting.length}`);

    if (newInteresting.length > 0) {
      const token = newInteresting[0];
      console.log(`✅ New Token Found: ${token.baseToken.symbol} | Liquidity: $${token.liquidity.usd}`);
    }

  } catch (error) {
    console.log("Error:", error.message);
    if (error.response) {
      console.log("Status:", error.response.status);
    }
  }
});

console.log("Bot is running - checking every 7 minutes");
