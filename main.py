import discord
from discord.ext import commands
import os
import random

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875

# ================= BOT =================
class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="Advanced CS Generator"))
        print(f"Bot aktif sebagai {self.user}")

bot = TatangBot()

# ================= MODAL 2 (DETAIL TAMBAHAN) =================
class CSDetailModal(discord.ui.Modal):
    def __init__(self, data):
        super().__init__(title="Detail Cerita (2/2)")
        self.data = data

        self.skill = discord.ui.TextInput(
            label="Bakat/Keahlian Dominan Karakter",
            required=True
        )
        self.etnis = discord.ui.TextInput(
            label="Kultur/Etnis (Opsional)",
            required=False
        )
        self.detail = discord.ui.TextInput(
            label="Detail Tambahan (Opsional)",
            style=discord.TextStyle.paragraph,
            required=False
        )

        self.add_item(self.skill)
        self.add_item(self.etnis)
        self.add_item(self.detail)

    async def on_submit(self, interaction: discord.Interaction):

        nama = self.data["nama"]
        level = self.data["level"]
        gender = self.data["gender"]
        ttl = self.data["ttl"]
        kota = self.data["kota"]
        server = self.data["server"]
        side = self.data["side"]

        skill = self.skill.value
        etnis = self.etnis.value if self.etnis.value else "Tidak disebutkan"
        detail = self.detail.value if self.detail.value else "Tidak ada detail tambahan"

        sifat_good = [
            "memiliki hati yang tulus dan selalu mengutamakan keadilan",
            "tumbuh sebagai pribadi disiplin dan pekerja keras",
            "percaya bahwa kejujuran adalah pondasi kehidupan"
        ]

        sifat_bad = [
            "dibesarkan dalam lingkungan keras penuh konflik",
            "memiliki mental baja dan penuh perhitungan",
            "tidak mudah percaya kepada siapapun"
        ]

        sifat = random.choice(sifat_good if side == "Goodside" else sifat_bad)

        cerita = f"""
{nama} adalah seorang {gender} yang lahir pada {ttl} di kota {kota}. 
Sejak kecil, ia {sifat}. Kehidupan yang dijalaninya penuh dengan dinamika, 
membentuk kepribadian yang kuat dan berpendirian.

Beranjak dewasa, {nama} mulai menemukan bakat alaminya dalam bidang {skill}. 
Kemampuannya tersebut bukan datang secara instan, melainkan hasil dari latihan, 
pengalaman pahit, serta berbagai kegagalan yang pernah ia alami.

Berasal dari latar belakang etnis/kultur {etnis}, ia membawa nilai-nilai kehidupan 
yang ditanamkan sejak kecil ke dalam setiap keputusan yang ia ambil. 
Hal tersebut menjadikannya sosok yang memiliki prinsip kuat dalam menjalani hidup.

Saat ini, {nama} berada di level {level} dalam server {server}. 
Memasuki dunia baru bukanlah hal yang mudah. Tantangan demi tantangan muncul, 
mengujinya secara mental maupun fisik.

{detail}

Di tengah kerasnya kehidupan kota, {nama} terus melangkah maju. 
Setiap keputusan akan menentukan apakah ia akan dikenal sebagai sosok terhormat 
atau figur yang disegani dan ditakuti.

Kisah hidupnya masih panjang. Semua pilihan kini berada di tangannya.
"""

        embed = discord.Embed(
            title="Character Story Berhasil Dibuat",
            description=f"Karakter: **{nama}**\nServer: **{server}**\nAlur: **{side}**",
            color=0x2ecc71
        )

        embed.add_field(name="Character Story", value=cerita[:1000], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


# ================= MODAL 1 =================
class CSModal(discord.ui.Modal):
    def __init__(self, server, side):
        super().__init__(title="Form Character Story (1/2)")
        self.server = server
        self.side = side

        self.nama = discord.ui.TextInput(label="Nama Lengkap Karakter (IC)", required=True)
        self.level = discord.ui.TextInput(label="Level Karakter", required=True)
        self.gender = discord.ui.TextInput(label="Jenis Kelamin", required=True)
        self.ttl = discord.ui.TextInput(label="Tanggal Lahir", required=True)
        self.kota = discord.ui.TextInput(label="Kota Asal", required=True)

        self.add_item(self.nama)
        self.add_item(self.level)
        self.add_item(self.gender)
        self.add_item(self.ttl)
        self.add_item(self.kota)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "nama": self.nama.value,
            "level": self.level.value,
            "gender": self.gender.value,
            "ttl": self.ttl.value,
            "kota": self.kota.value,
            "server": self.server,
            "side": self.side
        }

        await interaction.response.send_modal(CSDetailModal(data))


# ================= PILIH ALUR =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik (Goodside)", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat (Badside)", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))


# ================= SELECT SERVER =================
class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="SSRP", description="Buat CS untuk server State Side RP."),
            discord.SelectOption(label="Virtual RP", description="Buat CS untuk server Virtual RP."),
            discord.SelectOption(label="AARP", description="Buat CS untuk server Air Asia RP."),
            discord.SelectOption(label="GCRP", description="Buat CS untuk server Grand Country RP."),
            discord.SelectOption(label="TEN ROLEPLAY", description="Buat CS untuk server 10RP."),
            discord.SelectOption(label="CPRP", description="Buat CS untuk server Crystal Pride RP."),
            discord.SelectOption(label="Relative RP", description="Buat CS untuk server Relative RP."),
            discord.SelectOption(label="JGRP", description="Buat CS untuk server JGRP."),
            discord.SelectOption(label="FMRP", description="Buat CS untuk server Famerlone RP.")
        ]
        super().__init__(placeholder="Pilih server tujuan...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Pilih alur cerita untuk karaktermu:",
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
        title="Selamat Datang di Character Story Generator",
        description="Silakan pilih server tujuanmu untuk membuat Character Story.",
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=view)


# ================= RUN =================
if TOKEN:
    bot.run(TOKEN)
else:
    print("TOKEN tidak ditemukan.")
