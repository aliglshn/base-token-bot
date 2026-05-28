const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

// چک فوری وقتی بات شروع می‌شه
console.log("Running first check now...");
checkNewTokens();

cron.schedule('*/6 * * * *', async () => {   // هر ۶ دقیقه
  console.log("Running scheduled check...");
  await checkNewTokens();
});

async function checkNewTokens() {
  try {
    console.log("Fetching data from Dexscreener...");

    const response = await axios.get('https://api.dexscreener.com/latest/dex/search?q=base', {
      timeout: 15000
    });

    const pairs = response.data.pairs || [];
    console.log(`Total pairs received: ${pairs.length}`);

    // فیلتر توکن‌های جدید و خوب
    const interesting = pairs.filter(p => {
      if (!p.liquidity || !p.liquidity.usd || p.liquidity.usd < 8000) return false;
      
      const ageMinutes = (Date.now() - new Date(p.pairCreatedAt).getTime()) / (1000 * 60);
      return ageMinutes < 60; // توکن‌های کمتر از ۱ ساعت
    });

    console.log(`Interesting new tokens found: ${interesting.length}`);

    if (interesting.length > 0) {
      console.log("✅ New Token Example:", interesting[0].baseToken.symbol, 
                 "| Liquidity: $" + interesting[0].liquidity.usd);
    }

  } catch (error) {
    console.log("Error:", error.message);
    if (error.response) {
      console.log("Status Code:", error.response.status);
    }
  }
}

console.log("Bot is running - checking every 6 minutes");
