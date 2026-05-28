const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

cron.schedule('*/3 * * * *', async () => {   // هر ۳ دقیقه یکبار (خیلی مهم!)
  console.log("Checking for new tokens on Base...");

  try {
    const response = await axios.get('https://api.dexscreener.com/latest/dex/pairs/base', {
      timeout: 10000
    });
    
    const pairs = response.data.pairs || [];
    console.log(`Found ${pairs.length} pairs`);

    // فقط توکن‌های جدید با لیکوئیدیتی خوب
    const newTokens = pairs.filter(p => 
      p.liquidity && 
      p.liquidity.usd > 3000 && 
      p.pairCreatedAt && 
      (Date.now() - new Date(p.pairCreatedAt).getTime()) < 15 * 60 * 1000
    );

    console.log(`Found ${newTokens.length} interesting new tokens`);

  } catch (error) {
    if (error.response && error.response.status === 429) {
      console.log("Rate limit hit. Waiting longer...");
    } else {
      console.log("Error:", error.message);
    }
  }
});

console.log("Bot is running and checking every 3 minutes!");
