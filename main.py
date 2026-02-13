import discord
from discord.ext import commands

TOKEN = "ISI_TOKEN_KAMU"
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ================= CONFIG SERVER =================

SERVER_NAME = "APRP"
SERVER_DESCRIPTION = (
    "Asia Pacific Roleplay adalah server roleplay profesional.\n"
    "Server ini menyediakan pengalaman roleplay realistis.\n"
    "Ikuti semua aturan dan nikmati permainan."
)

# ================= DATABASE SEDERHANA =================

character_db = {}

# ================= MENU COMMAND =================

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="MENU BOT CS",
        description=(
            "!createcs - Membuat Character Story\n"
            "!mycs - Melihat Character Story\n"
            "!help - Bantuan\n"
            "!ping - Status bot\n"
            "!report - Kirim laporan"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ================= HELP =================

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="BANTUAN BOT",
        description="Gunakan !createcs untuk membuat CS",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# ================= PING =================

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Ping: {latency} ms")

# ================= REPORT =================

@bot.command()
async def report(ctx, *, text=None):
    if text is None:
        await ctx.send("Tulis laporan setelah command")
        return

    embed = discord.Embed(
        title="REPORT BARU",
        description=text,
        color=discord.Color.red()
    )

    embed.set_footer(text=f"Dari {ctx.author}")
    await ctx.send(embed=embed)

# ================= CREATE CS =================

@bot.command()
async def createcs(ctx):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Masukkan Nama Character:")
    nama = await bot.wait_for("message", check=check)

    await ctx.send("Masukkan Gender:")
    gender = await bot.wait_for("message", check=check)

    await ctx.send("Masukkan Tanggal Lahir:")
    ttl = await bot.wait_for("message", check=check)

    await ctx.send("Masukkan Kota Asal:")
    kota = await bot.wait_for("message", check=check)

    await ctx.send("Masukkan Character Story (CS panjang):")
    story = await bot.wait_for("message", check=check)

    character_db[ctx.author.id] = {
        "nama": nama.content,
        "gender": gender.content,
        "ttl": ttl.content,
        "kota": kota.content,
        "story": story.content,
        "level": 1
    }

    embed = discord.Embed(
        title="Character Story Berhasil Dibuat",
        description=SERVER_DESCRIPTION,
        color=discord.Color.green()
    )

    embed.add_field(name="Server", value=SERVER_NAME, inline=False)
    embed.add_field(name="Nama", value=nama.content, inline=False)
    embed.add_field(name="Level", value="1", inline=False)
    embed.add_field(name="Gender", value=gender.content, inline=False)
    embed.add_field(name="Tanggal Lahir", value=ttl.content, inline=False)
    embed.add_field(name="Kota Asal", value=kota.content, inline=False)
    embed.add_field(name="Character Story", value=story.content, inline=False)

    embed.set_footer(text=f"Dibuat oleh {ctx.author}")

    await ctx.send(embed=embed)

# ================= MY CS =================

@bot.command()
async def mycs(ctx):

    if ctx.author.id not in character_db:
        await ctx.send("Kamu belum membuat CS")
        return

    data = character_db[ctx.author.id]

    embed = discord.Embed(
        title="Character Story Kamu",
        description=SERVER_DESCRIPTION,
        color=discord.Color.blue()
    )

    embed.add_field(name="Server", value=SERVER_NAME, inline=False)
    embed.add_field(name="Nama", value=data["nama"], inline=False)
    embed.add_field(name="Level", value=data["level"], inline=False)
    embed.add_field(name="Gender", value=data["gender"], inline=False)
    embed.add_field(name="Tanggal Lahir", value=data["ttl"], inline=False)
    embed.add_field(name="Kota Asal", value=data["kota"], inline=False)
    embed.add_field(name="Character Story", value=data["story"], inline=False)

    embed.set_footer(text=f"Dibuat oleh {ctx.author}")

    await ctx.send(embed=embed)

# ================= RUN =================

bot.run(TOKEN)
