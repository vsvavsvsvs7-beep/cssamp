import discord
from discord.ext import commands
import random
import datetime
import os

# ================== Config ==================
TOKEN = os.getenv("TOKEN")  # Railway environment variable
ALLOWED_CHANNEL_ID = 1471935338065694875  # Channel khusus CS

# ================== Bot Setup ==================
class TatangCS(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.cooldowns = {}  # {user_id: datetime}

    async def on_ready(self):
        print(f"✅ Bot siap! Login sebagai {self.user}")
        await self.change_presence(activity=discord.Game(name="Story Crafter | Auto Mode"))

bot = TatangCS()

# ================== Story Generator ==================
def generate_goodside_story(nama, gender, kota, level):
    return (
        f"{nama} lahir di kota {kota}, dalam keluarga penuh kasih dan nilai moral yang kuat.\n\n"
        "Sejak kecil, ia dikenal peduli, penuh empati, dan selalu siap membantu orang lain.\n\n"
        "Masa kecil dan sekolah membentuk karakter: disiplin, integritas, kepemimpinan, dan rasa tanggung jawab.\n\n"
        f"Di level {level}, {nama} menapaki perjalanan baru, membangun reputasi sebagai pribadi yang dapat dipercaya.\n\n"
        "Perjalanan hidupnya baru dimulai, kisahnya akan dikenang sebagai simbol keberanian, kebaikan, dan inspirasi."
    )

def generate_badside_story(nama, gender, kota, level):
    return (
        f"{nama} lahir di kota {kota}, lingkungan keras membentuknya menjadi pribadi ambisius.\n\n"
        "Sejak kecil ia belajar bertahan hidup, membaca situasi, mengambil risiko, dan kadang cara gelap.\n\n"
        f"Di level {level}, {nama} menapaki jalan intrik, strategi, dan ambisi. Ia membangun reputasi dan dominasi.\n\n"
        "Perjalanan hidupnya penuh intrik dan risiko. Masa depan {nama} tergantung keputusan yang diambilnya."
    )

# ================== Modal ==================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    nama = discord.ui.TextInput(label="Nama Lengkap Karakter (IC) *", placeholder="Contoh: John Washington", required=True)
    level = discord.ui.TextInput(label="Level Karakter *", placeholder="Contoh: 1", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin *", placeholder="Laki-laki / Perempuan", required=True)
    tgl_lahir = discord.ui.TextInput(label="Tanggal Lahir *", placeholder="17 Agustus 1995", required=True)
    kota = discord.ui.TextInput(label="Kota Asal *", placeholder="Los Santos / San Fierro / Las Venturas", required=True)

    def __init__(self, side, user_id):
        super().__init__()
        self.side = side
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        now = datetime.datetime.now()

        # Cooldown 24 jam
        cd = bot.cooldowns.get(self.user_id)
        if cd and (cd - now).total_seconds() > 0:
            remaining = int((cd - now).total_seconds())
            minutes = remaining // 60
            seconds = remaining % 60
            await interaction.response.send_message(
                f"⏳ Maaf {interaction.user.mention}, kamu masih cooldown.\nSisa waktu: `{minutes}m {seconds}s`", ephemeral=True
            )
            return

        nama = self.nama.value
        level = self.level.value
        gender = self.gender.value
        tgl_lahir = self.tgl_lahir.value
        kota = self.kota.value

        story = generate_goodside_story(nama, gender, kota, level) if self.side == "Goodside" else generate_badside_story(nama, gender, kota, level)
        color = 0x2ecc71 if self.side == "Goodside" else 0xe74c3c

        embed = discord.Embed(
            title=f"✨ Character Story: {nama}",
            description=story,
            color=color
        )
        embed.add_field(name="Nama", value=nama, inline=True)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Jenis Kelamin", value=gender, inline=True)
        embed.add_field(name="Tanggal Lahir", value=tgl_lahir, inline=True)
        embed.add_field(name="Kota Asal", value=kota, inline=True)
        embed.set_footer(text=f"CS dibuat oleh {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Kirim embed + tag user di bawah
        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(f"👤 CS ini dibuat oleh {interaction.user.mention}")

        bot.cooldowns[self.user_id] = now + datetime.timedelta(hours=24)

# ================== Button View ==================
class CSButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="😇 Goodside", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("Goodside", interaction.user.id))

    @discord.ui.button(label="😈 Badside", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("Badside", interaction.user.id))

# ================== Commands ==================
@bot.command()
async def cs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    embed = discord.Embed(
        title="🎨 Story Crafter",
        description=(
            f"Hai {ctx.author.mention}! Pilih sisi karakter kamu di bawah ini:\n\n"
            "😇 **Goodside** → Buat karakter dengan sisi baik\n"
            "😈 **Badside** → Buat karakter dengan sisi jahat"
        ),
        color=0x5865f2
    )
    await ctx.send(embed=embed, view=CSButtonView())

@bot.command()
async def checkcooldown(ctx):
    user_id = ctx.author.id
    now = datetime.datetime.now()
    cd = bot.cooldowns.get(user_id)
    if cd and (cd - now).total_seconds() > 0:
        remaining = int((cd - now).total_seconds())
        minutes = remaining // 60
        seconds = remaining % 60
        await ctx.send(f"⏳ Maaf {ctx.author.mention}, kamu masih cooldown `{minutes}m {seconds}s`")
    else:
        await ctx.send(f"✅ {ctx.author.mention}, kamu bisa membuat CS sekarang!")

# ================== Reset / Cek All (Pemilik Server) ==================
@bot.command()
async def reset(ctx, member: discord.Member):
    if ctx.author != ctx.guild.owner:
        await ctx.send("❌ Maaf, fitur ini hanya bisa digunakan oleh Tatang.")
        return
    bot.cooldowns.pop(member.id, None)
    await ctx.send(f"♻️ Cooldown {member.mention} berhasil direset!")

@bot.command()
async def cekcdall(ctx):
    if ctx.author != ctx.guild.owner:
        await ctx.send("❌ Maaf, fitur ini hanya bisa digunakan oleh Tatang.")
        return
    now = datetime.datetime.now()
    msg = "⏱️ Cooldown semua player:\n"
    for user_id, cd in bot.cooldowns.items():
        remaining = int((cd - now).total_seconds())
        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            msg += f"<@{user_id}> : `{minutes}m {seconds}s`\n"
        else:
            msg += f"<@{user_id}> : ✅ Bisa digunakan\n"
    await ctx.send(msg)

# ================== Menu & Help ==================
@bot.command()
async def menu(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    embed = discord.Embed(
        title="📜 Story Crafter Menu",
        description="Gunakan command `!cs` untuk membuat Character Story interaktif!",
        color=0x5865f2
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.add_field(name="✨ !help", value="Panduan membuat CS secara mudah.", inline=False)
    embed.add_field(name="📖 !cs", value="Mulai membuat Character Story interaktif.", inline=False)
    embed.add_field(name="⏳ !checkcooldown", value="Cek cooldownmu saat ini.", inline=False)
    embed.add_field(name="♻️ !reset @player", value="Reset cooldown player (Hanya Tatang).", inline=False)
    embed.add_field(name="⏱️ !cekcdall", value="Cek cooldown semua player (Hanya Tatang).", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    embed = discord.Embed(
        title="📜 Story Crafter - Panduan Membuat CS",
        description="1️⃣ Ketik `!cs` → Pilih Goodside 😇 / Badside 😈\n"
                    "2️⃣ Isi form modal karakter\n"
                    "3️⃣ Submit → CS panjang muncul otomatis\n"
                    "⚠️ Cooldown: 24 jam per user",
        color=0x5865f2
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Bot aktif, {ctx.author.mention}")

# ================== Run Bot ==================
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKEN tidak ditemukan di environment variable.")
