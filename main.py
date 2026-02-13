import discord
from discord.ext import commands
import google.generativeai as genai
import os
import io
import datetime
import re

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
# Pakai Key Gemini kamu yang lama (Gratis)
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE" 
ALLOWED_CHANNEL_ID = 1471935338065694875 

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | CS Maker Free"))
        print(f"✅ Bot Online: {self.user}")

bot = TatangBot()

# ================= MODAL FORM =================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    identitas = discord.ui.TextInput(label="Nama IC & Level", placeholder="Contoh: Dika_Ganteng | Level 5", required=True)
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
        # Pakai defer biar gak 'Something went wrong'
        await interaction.response.defer(ephemeral=True)
        
        prompt = (
            f"Buatkan Character Story GTA SAMP untuk server {self.server}.\n"
            f"Alur: {self.side}\n"
            f"Identitas: {self.identitas.value}\n"
            f"Biodata: {self.biodata.value}\n"
            f"Latar Belakang: {self.detail.value}\n\n"
            "WAJIB: Minimal 500 kata, BBCode forum lengkap ([center], [justify], [b]). "
            "Gunakan Bahasa Indonesia yang baku dan kreatif."
        )
        
        try:
            response = ai_model.generate_content(prompt)
            hasil_cerita = response.text
            
            # Buat file .txt
            isi_file = (
                f"--- INSTRUKSI ---\nServer: {self.server}\nNama: {self.identitas.value}\n"
                f"Copy teks di bawah ini ke forum:\n------------------\n\n{hasil_cerita}"
            )
            
            file_data = io.BytesIO(isi_file.encode('utf-8'))
            clean_name = re.sub(r'[^\w\s-]', '', self.identitas.value).strip().replace(' ', '_')
            
            embed = discord.Embed(
                title="✅ Character Story Selesai!",
                description=f"Sukses membuat cerita untuk **{self.identitas.value}**.\nFile .txt siap diunduh di bawah.",
                color=0x00ff00
            )
            
            await interaction.followup.send(
                embed=embed, 
                file=discord.File(file_data, filename=f"CS_{clean_name}.txt"),
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

# ================= PILIHAN SERVER =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik (Good)", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat (Bad)", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=s) for s in ["JGRP", "SSRP", "Virtual RP", "AARP", "GCRP", "CPRP", "FMRP"]]
        super().__init__(placeholder="Pilih Server...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"📍 Server: **{self.values[0]}**", view=CSAlurView(self.values[0]), ephemeral=True)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID: return
    view = discord.ui.View(); view.add_item(ServerSelect())
    await ctx.send("🚀 **Generator CS Otomatis**", view=view)

if TOKEN:
    bot.run(TOKEN)
