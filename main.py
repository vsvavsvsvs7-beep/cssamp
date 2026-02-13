import discord
from discord.ext import commands
import google.generativeai as genai
import os
import datetime

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE"

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class TatangCS(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        print(f"✅ Tatang Bot Online: {self.user}")

bot = TatangCS()

# --- (Sertakan class CSModal, CSAlurView, ServerSelectView dari kode sebelumnya di sini) ---
# ... (Pastikan class-class UI tersebut tetap ada agar !panelcs tidak error)

# ================= COMMANDS (PREFIX !) =================

@bot.command()
async def panelcs(ctx):
    embed = discord.Embed(
        title="🚀 Tatang AI | Premium CS Generator",
        description="Pilih server tujuan kamu pada menu di bawah untuk memulai.",
        color=0x5865f2
    )
    embed.set_footer(text="Tatang Bot • High Quality Content")
    # Pastikan class ServerSelectView sudah kamu copy dari kode sebelumnya
    await ctx.send(embed=embed, view=ServerSelectView())

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="📁 Tatang Bot | Main Menu",
        description="Daftar perintah yang tersedia (Gunakan prefix `!`):",
        color=0x4287f5
    )
    embed.add_field(name="📝 `!panelcs`", value="Buka panel pembuat CS.", inline=False)
    embed.add_field(name="📊 `!status` atau `!ping` ", value="Cek koneksi bot.", inline=True)
    embed.add_field(name="⚠️ `!report` ", value="Laporkan masalah.", inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(aliases=['ping'])
async def status(ctx):
    latensi = round(bot.latency * 1000)
    embed = discord.Embed(title="📊 System Status", color=0x00ff00)
    embed.add_field(name="📡 Latency", value=f"`{latensi}ms`", inline=True)
    embed.add_field(name="🔋 Power", value="`Online`", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def report(ctx, *, pesan=None):
    if not pesan:
        return await ctx.send("❌ Format salah! Gunakan: `!report [masalah kamu]`")
    
    print(f"⚠️ REPORT: {ctx.author} -> {pesan}")
    await ctx.send(f"✅ **{ctx.author.name}**, laporan kamu telah terkirim ke Developer.", delete_after=10)

# ================= START =================
if TOKEN:
    bot.run(TOKEN)
