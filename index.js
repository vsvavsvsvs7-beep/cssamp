require('dotenv').config();
const { Client, GatewayIntentBits, Events } = require('discord.js');
const axios = require('axios');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

client.once(Events.ClientReady, (c) => {
  console.log(`✅ Bot online sebagai ${c.user.tag}`);
});

client.on(Events.MessageCreate, async (message) => {
  if (message.author.bot) return;
  if (!message.content.toLowerCase().startsWith('!ai')) return;

  const prompt = message.content.slice(3).trim();
  if (!prompt) return message.reply('Tulis pertanyaan setelah !ai');

  try {
    await message.channel.sendTyping();

    const response = await axios.post(
      'https://api.groq.com/openai/v1/chat/completions',
      {
        model: 'llama-3.1-8b-instant', // MODEL AKTIF
        messages: [
          { role: 'system', content: 'Kamu adalah AI Discord yang santai dan ramah.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.AI_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const reply = response.data.choices[0].message.content;

    if (!reply) {
      return message.reply('⚠️ AI tidak memberikan respon.');
    }

    if (reply.length > 2000) {
      return message.reply(reply.slice(0, 1990));
    }

    message.reply(reply);

  } catch (error) {
    console.log("===== GROQ ERROR =====");
    console.log(JSON.stringify(error.response?.data || error.message, null, 2));
    message.reply('⚠️ Error AI, cek log Railway.');
  }
});

client.login(process.env.DISCORD_TOKEN);
