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

# Perbaikan Inisialisasi AI
genai.configure(api_key=GEMINI_API_KEY)
# Menggunakan penamaan model yang lebih universal
ai_model = genai.GenerativeModel('models/gemini-1.5-flash')

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | CS AI Premium"))
        print(f"✅ Bot Berhasil Online: {self.user}")

bot = TatangBot()

# ================= MODAL FORM (ANTI-ERROR) =================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    # Saya ringkas labelnya agar tidak kena 'Invalid Form Body'
    identitas = discord.ui.TextInput(
        label="Nama IC & Level", 
        placeholder="Contoh: John_Doe | Level 5", 
        required=True
    )
    biodata = discord.ui.TextInput(
        label="Gender & Kota Asal", 
        placeholder="Contoh: Laki-laki | Chicago", 
        required=True
    )
    detail = discord.ui.TextInput(
        label="Bakat & Masa Lalu", 
        style=discord.TextStyle.paragraph, 
        placeholder="Tuliskan keahlian dan ringkasan cerita karaktermu...",
        max_length=2000,
        required=True
    )

    def __init__(self, server, side):
        super().__init__()
        self.server = server
        self.side = side

    async def on_submit(self, interaction: discord.Interaction):
        # Langsung respon agar tidak timeout
        await interaction.response.send_message("⌛ **AI sedang memproses cerita kamu...**", ephemeral=True)
        
        prompt = (
            f"Buatkan Character Story GTA SAMP untuk server {self.server}.\n"
            f"Alur: {self.side}\n"
            f"Identitas: {self.identitas.value}\n"
            f"Biodata: {self.biodata.value}\n"
            f"Latar Belakang: {self.detail.value}\n\n"
            "SYARAT: Minimal 500 kata, BBCode forum lengkap, bahasa Indonesia yang mendalam."
        )
        
        try:
            response = ai_model.generate_content(prompt)
            hasil_cerita = response.text
            
            # Buat file .txt otomatis
            file_data = io.BytesIO(hasil_cerita.encode('utf-8'))
            file_name = f"CS_{self.identitas.value.split('|')[0].strip()}.txt"
            discord_file = discord.File(file_data, filename=file_name)
            
            embed = discord.Embed(
                title="✅ Character Story Berhasil!",
                description=f"Server: **{self.server}** | Sisi: **{self.side}**\n\n*File .txt telah dilampirkan di bawah.*",
                color=0x2ecc71,
                timestamp=datetime.datetime.utcnow()
            )
            
            await interaction.followup.send(embed=embed)
            await interaction.followup.send(content=f"```bbcode\n{hasil_cerita[:1800]}...\n(Lihat file .txt untuk teks lengkap)```", file=discord_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Kesalahan Sistem: {str(e)}")

# ================= SELECTION LOGIC =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik (Goodside)", style=discord.ButtonStyle.success, emoji="😇")
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat (Badside)", style=discord.ButtonStyle.danger, emoji="😈")
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="JGRP", emoji="🎮"),
            discord.SelectOption(label="SSRP", emoji="🇺🇸"),
            discord.SelectOption(label="Virtual RP", emoji="💻"),
            discord.SelectOption(label="AARP", emoji="✈️"),
            discord.SelectOption(label="GCRP", emoji="🌳"),
            discord.SelectOption(label="TEN ROLEPLAY", emoji="🔟"),
            discord.SelectOption(label="CPRP", emoji="💎"),
            discord.SelectOption(label="Relative RP", emoji="👪"),
            discord.SelectOption(label="FMRP", emoji="🛡️"),
        ]
        super().__init__(placeholder="Pilih Server Tujuan...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"📍 Server: **{self.values[0]}**. Pilih alur cerita:", 
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
    embed = discord.Embed(title="🌟 TATANG AI PREMIUM", color=0x5865f2)
    embed.add_field(name="Gunakan:", value="`!panelcs` di channel khusus.")
    await ctx.send(embed=embed)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send(f"❌ Gunakan di <#{ALLOWED_CHANNEL_ID}>", delete_after=5)
    
    await ctx.send("🚀 **Silakan pilih server untuk membuat CS:**", view=ServerSelectView())

if TOKEN:
    bot.run(TOKEN)
