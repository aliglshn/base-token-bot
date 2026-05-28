const axios = require('axios');
const cron = require('node-cron');

console.log("Bot is starting...");

// تنظیمات
const GROK_API_KEY = process.env.GROK_API_KEY;   // بعداً در Railway اضافه می‌کنیم

async function generateTweet(token) {
  const prompt = `Create a short, exciting tweet (under 240 characters) about this new token on Base:

Name: ${token.baseToken.name} (${token.baseToken.symbol})
Address: ${token.baseToken.address}
Liquidity: $${Math.round(token.liquidity.usd)}
24h Volume: $${Math.round(token.volume?.h24 || 0)}
Age: ${Math.round((Date.now() - new Date(token.pairCreatedAt).getTime()) / 60000)} minutes

Make it sound professional and hype, use emojis, good for crypto twitter. Do not add any warnings.`;

  try {
    const response = await axios.post('https://api.x.ai/v1/chat/completions', {
      model: "grok-3",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.8,
      max_tokens: 150
    }, {
      headers: {
        'Authorization': `Bearer ${GROK_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data.choices[0].message.content.trim();
  } catch (e) {
    console.log("AI Error:", e.message);
    // توییت پشتیبان
    return `New token on Base 🔥\n\n${token.baseToken.symbol} just launched!\nLiquidity: $${Math.round(token.liquidity.usd)}\n\n${token.baseToken.address}\n\nDYOR!`;
  }
}

// چک توکن
async function checkNewTokens() {
  try {
    console.log("Fetching data from Dexscreener...");

    const response = await axios.get('https://api.dexscreener.com/latest/dex/search?q=base', {
      timeout: 15000
    });

    const pairs = response.data.pairs || [];

    const interesting = pairs.filter(p => {
      if (!p.liquidity || !p.liquidity.usd || p.liquidity.usd < 8000) return false;
      const ageMinutes = (Date.now() - new Date(p.pairCreatedAt).getTime()) / (1000 * 60);
      return ageMinutes < 60;
    });

    console.log(`Interesting tokens found: ${interesting.length}`);

    for (const token of interesting.slice(0, 2)) {   // حداکثر ۲ تا در هر چک
      console.log(`Generating tweet for ${token.baseToken.symbol}...`);
      const tweet = await generateTweet(token);
      console.log("Generated Tweet:\n", tweet);
      console.log("─".repeat(50));
    }

  } catch (error) {
    console.log("Error:", error.message);
  }
}

// اجرا
console.log("Running first check now...");
checkNewTokens();

cron.schedule('*/8 * * * *', async () => {
  console.log("Running scheduled check...");
  await checkNewTokens();
});

console.log("Bot is running - checking every 8 minutes");
