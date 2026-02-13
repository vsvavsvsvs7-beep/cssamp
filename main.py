import discord
from discord.ext import commands
import google.generativeai as genai
import os
import io
import datetime
import re

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
# Menggunakan API Key Gemini yang gratis
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE" 
ALLOWED_CHANNEL_ID = 1471935338065694875 

# Setup AI dengan penanganan model yang benar
genai.configure(api_key=GEMINI_API_KEY)
# Gunakan nama model langsung tanpa 'models/' jika versi library terbaru
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | CS Maker Free"))
        print(f"✅ Bot Berhasil Online!")

bot = TatangBot()

# ================= MODAL FORM =================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    identitas = discord.ui.TextInput(label="Nama IC & Level", placeholder="Contoh: Dika_Ganteng | Level 5", required=True)
    biodata = discord.ui.TextInput(label="Gender & Kota Asal", placeholder="Contoh: Laki-laki | Chicago", required=True)
    detail = discord.ui.TextInput(
        label="Bakat & Masa Lalu", 
        style=discord.TextStyle.paragraph, 
        placeholder="Tuliskan cerita karaktermu di sini...",
        max_length=2000,
        required=True
    )

    def __init__(self, server, side):
        super().__init__()
        self.server, self.side = server, side

    async def on_submit(self, interaction: discord.Interaction):
        # Gunakan defer agar tidak 'Something went wrong' saat AI berpikir
        await interaction.response.defer(ephemeral=True)
        
        prompt = (
            f"Buatkan Character Story GTA SAMP untuk server {self.server}.\n"
            f"Alur: {self.side}\nIdentitas: {self.identitas.value}\n"
            f"Biodata: {self.biodata.value}\nLatar Belakang: {self.detail.value}\n\n"
            "WAJIB: Minimal 500 kata, gunakan BBCode [center] [justify] [b]. Bahasa Indonesia formal."
        )
        
        try:
            response = ai_model.generate_content(prompt)
            cerita = response.text
            
            # Buat file TXT dengan instruksi di dalamnya
            isi_file = (
                f"--- PANDUAN COPY-PASTE ---\n"
                f"Copy seluruh teks di bawah ini ke forum {self.server}.\n"
                f"---------------------------\n\n{cerita}"
            )
            
            file_data = io.BytesIO(isi_file.encode('utf-8'))
            clean_name = re.sub(r'[^\w\s-]', '', self.identitas.value).strip().replace(' ', '_')
            
            embed = discord.Embed(
                title="✅ Character Story Selesai!",
                description=f"Karakter: **{self.identitas.value}**\nFile .txt siap di bawah.",
                color=0x2ecc71
            )
            
            await interaction.followup.send(
                embed=embed, 
                file=discord.File(file_data, filename=f"CS_{clean_name}.txt"),
                ephemeral=True
            )
            
        except Exception as e:
            # Jika masih 404, coba ganti ke format 'models/gemini-1.5-flash' secara otomatis
            try:
                alt_model = genai.GenerativeModel('models/gemini-1.5-flash')
                response = alt_model.generate_content(prompt)
                # ... (ulangi proses kirim file jika berhasil)
                await interaction.followup.send("✅ Berhasil menggunakan model alternatif.", ephemeral=True)
            except:
                await interaction.followup.send(f"❌ Error AI: {str(e)}", ephemeral=True)

# ================= UI SELECTION =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=s) for s in ["JGRP", "SSRP", "Virtual RP", "AARP", "GCRP", "CPRP"]]
        super().__init__(placeholder="Pilih Server...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"📍 Server: **{self.values[0]}**", view=CSAlurView(self.values[0]), ephemeral=True)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID: return
    view = discord.ui.View(); view.add_item(ServerSelect())
    await ctx.send("🚀 **Character Story Generator**", view=view)

if TOKEN:
    bot.run(TOKEN)
