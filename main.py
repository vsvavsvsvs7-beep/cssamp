import discord
from discord.ext import commands
import google.generativeai as genai
import os
import io
import datetime
import re

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE"
ALLOWED_CHANNEL_ID = 1471935338065694875 

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash') # Perbaikan Model Name

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | Premium CS AI"))
        print(f"✅ Bot Siap! Login sebagai: {self.user}")

bot = TatangBot()

# ================= MODAL FORM =================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    identitas = discord.ui.TextInput(label="Nama IC & Level", placeholder="Contoh: John_Doe | Level 5", required=True)
    biodata = discord.ui.TextInput(label="Gender & Kota Asal", placeholder="Contoh: Laki-laki | Chicago", required=True)
    detail = discord.ui.TextInput(
        label="Bakat & Masa Lalu", 
        style=discord.TextStyle.paragraph, 
        placeholder="Ceritakan keahlian dan latar belakang karaktermu...",
        max_length=2000,
        required=True
    )

    def __init__(self, server, side):
        super().__init__()
        self.server = server
        self.side = side

    async def on_submit(self, interaction: discord.Interaction):
        # Defer agar tidak 'Something went wrong'
        await interaction.response.defer(ephemeral=True)
        
        prompt = (
            f"Buatkan Character Story GTA SAMP panjang untuk server {self.server}.\n"
            f"Alur: {self.side}\n"
            f"Identitas: {self.identitas.value}\n"
            f"Biodata: {self.biodata.value}\n"
            f"Latar Belakang: {self.detail.value}\n\n"
            "WAJIB: Minimal 500 kata, bahasa Indonesia baku, format BBCode Forum lengkap ([center], [justify], [b])."
        )
        
        try:
            response = ai_model.generate_content(prompt)
            hasil_cerita = response.text
            
            # Tambahkan instruksi di dalam teks file
            isi_file = (
                f"--- INSTRUKSI Karakter Story ---\n"
                f"Server: {self.server}\n"
                f"Sisi: {self.side}\n"
                f"Cara Pakai: Copy semua teks BBCode di bawah ini dan paste ke formulir forum.\n"
                f"---------------------------------\n\n"
                f"{hasil_cerita}"
            )
            
            file_data = io.BytesIO(isi_file.encode('utf-8'))
            # Bersihkan nama file dari karakter ilegal
            clean_name = re.sub(r'[^\w\s-]', '', self.identitas.value).strip().replace(' ', '_')
            nama_file = f"CS_{clean_name}.txt"
            
            embed = discord.Embed(
                title="✅ CS Berhasil Dibuat!",
                description=f"Karakter: **{self.identitas.value}**\nServer: **{self.server}**\n\n*File panduan & teks sudah siap di bawah.*",
                color=0x2ecc71,
                timestamp=datetime.datetime.utcnow()
            )
            
            await interaction.followup.send(
                embed=embed, 
                file=discord.File(file_data, filename=nama_file),
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Kesalahan AI: {str(e)}", ephemeral=True)

# ================= SELECTION UI =================
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
        super().__init__(placeholder="Pilih Server...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"📍 Server: **{self.values[0]}**. Pilih alur cerita:", 
            view=CSAlurView(self.values[0]), 
            ephemeral=True
        )

# ================= COMMANDS =================
@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send(f"❌ Gunakan di <#{ALLOWED_CHANNEL_ID}>", delete_after=5)
    
    view = discord.ui.View()
    view.add_item(ServerSelect())
    await ctx.send("🚀 **Pilih Server untuk membuat Character Story:**", view=view)

@bot.command()
async def menu(ctx):
    await ctx.send("🌟 Ketik `!panelcs` untuk memulai pembuatan CS.")

if TOKEN:
    bot.run(TOKEN)
