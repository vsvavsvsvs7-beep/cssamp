import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

ALLOWED_CHANNEL_ID = 1471935338065694875
REPORT_CHANNEL_ID = 1471935338065694875  # ganti kalau mau channel report beda

# ================= BOT =================

class CSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def on_ready(self):
        print(f"✅ Bot aktif sebagai {self.user}")
        await self.change_presence(activity=discord.Game(name="CS Generator"))

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
            placeholder="Contoh: Laki-laki",
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

        self.talent = discord.ui.TextInput(
            label="Bakat / Keahlian",
            placeholder="Contoh: Menembak, Mengemudi",
            required=True
        )

        self.detail = discord.ui.TextInput(
            label="Detail Tambahan",
            placeholder="Contoh: Mantan tentara",
            style=discord.TextStyle.paragraph,
            required=False
        )

        self.add_item(self.nama)
        self.add_item(self.level)
        self.add_item(self.gender)
        self.add_item(self.ttl)
        self.add_item(self.kota)
        self.add_item(self.talent)
        self.add_item(self.detail)

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="✅ Character Story Berhasil Dibuat",
            color=0x00ff00
        )

        embed.add_field(name="Nama", value=self.nama.value, inline=False)
        embed.add_field(name="Level", value=self.level.value, inline=True)
        embed.add_field(name="Gender", value=self.gender.value, inline=True)
        embed.add_field(name="Tanggal Lahir", value=self.ttl.value, inline=False)
        embed.add_field(name="Kota", value=self.kota.value, inline=False)
        embed.add_field(name="Bakat", value=self.talent.value, inline=False)

        if self.detail.value:
            embed.add_field(name="Detail", value=self.detail.value, inline=False)

        embed.add_field(name="Server", value=self.server)
        embed.add_field(name="Side", value=self.side)

        embed.set_footer(text=f"Dibuat oleh {interaction.user}")

        await interaction.response.send_message(embed=embed)

# ================= VIEW =================

class SideView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Good Side", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Good Side"))

    @discord.ui.button(label="Bad Side", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Bad Side"))

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="JGRP"),
            discord.SelectOption(label="SSRP"),
            discord.SelectOption(label="APRP"),
            discord.SelectOption(label="CPRP"),
        ]

        super().__init__(
            placeholder="Pilih Server",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Pilih Side:",
            view=SideView(self.values[0])
        )

class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

# ================= COMMAND =================

@bot.command()
async def menu(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="📋 Menu Character Story",
        description="Pilih server untuk membuat Character Story",
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=MenuView())

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📖 Help Menu",
        color=0x5865f2
    )

    embed.add_field(name="!menu", value="Buka menu CS", inline=False)
    embed.add_field(name="!ping", value="Cek status bot", inline=False)
    embed.add_field(name="!report", value="Report masalah", inline=False)
    embed.add_field(name="!help", value="Lihat help", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! `{latency}ms`")

@bot.command()
async def report(ctx, *, message):

    channel = bot.get_channel(REPORT_CHANNEL_ID)

    embed = discord.Embed(
        title="📢 Report Baru",
        description=message,
        color=0xff0000
    )

    embed.set_footer(text=f"Dari {ctx.author}")

    await channel.send(embed=embed)

    await ctx.send("✅ Report berhasil dikirim")

# ================= RUN =================

bot.run(TOKEN)
