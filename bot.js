const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

cron.schedule('*/5 * * * *', async () => {   // هر ۵ دقیقه یکبار
  console.log("Checking for new tokens on Base...");

  try {
    // روش درست‌تر و پایدارتر
    const response = await axios.get('https://api.dexscreener.com/latest/dex/search?q=base', {
      timeout: 15000
    });
    
    const pairs = response.data.pairs || [];
    console.log(`Found ${pairs.length} pairs on search`);

    // فیلتر توکن‌های جدید با لیکوئیدیتی خوب
    const interesting = pairs.filter(p => {
      if (!p.liquidity || !p.liquidity.usd) return false;
      if (p.liquidity.usd < 5000) return false;                    // حداقل لیکوئیدیتی
      if (!p.pairCreatedAt) return false;
      
      const ageMinutes = (Date.now() - new Date(p.pairCreatedAt).getTime()) / (1000 * 60);
      return ageMinutes < 30;   // فقط توکن‌های کمتر از ۳۰ دقیقه
    });

    console.log(`Found ${interesting.length} interesting new tokens`);

    if (interesting.length > 0) {
      console.log("New token found! Symbol:", interesting[0].baseToken.symbol);
    }

  } catch (error) {
    console.log("Error:", error.message);
    if (error.response) {
      console.log("Status:", error.response.status);
    }
  }
});

console.log("Bot is running and checking every 5 minutes!");
