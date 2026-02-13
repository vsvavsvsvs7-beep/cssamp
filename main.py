import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import datetime

# --- KONFIGURASI ---
TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE"
# ID Channel khusus untuk buat CS
ALLOWED_CHANNEL_ID = 1471935338065694875 

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class TatangCS(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Proses sinkronisasi Slash Command (agar fitur / muncul)
        await self.tree.sync()
        print(f"✅ Sistem Berhasil Sinkron!")

bot = TatangCS()

# --- (Class UI: ServerSelectView, CSAlurView, CSMainModal, CSDetailModal tetap sama seperti kode sebelumnya) ---
# ... (Pastikan kamu tetap menyertakan semua class UI tersebut di file main.py kamu)

# ================= COMMAND !PANELCS (DENGAN LOCK CHANNEL) =================

@bot.command(name="panelcs")
async def panelcs(ctx):
    # Pengecekan ID Channel
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        embed_wrong = discord.Embed(
            title="❌ Akses Ditolak",
            description=f"Maaf, pembuatan CS hanya diperbolehkan di channel <#{ALLOWED_CHANNEL_ID}>.",
            color=0xff4b4b
        )
        return await ctx.send(embed=embed_wrong, delete_after=10)

    # Jika ID Channel benar, tampilkan panel
    embed = discord.Embed(
        title="🚀 Tatang AI | Premium CS Generator",
        description=(
            "Silakan pilih server tujuan kamu pada menu di bawah.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📍 **Channel:** Authorized\n"
            "✨ **Status:** AI Ready to Write\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x5865f2
    )
    embed.set_footer(text="Tatang Bot • High Quality Content")
    await ctx.send(embed=embed, view=ServerSelectView())

# ================= SLASH COMMANDS (Bisa di mana saja atau di-lock juga) =================

@bot.tree.command(name="menu", description="Menampilkan menu utama bot")
async def menu_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📁 Tatang Bot | Main Menu",
        description=f"Gunakan `!panelcs` di <#{ALLOWED_CHANNEL_ID}> untuk membuat Character Story.",
        color=0x4287f5
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Cek latensi sistem")
async def status_slash(interaction: discord.Interaction):
    ping = round(bot.latency * 1000)
    await interaction.response.send_message(f"📡 Latensi: `{ping}ms` | AI: **Stable**")

# ================= START =================
if TOKEN:
    bot.run(TOKEN)
