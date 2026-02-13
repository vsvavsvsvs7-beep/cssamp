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
        await self.change_presence(activity=discord.Game(name="!menu | Premium CS AI"))
        print(f"✅ {self.user} is online!")

bot = TatangBot()

# ================= UI LOGIC (Penyebab Error Sebelumnya) =================

class CSDetailModal(discord.ui.Modal):
    def __init__(self, server, side, data_awal):
        super().__init__(title=f"Detail Cerita ({side})")
        self.server, self.side, self.data_awal = server, side, data_awal
        self.bakat = discord.ui.TextInput(label="Bakat Karakter", placeholder="Contoh: Supir ahli, penembak...", required=True)
        self.tambahan = discord.ui.TextInput(label="Detail Tambahan", style=discord.TextStyle.paragraph, placeholder="Masa lalu kelam, dll...", required=False)
        self.add_item(self.bakat)
        self.add_item(self.tambahan)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("⌛ **AI sedang menulis cerita panjang...**", ephemeral=True)
        prompt = f"Buatkan CS GTA SAMP server {self.server} sisi {self.side}. Nama: {self.data_awal['nama']}, Asal: {self.data_awal['asal']}, Bakat: {self.bakat.value}. Minimal 500 kata, 3 paragraf, format BBCode."
        try:
            response = ai_model.generate_content(prompt)
            await interaction.followup.send(f"✅ **CS SELESAI!**\n```bbcode\n{response.text}\n```")
        except Exception as e:
            await interaction.followup.send(f"❌ Error AI: {e}")

class CSMainModal(discord.ui.Modal, title="Form Biodata (1/2)"):
    nama = discord.ui.TextInput(label="Nama IC", placeholder="John_Doe")
    asal = discord.ui.TextInput(label="Kota Asal", placeholder="New York")
    def __init__(self, server, side):
        super().__init__()
        self.server, self.side = server, side

    async def on_submit(self, interaction: discord.Interaction):
        data = {"nama": self.nama.value, "asal": self.asal.value}
        await interaction.response.send_modal(CSDetailModal(self.server, self.side, data))

class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Goodside", style=discord.ButtonStyle.success, emoji="😇")
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSMainModal(self.server, "Goodside"))

    @discord.ui.button(label="Badside", style=discord.ButtonStyle.danger, emoji="😈")
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSMainModal(self.server, "Badside"))

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="JGRP", emoji="🎮"),
            discord.SelectOption(label="SSRP", emoji="🇺🇸"),
            discord.SelectOption(label="Virtual RP", emoji="💻"),
        ]
        super().__init__(placeholder="Pilih Server...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"📍 Server: **{self.values[0]}**. Pilih alur:", view=CSAlurView(self.values[0]), ephemeral=True)

class ServerSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

# ================= COMMANDS =================

@bot.command()
async def menu(ctx):
    embed = discord.Embed(title="🌟 TATANG AI MENU", description="`!panelcs` - Buat CS\n`!status` - Cek Bot", color=0x5865f2)
    await ctx.send(embed=embed)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send(f"❌ Gunakan di <#{ALLOWED_CHANNEL_ID}>", delete_after=5)
    
    embed = discord.Embed(title="🚀 CS GENERATOR", description="Silakan pilih server tujuan:", color=0x5865f2)
    await ctx.send(embed=embed, view=ServerSelectView())

@bot.command()
async def status(ctx):
    await ctx.send(f"📡 Latency: `{round(bot.latency * 1000)}ms` | Engine: **Online**")

if TOKEN:
    bot.run(TOKEN)
