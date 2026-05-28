const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

cron.schedule('*/6 * * * *', async () => {   // هر ۶ دقیقه
  console.log("Checking for new tokens on Base...");

  try {
    // آدرس درست و تست شده
    const response = await axios.get('https://api.dexscreener.com/latest/dex/pairs/base', {
      timeout: 10000
    });
    
    const pairs = response.data.pairs || [];
    console.log(`Found ${pairs.length} pairs`);

    // فیلتر توکن‌های جدید
    const newOnes = pairs.filter(p => {
      if (!p.liquidity?.usd || p.liquidity.usd < 8000) return false;
      
      const age = (Date.now() - new Date(p.pairCreatedAt).getTime()) / (1000 * 60);
      return age < 40; // کمتر از ۴۰ دقیقه
    });

    console.log(`Interesting new tokens: ${newOnes.length}`);

    if (newOnes.length > 0) {
      console.log("✅ New token example:", newOnes[0].baseToken.symbol);
    }

  } catch (error) {
    console.log("Error:", error.message);
    if (error.response) {
      console.log("Status Code:", error.response.status);
    }
  }
});

console.log("Bot is running - checking every 6 minutes");
