import discord
from discord.ext import commands
import os
import io
import re

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
ALLOWED_CHANNEL_ID = 1471935338065694875 

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="CS Generator | Manual Mode"))
        print(f"✅ Bot Siap! Login sebagai: {self.user}")

bot = TatangBot()

# ================= MODAL FORM (Sesuai Gambar) =================
class CSModal(discord.ui.Modal, title="Form Character Story (1/2)"):
    nama_ic = discord.ui.TextInput(label="Nama Lengkap Karakter (IC)", placeholder="Contoh: John_Washington", required=True)
    level = discord.ui.TextInput(label="Level Karakter", placeholder="Contoh: 5", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin", placeholder="Laki-laki / Perempuan", required=True)
    kota = discord.ui.TextInput(label="Kota Asal", placeholder="Contoh: Chicago", required=True)
    cerita = discord.ui.TextInput(
        label="Tulis Cerita Karakter", 
        style=discord.TextStyle.paragraph, 
        placeholder="Tuliskan minimal 300-500 kata di sini...",
        min_length=100,
        required=True
    )

    def __init__(self, server, side):
        super().__init__()
        self.server = server
        self.side = side

    async def on_submit(self, interaction: discord.Interaction):
        # Membuat file .txt secara manual dari input user
        isi_cerita = (
            f"--- CHARACTER STORY ---\n"
            f"Server: {self.server}\n"
            f"Alur: {self.side}\n"
            f"Nama IC: {self.nama_ic.value}\n"
            f"Level: {self.level.value}\n"
            f"Gender: {self.gender.value}\n"
            f"Kota: {self.kota.value}\n"
            f"------------------------\n\n"
            f"{self.cerita.value}"
        )
        
        file_data = io.BytesIO(isi_cerita.encode('utf-8'))
        clean_name = re.sub(r'[^\w\s-]', '', self.nama_ic.value).strip().replace(' ', '_')
        
        # Embed Sukses (Warna Hijau sesuai Gambar)
        embed = discord.Embed(
            title="✅ Character Story Selesai!",
            description=f"Karakter: **{self.nama_ic.value}** | Server: **{self.server}**\n\n**{self.server}**\nFile .txt siap diunduh.",
            color=0x2ecc71
        )
        
        await interaction.response.send_message(
            embed=embed, 
            file=discord.File(file_data, filename=f"CS_{clean_name}.txt"),
            ephemeral=True
        )

# ================= PILIHAN ALUR (Sesuai Gambar) =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="😇 😇 Sisi Baik (Goodside)", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="😈 😈 Sisi Jahat (Badside)", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))

# ================= SELECTION SERVER =================
class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="JGRP", emoji="🎮"),
            discord.SelectOption(label="SSRP", emoji="🇺🇸"),
            discord.SelectOption(label="APRP", emoji="✈️"),
            discord.SelectOption(label="CPRP", emoji="💎"),
        ]
        super().__init__(placeholder="Pilih Server Tujuanmu:", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Pilih Alur cerita untuk karaktermu:", 
            view=CSAlurView(self.values[0]), 
            ephemeral=True
        )

# ================= COMMANDS =================
@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID: return
    
    view = discord.ui.View()
    view.add_item(ServerSelect())
    
    embed = discord.Embed(
        title="⭐ Selamat Datang!",
        description="Pilih Server Tujuanmu:",
        color=0x5865f2
    )
    await ctx.send(embed=embed, view=view)

if TOKEN:
    bot.run(TOKEN)
