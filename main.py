import discord
from discord.ext import commands
import google.generativeai as genai
import os
import io
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
        print(f"✅ {self.user} Online & Ready!")

bot = TatangBot()

# ================= STEP 3: MODAL DETAIL (FINAL) =================
class CSDetailModal(discord.ui.Modal):
    def __init__(self, server, side, data_awal):
        super().__init__(title=f"Detail Cerita {side}")
        self.server, self.side, self.data_awal = server, side, data_awal
        
        self.bakat = discord.ui.TextInput(label="Bakat/Keahlian Dominan", placeholder="Contoh: Penembak, supir ahli...", required=True)
        self.tambahan = discord.ui.TextInput(label="Cerita Tambahan", style=discord.TextStyle.paragraph, placeholder="Masa lalu, tujuan hidup, dll...", max_length=1000, required=True)
        
        self.add_item(self.bakat)
        self.add_item(self.tambahan)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("⌛ **AI sedang menyusun CS & Menyiapkan File...**", ephemeral=True)
        
        prompt = f"""
        Buatkan Character Story GTA SAMP panjang (500+ kata) untuk server {self.server}.
        Side: {self.side}
        Nama: {self.data_awal['nama']} | Level: {self.data_awal['lvl']} | Asal: {self.data_awal['asal']}
        Bakat: {self.bakat.value}
        Tambahan: {self.tambahan.value}
        
        Output: Gunakan BBCode Forum [justify] [center] [b]. Bahasa Indonesia formal dan mendalam.
        """
        
        try:
            response = ai_model.generate_content(prompt)
            cerita_teks = response.text
            
            # --- FITUR TAMBAHAN: AUTO-GENERATE FILE .TXT ---
            file_data = io.BytesIO(cerita_teks.encode('utf-8'))
            discord_file = discord.File(file_data, filename=f"CS_{self.data_awal['nama']}.txt")
            
            embed = discord.Embed(
                title="✅ Character Story Selesai!",
                description=f"Berhasil membuat cerita untuk **{self.data_awal['nama']}** di server **{self.server}**.\n\n*Salin teks di bawah atau download file yang terlampir.*",
                color=0x00ff88
            )
            
            await interaction.followup.send(embed=embed)
            await interaction.followup.send(content=f"```bbcode\n{cerita_teks}\n```", file=discord_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ AI Error: {e}")

# ================= STEP 2: MODAL BIODATA =================
class CSMainModal(discord.ui.Modal):
    def __init__(self, server, side):
        super().__init__(title=f"Biodata {side}")
        self.server, self.side = server, side
        
        self.nama = discord.ui.TextInput(label="Nama Lengkap (IC)", placeholder="Contoh: John_Doe", min_length=3, required=True)
        self.lvl = discord.ui.TextInput(label="Level Karakter", placeholder="Contoh: 5", required=True)
        self.asal = discord.ui.TextInput(label="Kota Asal", placeholder="Contoh: Chicago", required=True)
        
        self.add_item(self.nama); self.add_item(self.lvl); self.add_item(self.asal)

    async def on_submit(self, interaction: discord.Interaction):
        data_awal = {"nama": self.nama.value, "lvl": self.lvl.value, "asal": self.asal.value}
        # Lanjut ke modal kedua
        await interaction.response.send_modal(CSDetailModal(self.server, self.side, data_awal))

# ================= STEP 1: PILIH ALUR =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik (Goodside)", style=discord.ButtonStyle.success, emoji="😇")
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSMainModal(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat (Badside)", style=discord.ButtonStyle.danger, emoji="😈")
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSMainModal(self.server, "Badside"))

# ================= STEP 0: PILIH SERVER (LENGKAP) =================
class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="SSRP", description="State Side RP", emoji="🇺🇸"),
            discord.SelectOption(label="Virtual RP", description="Virtual Roleplay", emoji="💻"),
            discord.SelectOption(label="AARP", description="Air Asia RP", emoji="✈️"),
            discord.SelectOption(label="GCRP", description="Grand Country RP", emoji="🌳"),
            discord.SelectOption(label="TEN ROLEPLAY", description="10RP", emoji="🔟"),
            discord.SelectOption(label="CPRP", description="Cyristal Pride RP", emoji="💎"),
            discord.SelectOption(label="Relative RP", description="Relative Roleplay", emoji="👪"),
            discord.SelectOption(label="JGRP", description="Jogjagamers RP", emoji="🎮"),
            discord.SelectOption(label="FMRP", description="FAMERLONE RP", emoji="🛡️"),
        ]
        super().__init__(placeholder="Pilih server tujuan kamu...", options=options)

    async def callback(self, interaction: discord.Interaction):
        view = CSAlurView(self.values[0])
        await interaction.response.send_message(f"📍 Server: **{self.values[0]}**. Pilih alur:", view=view, ephemeral=True)

class ServerSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

# ================= COMMANDS =================
@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="🌟 TATANG AI PREMIUM",
        description="Gunakan `!panelcs` di channel khusus untuk mulai membuat CS.",
        color=0x5865f2
    )
    embed.add_field(name="📍 Channel CS", value=f"<#{ALLOWED_CHANNEL_ID}>", inline=True)
    embed.add_field(name="📡 Status", value="`Online`", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send(f"❌ Gunakan di <#{ALLOWED_CHANNEL_ID}>", delete_after=5)
    
    embed = discord.Embed(
        title="🚀 CS GENERATOR SYSTEM",
        description="Pilih server tujuan kamu untuk memulai pembuatan cerita otomatis.",
        color=0x5865f2
    )
    await ctx.send(embed=embed, view=ServerSelectView())

@bot.command()
async def status(ctx):
    ping = round(bot.latency * 1000)
    await ctx.send(f"📡 Latency: `{ping}ms` | AI Engine: **Gemini 1.5 Flash**")

if TOKEN:
    bot.run(TOKEN)
