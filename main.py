import discord
from discord.ext import commands
import os
import random
import datetime

# ------------------- Config -------------------
TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875  # Channel khusus CS

OWNER_ID = 1471265207945924619
MANAGEMENT_ROLE_ID = 1471265207945924619  # Role Management

# ------------------- Bot Setup -------------------
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

# ------------------- Story Generator -------------------
def generate_goodside_story(nama, gender, kota, level):
    return (
        f"{nama} lahir di kota {kota}, dalam keluarga penuh kasih dan nilai moral yang kuat.\n\n"
        "Sejak kecil, ia dikenal peduli, penuh empati, dan selalu siap membantu orang lain.\n\n"
        "Masa kecil dan sekolah membentuk karakter: disiplin, integritas, kepemimpinan, dan rasa tanggung jawab.\n\n"
        f"Di level {level}, {nama} menapaki perjalanan baru, membangun reputasi sebagai pribadi yang dapat dipercaya.\n\n"
        "Ia bertemu mentor, membangun relasi, menghadapi konflik dengan kepala dingin, dan selalu menebar kebaikan.\n\n"
        "Setiap keputusan dipikirkan matang, seimbang antara kepentingan diri dan orang lain.\n\n"
        "Perjalanan hidupnya baru dimulai, kisahnya akan dikenang sebagai simbol keberanian, kebaikan, dan inspirasi."
    )

def generate_badside_story(nama, gender, kota, level):
    return (
        f"{nama} lahir di kota {kota}, lingkungan keras membentuknya menjadi pribadi ambisius.\n\n"
        "Sejak kecil ia belajar bertahan hidup, membaca situasi, mengambil risiko, dan kadang cara gelap.\n\n"
        f"Di level {level}, {nama} menapaki jalan intrik, strategi, dan ambisi. Ia membangun reputasi dan dominasi.\n\n"
        "Masa remaja penuh konflik, pengkhianatan, dan peluang yang harus dimanfaatkan untuk menang.\n\n"
        "Ia menghadapi dilema moral, namun selalu menemukan cara untuk menguatkan posisinya.\n\n"
        "Perjalanan hidupnya penuh intrik, ambisi, dan risiko. Masa depan {nama} tergantung keputusan yang diambilnya, "
        "dan kisahnya akan dikenang sebagai legenda yang kuat dan cerdas."
    )

# ------------------- Modal -------------------
class CSModal(discord.ui.Modal, title="Form Character Story"):
    nama = discord.ui.TextInput(label="Nama Lengkap Karakter (IC) *", placeholder="Contoh: John Washington, Kenji Tanaka", required=True)
    level = discord.ui.TextInput(label="Level Karakter *", placeholder="Contoh: 1", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin *", placeholder="Laki-laki / Perempuan", required=True)
    tgl_lahir = discord.ui.TextInput(label="Tanggal Lahir *", placeholder="17 Agustus 1995", required=True)
    kota = discord.ui.TextInput(label="Kota Asal *", placeholder="Los Santos, San Fierro, Las Venturas", required=True)

    def __init__(self, side):
        super().__init__()
        self.side = side

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.datetime.now()

        # Cooldown 24 jam
        cd = bot.cooldowns.get(user_id)
        if cd and (cd - now).total_seconds() > 0:
            remaining = int((cd - now).total_seconds())
            minutes = remaining // 60
            seconds = remaining % 60
            await interaction.response.send_message(
                f"⏳ Maaf {interaction.user.mention}, kamu masih cooldown.\n"
                f"Sisa waktu: `{minutes}m {seconds}s`\n"
                f"Reset cooldown bisa minta ke <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>",
                ephemeral=True
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

        await interaction.response.send_message(embed=embed)
        bot.cooldowns[user_id] = now + datetime.timedelta(hours=24)

# ------------------- Button View -------------------
class CSButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Goodside 😇", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("Goodside"))

    @discord.ui.button(label="Badside 😈", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("Badside"))

# ------------------- Commands -------------------
@bot.command()
async def menu(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="📜 Story Crafter Menu",
        description="Gunakan command `!cs` untuk membuat Character Story epik. Pilih Goodside 😇 atau Badside 😈 lewat tombol setelah menjalankan `!cs`.",
        color=0x5865f2
    )
    embed.add_field(name="✨ !help", value="Tampilkan panduan cara membuat CS.", inline=False)
    embed.add_field(name="📖 !cs", value="Mulai membuat Character Story interaktif.", inline=False)
    embed.add_field(name="⏳ !checkcooldown", value="Cek cooldownmu saat ini.", inline=False)
    embed.add_field(name="♻️ !reset @player", value="Reset cooldown player (Owner / Management).", inline=False)
    embed.add_field(name="⏱️ !cekcdall", value="Cek cooldown semua player (Owner / Management).", inline=False)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

    await ctx.send(content=f"Butuh bantuan hubungi <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>", embed=embed)

@bot.command()
async def help(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="📜 Story Crafter - Panduan Membuat CS",
        description="Berikut panduan membuat Character Story:",
        color=0x5865f2
    )
    embed.add_field(
        name="1️⃣ Mulai CS",
        value="Ketik `!cs` untuk memulai membuat Character Story. Pilih Goodside 😇 atau Badside 😈 lewat tombol.",
        inline=False
    )
    embed.add_field(
        name="2️⃣ Isi Form",
        value="- Nama Lengkap Karakter (IC)\n- Level Karakter\n- Jenis Kelamin\n- Tanggal Lahir\n- Kota Asal (Los Santos, San Fierro, Las Venturas)\n\nPastikan semua data terisi.",
        inline=False
    )
    embed.add_field(
        name="3️⃣ Submit & Lihat Hasil",
        value="Setelah submit, bot akan menampilkan CS panjang otomatis di channel.\n⚠️ Cooldown: 24 jam per user. Reset bisa minta ke Owner / Management.",
        inline=False
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

    await ctx.send(content=f"Butuh bantuan hubungi <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>", embed=embed)

@bot.command()
async def cs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    await ctx.send(f"📌 {ctx.author.mention}, pilih sisi karaktermu:", view=CSButtonView())

@bot.command()
async def checkcooldown(ctx):
    user_id = ctx.author.id
    now = datetime.datetime.now()
    cd = bot.cooldowns.get(user_id)
    if cd and (cd - now).total_seconds() > 0:
        remaining = int((cd - now).total_seconds())
        minutes = remaining // 60
        seconds = remaining % 60
        await ctx.send(
            f"⏳ Maaf {ctx.author.mention}, kamu masih cooldown.\n"
            f"Sisa waktu: `{minutes}m {seconds}s`\n"
            f"Reset cooldown bisa minta ke <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>"
        )
    else:
        await ctx.send(f"✅ {ctx.author.mention}, kamu bisa membuat Character Story sekarang!")

@bot.command()
async def reset(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID and MANAGEMENT_ROLE_ID not in [r.id for r in ctx.author.roles]:
        await ctx.send("❌ Kamu tidak punya izin untuk reset cooldown.")
        return
    bot.cooldowns.pop(member.id, None)
    await ctx.send(f"♻️ Cooldown {member.mention} berhasil direset oleh {ctx.author.mention}")

@bot.command()
async def cekcdall(ctx):
    if ctx.author.id != OWNER_ID and MANAGEMENT_ROLE_ID not in [r.id for r in ctx.author.roles]:
        await ctx.send("❌ Kamu tidak punya izin untuk cek cooldown semua.")
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

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Bot aktif, {ctx.author.mention}")

# ------------------- Run Bot -------------------
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKEN tidak ditemukan.")
