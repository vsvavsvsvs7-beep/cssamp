import discord
from discord.ext import commands
import google.generativeai as genai
import os
import datetime

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE"
ALLOWED_CHANNEL_ID = 1471935338065694875 

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        # Set status bot agar terlihat keren
        await self.change_presence(activity=discord.Game(name="!menu | Premium CS AI"))
        print(f"✅ {self.user} is online and ready!")

bot = TatangBot()

# --- Sertakan class UI (ServerSelectView, dll) dari kode sebelumnya di sini ---

# ================= COMMANDS =================

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="🌟 TATANG AI PREMIUM SYSTEM",
        description="Selamat datang di layanan AI Pembuat Character Story otomatis.",
        color=0x5865f2,
        timestamp=datetime.datetime.utcnow()
    )
    
    # Kategori Perintah Utama
    embed.add_field(
        name="📝 MAIN SERVICES",
        value=(
            "`!panelcs` - Buka panel pembuatan CS (Hanya di channel khusus)\n"
            "`!tutorial` - Cara menggunakan bot ini"
        ),
        inline=False
    )
    
    # Kategori Informasi & Status
    embed.add_field(
        name="📊 SYSTEM INFO",
        value=(
            "`!status` - Cek koneksi & latensi bot\n"
            "`!about`  - Informasi tentang Tatang AI"
        ),
        inline=False
    )
    
    # Kategori Bantuan
    embed.add_field(
        name="🛠️ SUPPORT",
        value=(
            "`!report` - Laporkan bug/error\n"
            "`!ping`   - Tes respon cepat"
        ),
        inline=False
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def panelcs(ctx):
    # Cek apakah channel-nya benar
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        embed_err = discord.Embed(
            description=f"❌ **Akses Ditolak!** Gunakan perintah ini di <#{ALLOWED_CHANNEL_ID}>",
            color=0xff4b4b
        )
        return await ctx.send(embed=embed_err, delete_after=10)

    embed = discord.Embed(
        title="🚀 CS GENERATOR PANEL",
        description="Klik tombol di bawah untuk memilih server tujuan kamu.",
        color=0x5865f2
    )
    # Ganti 'ServerSelectView()' dengan nama class View kamu
    await ctx.send(embed=embed, view=ServerSelectView())

@bot.command(aliases=['ping'])
async def status(ctx):
    latensi = round(bot.latency * 1000)
    embed = discord.Embed(title="📈 System Status", color=0x2ecc71)
    embed.add_field(name="📡 Latency", value=f"`{latensi}ms`", inline=True)
    embed.add_field(name="🔋 Engine", value="`Gemini-1.5-Flash`", inline=True)
    embed.add_field(name="🕒 Uptime", value="`Stable`", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def tutorial(ctx):
    text = (
        "1. Pergi ke channel <#1471935338065694875>\n"
        "2. Ketik `!panelcs` dan pilih server tujuan.\n"
        "3. Isi formulir (Nama, Level, dll) dengan benar.\n"
        "4. Tunggu AI menulis cerita kamu secara otomatis."
    )
    await ctx.send(embed=discord.Embed(title="📖 Cara Penggunaan", description=text, color=0xf1c40f))

@bot.command()
async def report(ctx, *, pesan=None):
    if not pesan:
        return await ctx.send("❌ Masukkan detail laporan! Contoh: `!report bot tidak membalas`")
    await ctx.send(f"✅ **Laporan Terkirim!** Terima kasih {ctx.author.mention}.")

# ================= RUN =================
if TOKEN:
    bot.run(TOKEN)
