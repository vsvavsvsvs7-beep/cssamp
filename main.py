import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875

# ================= BOT =================

class CSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f"Bot aktif sebagai {self.user}")
        await self.change_presence(
            activity=discord.Game(name="Character Story Generator")
        )

bot = CSBot()

# ================= MODAL 2 =================

class CSModalPart2(discord.ui.Modal):

    def __init__(self, data):
        super().__init__(title=f"Detail Cerita ({data['side']}) (2/2)")
        self.data = data

        self.skill = discord.ui.TextInput(
            label="Bakat/Keahlian Dominan",
            placeholder="Contoh: Penembak jitu, mekanik, hacker",
            required=True,
            max_length=200
        )

        self.etnis = discord.ui.TextInput(
            label="Kultur/Etnis (Opsional)",
            placeholder="Contoh: American, Japanese",
            required=False,
            max_length=200
        )

        self.detail = discord.ui.TextInput(
            label="Cerita Lengkap Karakter",
            placeholder="Ceritakan masa kecil, konflik, tujuan hidup, dll",
            style=discord.TextStyle.paragraph,
            required=True,
            min_length=200,
            max_length=4000
        )

        self.add_item(self.skill)
        self.add_item(self.etnis)
        self.add_item(self.detail)

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Character Story Berhasil Dibuat",
            color=0x2ecc71
        )

        embed.add_field(name="Server", value=self.data["server"], inline=True)
        embed.add_field(name="Alur", value=self.data["side"], inline=True)

        embed.add_field(name="Nama IC", value=self.data["nama"], inline=False)

        embed.add_field(
            name="Info Karakter",
            value=(
                f"Level: {self.data['level']}\n"
                f"Gender: {self.data['gender']}\n"
                f"Tanggal Lahir: {self.data['ttl']}\n"
                f"Kota Asal: {self.data['kota']}"
            ),
            inline=False
        )

        embed.add_field(name="Keahlian", value=self.skill.value, inline=False)

        if self.etnis.value:
            embed.add_field(name="Etnis", value=self.etnis.value, inline=False)

        embed.add_field(name="Cerita", value=self.detail.value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# ================= VIEW LANJUT =================

class ContinueView(discord.ui.View):
    def __init__(self, data):
        super().__init__(timeout=300)
        self.data = data

    @discord.ui.button(label="Lanjut ke Tahap 2", style=discord.ButtonStyle.primary)
    async def lanjut(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModalPart2(self.data))

# ================= MODAL 1 =================

class CSModalPart1(discord.ui.Modal):

    def __init__(self, server, side):
        super().__init__(title="Form Character Story (1/2)")
        self.server = server
        self.side = side

        self.nama = discord.ui.TextInput(
            label="Nama Lengkap Karakter (IC)",
            placeholder="Contoh: John Washington",
            required=True
        )

        self.level = discord.ui.TextInput(
            label="Level Karakter",
            placeholder="Contoh: 1",
            required=True
        )

        self.gender = discord.ui.TextInput(
            label="Jenis Kelamin",
            placeholder="Contoh: Laki-laki / Perempuan",
            required=True
        )

        self.ttl = discord.ui.TextInput(
            label="Tanggal Lahir",
            placeholder="Contoh: 17 Agustus 1995",
            required=True
        )

        self.kota = discord.ui.TextInput(
            label="Kota Asal",
            placeholder="Contoh: Chicago",
            required=True
        )

        self.add_item(self.nama)
        self.add_item(self.level)
        self.add_item(self.gender)
        self.add_item(self.ttl)
        self.add_item(self.kota)

    async def on_submit(self, interaction: discord.Interaction):

        data = {
            "server": self.server,
            "side": self.side,
            "nama": self.nama.value,
            "level": self.level.value,
            "gender": self.gender.value,
            "ttl": self.ttl.value,
            "kota": self.kota.value
        }

        view = ContinueView(data)

        await interaction.response.send_message(
            "Data tahap 1 berhasil disimpan.\nKlik tombol di bawah untuk lanjut.",
            view=view,
            ephemeral=True
        )

# ================= VIEW PILIH ALUR =================

class SideView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik (Goodside)", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModalPart1(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat (Badside)", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModalPart1(self.server, "Badside"))

# ================= SELECT SERVER =================

class ServerSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="SSRP", description="State Side RP"),
            discord.SelectOption(label="Virtual RP", description="Virtual RP"),
            discord.SelectOption(label="AARP", description="Air Asia RP"),
            discord.SelectOption(label="GCRP", description="Grand Country RP"),
            discord.SelectOption(label="TEN ROLEPLAY", description="10RP"),
            discord.SelectOption(label="CPRP", description="Crystal Pride RP"),
            discord.SelectOption(label="Relative RP", description="Relative RP"),
            discord.SelectOption(label="JGRP", description="JGRP"),
            discord.SelectOption(label="FMRP", description="Famerlone RP"),
        ]

        super().__init__(
            placeholder="Pilih server tujuan...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Pilih alur karakter:",
            view=SideView(self.values[0]),
            ephemeral=True
        )

# ================= COMMAND =================

@bot.command()
async def panelcs(ctx):

    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    view = discord.ui.View(timeout=None)
    view.add_item(ServerSelect())

    embed = discord.Embed(
        title="Form Character Story",
        description="Pilih server untuk membuat Character Story",
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=view)

# ================= RUN =================

bot.run(TOKEN)
