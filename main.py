import discord
from discord.ext import commands
import os
import io
import re
import random

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
ALLOWED_CHANNEL_ID = 1471935338065694875  # Ganti jika perlu

# ================= BOT CLASS =================
class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="CS Generator | Auto Mode"))
        print(f"✅ Bot Siap! Login sebagai: {self.user}")

bot = TatangBot()

# ================= MODAL =================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    nama_ic = discord.ui.TextInput(label="Nama Lengkap Karakter (IC)", required=True)
    level = discord.ui.TextInput(label="Level Karakter", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin", required=True)
    kota = discord.ui.TextInput(label="Kota Asal", required=True)

    def __init__(self, server, side):
        super().__init__()
        self.server = server
        self.side = side

    def generate_story(self, nama, gender, kota, level):
        sifat_good = [
            "pribadi yang rendah hati dan pekerja keras",
            "sosok yang peduli terhadap sesama",
            "orang yang selalu menjunjung tinggi kejujuran"
        ]

        sifat_bad = [
            "pribadi yang ambisius dan penuh intrik",
            "sosok yang tumbuh di lingkungan keras",
            "orang yang tidak segan melakukan apapun demi tujuannya"
        ]

        konflik_good = [
            "Ia sering membantu warga sekitar dan dikenal sebagai pribadi yang bisa dipercaya.",
            "Sejak kecil ia bercita-cita menjadi seseorang yang sukses dengan cara yang benar.",
            "Ia percaya bahwa kerja keras akan selalu membuahkan hasil."
        ]

        konflik_bad = [
            "Lingkungan keras membentuk mentalnya menjadi kuat dan penuh strategi.",
            "Ia belajar bahwa dunia tidak selalu adil dan kadang perlu cara ekstrem untuk bertahan.",
            "Ambisinya membuatnya berani mengambil risiko besar."
        ]

        if self.side == "Goodside":
            sifat = random.choice(sifat_good)
            konflik = random.choice(konflik_good)
        else:
            sifat = random.choice(sifat_bad)
            konflik = random.choice(konflik_bad)

        cerita = f"""
{nama} adalah seorang {gender} yang berasal dari kota {kota}. 
Sejak kecil, ia dikenal sebagai {sifat}. Kehidupan yang dijalaninya tidak selalu mudah, 
namun semua tantangan tersebut membentuk dirinya menjadi pribadi yang lebih kuat.

Kini di level {level} pada server {self.server}, {nama} memulai perjalanan barunya. 
{konflik}

Dengan tekad dan ambisi yang ia miliki, {nama} berusaha membangun nama dan reputasi di kota tersebut. 
Setiap langkah yang diambil akan menentukan masa depannya. 

Apakah ia akan dikenang sebagai sosok yang dihormati, atau menjadi figur yang ditakuti, 
semuanya bergantung pada pilihan yang ia ambil ke depannya.

Perjalanan ini baru saja dimulai, dan kisah hidupnya masih panjang untuk dituliskan...
"""
        return cerita

    async def on_submit(self, interaction: discord.Interaction):
        nama = self.nama_ic.value
        level = self.level.value
        gender = self.gender.value
        kota = self.kota.value

        generated_story = self.generate_story(nama, gender, kota, level)

        isi_cerita = (
            f"--- CHARACTER STORY ---\n"
            f"Server: {self.server}\n"
            f"Alur: {self.side}\n"
            f"Nama IC: {nama}\n"
            f"Level: {level}\n"
            f"Gender: {gender}\n"
            f"Kota: {kota}\n"
            f"------------------------\n\n"
            f"{generated_story}"
        )

        file_data = io.BytesIO(isi_cerita.encode('utf-8'))
        clean_name = re.sub(r'[^\w\s-]', '', nama).strip().replace(' ', '_')

        embed = discord.Embed(
            title="✅ Character Story Berhasil Digenerate!",
            description=f"Karakter: **{nama}** | Server: **{self.server}**\n\nFile .txt siap diunduh.",
            color=0x2ecc71
        )

        await interaction.response.send_message(
            embed=embed,
            file=discord.File(file_data, filename=f"CS_{clean_name}.txt"),
            ephemeral=True
        )

# ================= VIEW ALUR =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="😇 Sisi Baik (Goodside)", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="😈 Sisi Jahat (Badside)", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))

# ================= SELECT SERVER =================
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
            "Pilih alur cerita karakter kamu:",
            view=CSAlurView(self.values[0]),
            ephemeral=True
        )

# ================= COMMAND =================
@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    
    view = discord.ui.View()
    view.add_item(ServerSelect())

    embed = discord.Embed(
        title="⭐ Selamat Datang di CS Generator",
        description="Silakan pilih server tujuanmu:",
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=view)

# ================= RUN =================
if TOKEN:
    bot.run(TOKEN)
else:
    print("TOKEN tidak ditemukan di environment variable.")
