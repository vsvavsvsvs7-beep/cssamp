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

# ================= UI LOGIC: FORM & MENU =================

# STEP 3: Form Detail Akhir (Halaman 2/2)
class CSDetailModal(discord.ui.Modal):
    def __init__(self, server, side, data_awal):
        super().__init__(title=f"Detail Cerita ({side}) (2/2)")
        self.server, self.side, self.data_awal = server, side, data_awal
        
        self.bakat = discord.ui.TextInput(
            label="Bakat/Keahlian Dominan Karakter", 
            placeholder="Contoh: Penembak jitu, negosiator ulung, supir ahli...", 
            required=True
        )
        self.kultur = discord.ui.TextInput(
            label="Kultur/Etnis (Opsional)", 
            placeholder="Contoh: African-American, Hispanic...", 
            required=False
        )
        self.tambahan = discord.ui.TextInput(
            label="Detail Tambahan (Opsional)", 
            style=discord.TextStyle.paragraph, 
            placeholder="Contoh: Punya hutang, dikhianati geng lama, dll.", 
            max_length=1000,
            required=False
        )
        
        self.add_item(self.bakat)
        self.add_item(self.kultur)
        self.add_item(self.tambahan)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"⌛ **AI sedang menyusun narasi panjang untuk {self.server}...**", ephemeral=True)
        
        prompt = f"""
        Buatkan CS GTA SAMP panjang (min 500 kata) untuk server {self.server}.
        Side: {self.side} | Nama: {self.data_awal['nama']} | Level: {self.data_awal['level']}
        Gender: {self.data_awal['jk']} | Lahir: {self.data_awal['tgl']} | Asal: {self.data_awal['asal']}
        Bakat: {self.bakat.value} | Etnis: {self.kultur.value} | Tambahan: {self.tambahan.value}
        Output: BBCode Forum rapi ([center], [justify], [b]). Bahasa Indonesia baku.
        """
        
        try:
            response = ai_model.generate_content(prompt)
            await interaction.followup.send(f"✅ **CS SELESAI!** Salin BBCode di bawah:\n```bbcode\n{response.text}\n```")
        except Exception as e:
            await interaction.followup.send(f"❌ Error AI: {e}")

# STEP 2: Form Biodata (Halaman 1/2)
class CSMainModal(discord.ui.Modal):
    def __init__(self, server, side):
        super().__init__(title=f"Form Biodata ({side}) (1/2)")
        self.server, self.side = server, side
        
        self.nama = discord.ui.TextInput(label="Nama Lengkap Karakter (IC)", placeholder="Contoh: John_Washington", required=True)
        self.level = discord.ui.TextInput(label="Level Karakter", placeholder="Contoh: 1", required=True)
        self.jk = discord.ui.TextInput(label="Jenis Kelamin", placeholder="Contoh: Laki-laki / Perempuan", required=True)
        self.tgl = discord.ui.TextInput(label="Tanggal Lahir", placeholder="Contoh: 17 Agustus 1995", required=True)
        self.asal = discord.ui.TextInput(label="Kota Asal", placeholder="Contoh: Chicago, Illinois", required=True)
        
        self.add_item(self.nama); self.add_item(self.level); self.add_item(self.jk)
        self.add_item(self.tgl); self.add_item(self.asal)

    async def on_submit(self, interaction: discord.Interaction):
        data_awal = {
            "nama": self.nama.value, "level": self.level.value, 
            "jk": self.jk.value, "tgl": self.tgl.value, "asal": self.asal.value
        }
        await interaction.response.send_modal(CSDetailModal(self.server, self.side, data_awal))

# STEP 1: Pilih Sisi (Good/Bad)
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

# STEP 0: Pilih Server (Dropdown Lengkap Sesuai Gambar)
class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="SSRP", description="State Side RP", emoji="🇺🇸"),
            discord.SelectOption(label="Virtual RP", description="Virtual Roleplay", emoji="💻"),
            discord.SelectOption(label="AARP", description="Air Asia RP", emoji="✈️"),
            discord.SelectOption(label="GCRP", description="Grand Country RP", emoji="🌳"),
            discord.SelectOption(label="TEN ROLEPLAY", description="10RP", emoji="🔟"),
            discord.SelectOption(label="CPRP", description="Cyristal Pride RP", emoji="💎"),
            discord.SelectOption(label="Relative RP", description="Relative RP", emoji="👪"),
            discord.SelectOption(label="JGRP", description="Jogjagamers RP", emoji="🎮"),
            discord.SelectOption(label="FMRP", description="FAMERLONE RP", emoji="🛡️"),
        ]
        super().__init__(placeholder="Pilih server tujuan...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content=f"📍 Server: **{self.values[0]}**\nPilih alur cerita untuk karaktermu:", 
            view=CSAlurView(self.values[0]), 
            ephemeral=True
        )

class ServerSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

# ================= COMMANDS =================

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="📂 TATANG AI | DASHBOARD",
        description="Pilih layanan di bawah ini:",
        color=0x4287f5,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="📝 `!panelcs`", value="> Mulai membuat Character Story (Hanya di channel khusus).", inline=False)
    embed.add_field(name="📊 `!status` ", value="> Cek kondisi bot dan koneksi.", inline=True)
    embed.add_field(name="📖 `!help`   ", value="> Panduan penggunaan.", inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send(f"❌ Gunakan di <#{ALLOWED_CHANNEL_ID}>", delete_after=5)
    
    embed = discord.Embed(
        title="🚀 PRE-STEP: PEMILIHAN SERVER",
        description="Pilih server tujuan kamu melalui menu di bawah ini:",
        color=0x5865f2
    )
    embed.set_image(url="https://i.imgur.com/your_banner_here.png") # Opsional
    await ctx.send(embed=embed, view=ServerSelectView())

@bot.command()
async def status(ctx):
    await ctx.send(f"📡 Latency: `{round(bot.latency * 1000)}ms` | AI Engine: **Online**")

if TOKEN:
    bot.run(TOKEN)
