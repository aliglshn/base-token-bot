const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

cron.schedule('*/30 * * * * *', async () => {
  console.log("Checking for new tokens on Base...");

  try {
    const response = await axios.get('https://api.dexscreener.com/latest/dex/pairs/base');
    const pairs = response.data.pairs || [];
    
    console.log(`Found ${pairs.length} pairs`);
    
  } catch (error) {
    console.log("Error:", error.message);
  }
});

console.log("Bot is running and checking every 30 seconds!");
