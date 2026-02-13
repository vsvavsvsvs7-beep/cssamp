import discord
from discord.ext import commands
from openai import OpenAI
os
import io
import datetime
import re

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
# Gunakan API Key ChatGPT kamu di sini
OPENAI_API_KEY = "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"
ALLOWED_CHANNEL_ID = 1471935338065694875 

# Inisialisasi Client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | ChatGPT Powered"))
        print(f"✅ Bot Online (ChatGPT Mode): {self.user}")

bot = TatangBot()

# ================= MODAL FORM =================
class CSModal(discord.ui.Modal, title="Form Character Story (ChatGPT)"):
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
        self.server, self.side = server, side

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        prompt = (
            f"Buatkan Character Story GTA SAMP untuk server {self.server}.\n"
            f"Alur: {self.side}\n"
            f"Identitas: {self.identitas.value}\n"
            f"Biodata: {self.biodata.value}\n"
            f"Latar Belakang: {self.detail.value}\n\n"
            "WAJIB: Minimal 500 kata, BBCode forum lengkap ([center], [justify], [b])."
        )
        
        try:
            # Pemanggilan API ChatGPT (GPT-3.5-Turbo atau GPT-4)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Kamu adalah penulis Character Story GTA SAMP profesional."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            hasil_cerita = response.choices[0].message.content
            
            # Tambahkan instruksi di file .txt
            isi_file = f"--- INSTRUKSI COPY-PASTE ---\nServer: {self.server}\nSisi: {self.side}\n---------------------------\n\n{hasil_cerita}"
            file_data = io.BytesIO(isi_file.encode('utf-8'))
            clean_name = re.sub(r'[^\w\s-]', '', self.identitas.value).strip().replace(' ', '_')
            
            embed = discord.Embed(
                title="✅ CS ChatGPT Selesai!",
                description=f"Karakter: **{self.identitas.value}**\nFile .txt siap diunduh.",
                color=0x10a37f # Warna hijau khas ChatGPT
            )
            
            await interaction.followup.send(
                embed=embed, 
                file=discord.File(file_data, filename=f"CS_{clean_name}.txt"),
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Kesalahan ChatGPT: {str(e)}", ephemeral=True)

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
        options = [discord.SelectOption(label=s) for s in ["JGRP", "SSRP", "Virtual RP", "AARP", "GCRP", "TEN RP", "CPRP", "Relative RP", "FMRP"]]
        super().__init__(placeholder="Pilih Server...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"📍 Server: **{self.values[0]}**", view=CSAlurView(self.values[0]), ephemeral=True)

# ================= COMMANDS =================
@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID: return
    view = discord.ui.View(); view.add_item(ServerSelect())
    await ctx.send("🚀 **Panel CS ChatGPT**", view=view)

@bot.command()
async def menu(ctx):
    await ctx.send("🌟 Ketik `!panelcs` untuk membuat CS via ChatGPT.")

if TOKEN:
    bot.run(TOKEN)
