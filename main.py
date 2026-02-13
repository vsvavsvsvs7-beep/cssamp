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
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def on_ready(self):
        print(f"Bot aktif sebagai {self.user}")

bot = CSBot()

# ================= MODAL =================

class CSModal(discord.ui.Modal):

    def __init__(self, server, side):
        super().__init__(title="Form Character Story")
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

        embed = discord.Embed(
            title="Character Story Berhasil Dibuat",
            description=f"Server: {self.server}\nSide: {self.side}",
            color=0x2ecc71
        )

        embed.add_field(name="Nama", value=self.nama.value, inline=False)
        embed.add_field(name="Level", value=self.level.value, inline=True)
        embed.add_field(name="Gender", value=self.gender.value, inline=True)
        embed.add_field(name="Tanggal Lahir", value=self.ttl.value, inline=False)
        embed.add_field(name="Kota Asal", value=self.kota.value, inline=False)

        embed.set_footer(text=f"Dibuat oleh {interaction.user}")

        await interaction.response.send_message(embed=embed)

# ================= VIEW PILIH SIDE =================

class SideView(discord.ui.View):
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
            discord.SelectOption(
                label="JGRP",
                description="Buat Character Story untuk server JGRP"
            ),
            discord.SelectOption(
                label="SSRP",
                description="Buat Character Story untuk server State Side RP"
            ),
            discord.SelectOption(
                label="APRP",
                description="Buat Character Story untuk server Asia Pacific RP"
            ),
            discord.SelectOption(
                label="CPRP",
                description="Buat Character Story untuk server Crystal Pride RP"
            ),
        ]

        super().__init__(
            placeholder="Pilih Server Tujuan...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Pilih alur karakter:",
            view=SideView(self.values[0]),
            ephemeral=True
        )

# ================= COMMAND PANELCS =================

@bot.command()
async def panelcs(ctx):

    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    view = discord.ui.View(timeout=None)
    view.add_item(ServerSelect())

    embed = discord.Embed(
        title="Form Character Story",
        description="Silakan pilih server tujuan untuk membuat Character Story.",
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=view)

# ================= RUN =================

bot.run(TOKEN)
