require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

client.once('ready', () => {
  console.log(`✅ Bot online sebagai ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  if (!message.content.startsWith('!ai')) return;

  const prompt = message.content.slice(3).trim();
  if (!prompt) {
    return message.reply('Masukkan pertanyaan setelah !ai');
  }

  message.channel.sendTyping();

  try {
    const response = await axios.post(
      'https://api.groq.com/openai/v1/chat/completions',
      {
        model: 'llama3-8b-8192',
        messages: [
          { role: 'system', content: 'Kamu adalah AI Discord yang ramah dan santai.' },
          { role: 'user', content: prompt }
        ]
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.AI_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const reply = response.data.choices[0].message.content;
    message.reply(reply);

  } catch (error) {
    console.error(error.response?.data || error.message);
    message.reply('⚠️ AI error atau limit habis.');
  }
});

client.login(process.env.DISCORD_TOKEN);
