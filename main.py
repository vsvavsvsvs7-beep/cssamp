import discord
from discord.ext import commands
from openai import OpenAI
import os
import io
import datetime
import re

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
# API Key ChatGPT yang kamu berikan
OPENAI_API_KEY = "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"
ALLOWED_CHANNEL_ID = 1471935338065694875 

client = OpenAI(api_key=OPENAI_API_KEY)

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | ChatGPT CS"))
        print(f"✅ Bot Berhasil Online!")

bot = TatangBot()

# ================= MODAL FORM (CHATGPT) =================
class CSModal(discord.ui.Modal, title="Form Character Story (ChatGPT)"):
    identitas = discord.ui.TextInput(label="Nama IC & Level", placeholder="Contoh: Dika_Ganteng | Level 5", required=True)
    biodata = discord.ui.TextInput(label="Gender & Kota Asal", placeholder="Contoh: Laki-laki | Chicago", required=True)
    detail = discord.ui.TextInput(
        label="Bakat & Masa Lalu", 
        style=discord.TextStyle.paragraph, 
        placeholder="Tuliskan masa lalu dan tujuan hidup karaktermu secara mendetail...",
        max_length=2000,
        required=True
    )

    def __init__(self, server, side):
        super().__init__()
        self.server, self.side = server, side

    async def on_submit(self, interaction: discord.Interaction):
        # Gunakan defer untuk menghindari 'Something went wrong'
        await interaction.response.defer(ephemeral=True)
        
        prompt = (
            f"Buatkan Character Story GTA SAMP untuk server {self.server}.\n"
            f"Alur: {self.side}\n"
            f"Identitas: {self.identitas.value}\n"
            f"Biodata: {self.biodata.value}\n"
            f"Latar Belakang: {self.detail.value}\n\n"
            "WAJIB: Minimal 500 kata, BBCode forum lengkap ([center], [justify], [b]). "
            "Gunakan bahasa Indonesia yang emosional dan mendalam."
        )
        
        try:
            # Memanggil ChatGPT
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Kamu adalah penulis CS GTA SAMP profesional. Selalu sertakan instruksi copy-paste di akhir."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            hasil_cerita = completion.choices[0].message.content
            
            # Buat isi file dengan instruksi
            isi_teks = (
                f"--- INSTRUKSI COPY-PASTE CS ---\n"
                f"Server: {self.server}\n"
                f"Karakter: {self.identitas.value}\n"
                f"--------------------------------\n\n"
                f"{hasil_cerita}"
            )
            
            file_data = io.BytesIO(isi_teks.encode('utf-8'))
            clean_name = re.sub(r'[^\w\s-]', '', self.identitas.value).strip().replace(' ', '_')
            
            embed = discord.Embed(
                title="✅ CS ChatGPT Selesai!",
                description=f"Berhasil membuat cerita untuk **{self.identitas.value}**.\nDownload file di bawah.",
                color=0x10a37f,
                timestamp=datetime.datetime.utcnow()
            )
            
            await interaction.followup.send(
                embed=embed, 
                file=discord.File(file_data, filename=f"CS_{clean_name}.txt"),
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error ChatGPT: {str(e)}", ephemeral=True)

# ================= UI & COMMANDS =================
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
            f"📍 Server: **{self.values[0]}**. Pilih alur:", 
            view=CSAlurView(self.values[0]), 
            ephemeral=True
        )

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID: return
    view = discord.ui.View(); view.add_item(ServerSelect())
    await ctx.send("🚀 **Character Story Generator (ChatGPT)**", view=view)

@bot.command()
async def menu(ctx):
    await ctx.send("🌟 Gunakan `!panelcs` untuk membuat cerita otomatis.")

if TOKEN:
    bot.run(TOKEN)
