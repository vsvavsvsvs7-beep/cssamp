import discord
from discord.ext import commands
import os
import random

# ================= KONFIG =================

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875  # ganti sesuai channel kamu

# ================= BOT =================

class CSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def on_ready(self):
        print(f"Login sebagai {self.user}")
        await self.change_presence(
            activity=discord.Game(name="Character Story Generator")
        )

bot = CSBot()

# ================= MODAL =================

class CSModal(discord.ui.Modal, title="Form Character Story"):

    nama = discord.ui.TextInput(
        label="Nama Lengkap Karakter (IC)",
        placeholder="Contoh: John Washington, Kenji Tanaka",
        required=True,
        max_length=50
    )

    level = discord.ui.TextInput(
        label="Level Karakter",
        placeholder="Contoh: 1",
        required=True,
        max_length=5
    )

    gender = discord.ui.TextInput(
        label="Jenis Kelamin",
        placeholder="Contoh: Laki-laki / Perempuan",
        required=True,
        max_length=20
    )

    tanggal_lahir = discord.ui.TextInput(
        label="Tanggal Lahir",
        placeholder="Contoh: 17 Agustus 1995",
        required=True,
        max_length=30
    )

    kota = discord.ui.TextInput(
        label="Kota Asal",
        placeholder="Contoh: Los Santos, San Fierro, Las Venturas",
        required=True,
        max_length=50
    )

    def __init__(self, side):
        super().__init__()
        self.side = side

    # ================= STORY GENERATOR =================

    def generate_story(self, nama, gender, kota, level, tanggal):

        intro_list = [
            f"{nama} lahir pada tanggal {tanggal} dan dibesarkan di kota {kota}, sebuah kota yang penuh dengan dinamika kehidupan.",
            f"Sejak kecil, {nama} telah mengenal kerasnya kehidupan di lingkungan tempat ia tumbuh.",
            f"Sebagai seorang {gender}, ia harus belajar memahami dunia lebih cepat dibandingkan kebanyakan orang."
        ]

        masa_kecil_list = [
            f"Masa kecilnya dipenuhi dengan berbagai pengalaman yang membentuk karakter dan mentalnya.",
            f"Ia sering menyaksikan berbagai kejadian yang mengajarkannya arti bertahan hidup.",
            f"Setiap tantangan yang dihadapinya membuat dirinya semakin kuat dan matang."
        ]

        remaja_list = [
            f"Memasuki usia remaja, {nama} mulai memahami bagaimana dunia sebenarnya bekerja.",
            f"Ia bertemu banyak orang dengan latar belakang berbeda yang memberikan pelajaran hidup berharga.",
            f"Pengalaman tersebut membentuk cara berpikir dan pandangannya terhadap kehidupan."
        ]

        goodside_list = [
            f"{nama} memilih untuk berjalan di jalan yang benar.",
            f"Ia percaya bahwa kerja keras dan kejujuran adalah kunci kesuksesan.",
            f"Ia berusaha menjadi sosok yang dihormati dan dipercaya oleh orang lain.",
            f"Ia ingin membangun masa depan yang bersih dan penuh kehormatan."
        ]

        badside_list = [
            f"{nama} menyadari bahwa dunia tidak selalu adil.",
            f"Ia memilih jalan yang gelap untuk bertahan hidup.",
            f"Ia tidak ragu melakukan apa pun demi mencapai tujuannya.",
            f"Ia membangun reputasi sebagai sosok yang ditakuti."
        ]

        sekarang_list = [
            f"Sekarang di level {level}, {nama} memulai babak baru dalam hidupnya.",
            f"Kota {kota} menjadi saksi perjalanan barunya.",
            f"Setiap keputusan yang ia ambil akan menentukan masa depannya.",
            f"Kisah hidupnya masih terus berjalan dan belum mencapai akhir."
        ]

        intro = random.choice(intro_list)
        masa_kecil = random.choice(masa_kecil_list)
        remaja = random.choice(remaja_list)

        if self.side == "Goodside":
            jalan = random.choice(goodside_list)
        else:
            jalan = random.choice(badside_list)

        sekarang = random.choice(sekarang_list)

        story = (
            f"{intro}\n\n"
            f"{masa_kecil}\n\n"
            f"{remaja}\n\n"
            f"{jalan}\n\n"
            f"{sekarang}\n\n"
            f"Perjalanan hidup {nama} masih panjang, dan masa depannya akan ditentukan oleh setiap langkah yang ia ambil."
        )

        return story

    # ================= SUBMIT =================

    async def on_submit(self, interaction: discord.Interaction):

        nama = self.nama.value
        level = self.level.value
        gender = self.gender.value
        tanggal = self.tanggal_lahir.value
        kota = self.kota.value

        story = self.generate_story(
            nama,
            gender,
            kota,
            level,
            tanggal
        )

        # embed hasil
        embed = discord.Embed(
            title="Character Story Berhasil Dibuat",
            color=0x2ecc71
        )

        embed.add_field(name="Side", value=self.side, inline=False)
        embed.add_field(name="Nama", value=nama, inline=False)
        embed.add_field(name="Level", value=level, inline=False)
        embed.add_field(name="Jenis Kelamin", value=gender, inline=False)
        embed.add_field(name="Tanggal Lahir", value=tanggal, inline=False)
        embed.add_field(name="Kota Asal", value=kota, inline=False)

        embed.add_field(
            name="Character Story",
            value=story[:1024],
            inline=False
        )

        embed.set_footer(
            text=f"Dibuat oleh {interaction.user}"
        )

        await interaction.response.send_message(
            "Character Story berhasil dibuat.",
            ephemeral=True
        )

        await interaction.channel.send(embed=embed)

# ================= VIEW =================

class CSView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Sisi Baik (Goodside)",
        style=discord.ButtonStyle.success
    )
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CSModal("Goodside")
        )

    @discord.ui.button(
        label="Sisi Jahat (Badside)",
        style=discord.ButtonStyle.danger
    )
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CSModal("Badside")
        )

# ================= COMMAND =================

@bot.command()
async def panelcs(ctx):

    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="Character Story Generator",
        description=(
            "Buat Character Story secara otomatis.\n\n"
            "Klik tombol di bawah untuk memilih alur karakter.\n\n"
            "Goodside = karakter baik\n"
            "Badside = karakter jahat"
        ),
        color=0x5865f2
    )

    await ctx.send(
        embed=embed,
        view=CSView()
    )

# ================= RUN =================

if not TOKEN:
    print("TOKEN tidak ditemukan di environment variable.")
else:
    bot.run(TOKEN)
