import discord
from discord.ext import commands
import os
import random

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875  # ganti jika perlu

# ================= BOT =================
class CSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f"Login sebagai {self.user}")
        await self.change_presence(activity=discord.Game(name="Auto CS Generator"))

bot = CSBot()

# ================= MODAL =================
class CSModal(discord.ui.Modal, title="Form Character Story"):

    nama = discord.ui.TextInput(label="Nama Karakter (IC)", required=True)
    level = discord.ui.TextInput(label="Level Karakter", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin", required=True)
    kota = discord.ui.TextInput(label="Kota Asal", required=True)

    def __init__(self, server, side):
        super().__init__()
        self.server = server
        self.side = side

    def generate_story(self, nama, gender, kota, level):

        intro = (
            f"{nama} lahir dan dibesarkan di kota {kota}. "
            f"Sejak kecil ia telah menghadapi berbagai dinamika kehidupan yang tidak selalu mudah. "
            f"Sebagai seorang {gender}, ia belajar untuk memahami kerasnya realita sejak usia dini. "
        )

        masa_kecil = (
            f"Masa kecilnya dipenuhi dengan pengalaman yang membentuk karakter dan mentalnya. "
            f"Lingkungan tempat ia tumbuh mengajarkannya arti tanggung jawab, keberanian, dan cara bertahan hidup. "
            f"Tak jarang ia harus mengambil keputusan sulit yang menguji kedewasaannya."
        )

        perkembangan = (
            f"Memasuki usia remaja, {nama} mulai memahami bagaimana dunia bekerja. "
            f"Ia bertemu berbagai tipe orang dengan latar belakang berbeda. "
            f"Setiap pertemuan meninggalkan pelajaran berharga yang membentuk pola pikirnya hingga sekarang."
        )

        if self.side == "Goodside":
            konflik = (
                f"Meskipun dihadapkan pada berbagai godaan dan tekanan, {nama} memilih untuk berjalan di jalur yang benar. "
                f"Ia percaya bahwa integritas dan kerja keras adalah fondasi utama dalam membangun masa depan yang cerah. "
                f"Ia berusaha menjadi sosok yang dihormati dan dipercaya oleh orang-orang di sekitarnya."
            )
        else:
            konflik = (
                f"Namun kehidupan tidak selalu memberi pilihan yang mudah. "
                f"{nama} menyadari bahwa untuk bertahan di dunia yang keras, dibutuhkan strategi dan keberanian mengambil risiko. "
                f"Ia tidak ragu untuk melakukan apa pun demi mencapai tujuannya dan membangun kekuatan di lingkungannya."
            )

        masa_sekarang = (
            f"Sekarang di server {self.server} pada level {level}, {nama} memulai perjalanan barunya. "
            f"Kota ini menjadi panggung baru bagi kisah hidupnya. "
            f"Setiap langkah, setiap keputusan, dan setiap relasi yang ia bangun akan menentukan arah masa depannya."
        )

        masa_depan = (
            f"Perjalanan ini masih panjang. "
            f"Apakah {nama} akan dikenal sebagai sosok yang dihormati atau figur yang ditakuti, "
            f"semuanya bergantung pada pilihan yang ia ambil ke depannya. "
            f"Satu hal yang pasti, kisah hidupnya baru saja dimulai dan belum mencapai akhir."
        )

        story = (
            f"{intro}\n\n"
            f"{masa_kecil}\n\n"
            f"{perkembangan}\n\n"
            f"{konflik}\n\n"
            f"{masa_sekarang}\n\n"
            f"{masa_depan}"
        )

        return story

    async def on_submit(self, interaction: discord.Interaction):

        nama = self.nama.value
        level = self.level.value
        gender = self.gender.value
        kota = self.kota.value

        story = self.generate_story(nama, gender, kota, level)

        embed = discord.Embed(
            title="Character Story Berhasil Dibuat",
            color=0x2ecc71
        )

        embed.add_field(name="Server", value=self.server, inline=False)
        embed.add_field(name="Side", value=self.side, inline=False)
        embed.add_field(name="Nama", value=nama, inline=False)
        embed.add_field(name="Level", value=level, inline=False)
        embed.add_field(name="Gender", value=gender, inline=False)
        embed.add_field(name="Kota Asal", value=kota, inline=False)
        embed.add_field(name="Character Story", value=story[:1024], inline=False)

        embed.set_footer(text=f"Dibuat oleh {interaction.user}")

        await interaction.response.send_message("CS berhasil dibuat!", ephemeral=True)
        await interaction.channel.send(embed=embed)

# ================= VIEW =================
class CSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Goodside", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("APRP", "Goodside"))

    @discord.ui.button(label="Badside", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("APRP", "Badside"))

# ================= COMMAND =================
@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="Selamat Datang di CS Generator",
        description="Silakan pilih sisi karakter kamu:",
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=CSView())

# ================= RUN =================
if TOKEN:
    bot.run(TOKEN)
else:
    print("TOKEN tidak ditemukan.")
