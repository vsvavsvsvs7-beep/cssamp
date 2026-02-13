import discord
from discord.ext import commands, tasks
import os
import datetime
import random

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875  # Channel khusus
OWNER_ROLE_ID = 1465731110162927707  # Role OWNER

# ================= BOT =================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Dictionary untuk cooldown user
bot.cooldowns = {}

# ================= HELPER =================
def channel_only():
    async def predicate(ctx):
        if ctx.channel.id != ALLOWED_CHANNEL_ID:
            await ctx.send("❌ Maaf, command hanya bisa digunakan di channel khusus.")
            return False
        return True
    return commands.check(predicate)

def cooldown_active(user_id):
    now = datetime.datetime.now()
    cd = bot.cooldowns.get(user_id)
    if cd and (cd - now).total_seconds() > 0:
        remaining = int((cd - now).total_seconds())
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        return f"{hours}h {minutes}m {seconds}s"
    return None

# ================= TASK LOOP =================
@tasks.loop(minutes=5)
async def notify_cooldown():
    now = datetime.datetime.now()
    to_remove = []
    for user_id, cd in bot.cooldowns.items():
        if (cd - now).total_seconds() <= 0:
            channel = bot.get_channel(ALLOWED_CHANNEL_ID)
            if channel:
                await channel.send(f"✅ <@{user_id}>, cooldown-mu sudah selesai! Sekarang kamu bisa membuat Character Story lagi!")
            to_remove.append(user_id)
    for uid in to_remove:
        bot.cooldowns.pop(uid, None)

@bot.event
async def on_ready():
    print(f"✅ Bot siap! Login sebagai: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Story Crafter | Auto Mode"))
    notify_cooldown.start()

# ================= MODAL =================
class CSModal(discord.ui.Modal, title="Form Character Story"):
    nama = discord.ui.TextInput(label="Nama Lengkap Karakter (IC) *", placeholder="Contoh: John Washington, Kenji Tanaka", required=True)
    level = discord.ui.TextInput(label="Level Karakter *", placeholder="Contoh: 1", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin *", placeholder="Contoh: Laki-laki / Perempuan", required=True)
    tgl_lahir = discord.ui.TextInput(label="Tanggal Lahir *", placeholder="Contoh: 17 Agustus 1995", required=True)
    kota = discord.ui.TextInput(label="Kota Asal *", placeholder="Contoh: Los Santos / San Fierro", required=True)

    def __init__(self, side):
        super().__init__()
        self.side = side

    def generate_story(self, nama, gender, kota, level):
        intro = f"{nama} lahir dan dibesarkan di kota {kota}. Sejak kecil ia menghadapi berbagai dinamika kehidupan.\n"
        masa_kecil = f"Masa kecilnya membentuk karakter dan mentalnya. Lingkungan mengajarkannya keberanian dan tanggung jawab.\n"
        perkembangan = f"Memasuki remaja, {nama} bertemu banyak orang dan belajar dari pengalaman.\n"

        if self.side == "Goodside":
            konflik = f"Meskipun menghadapi godaan dan tekanan, {nama} memilih jalur yang benar. Ia dihormati dan dipercaya banyak orang.\n"
        else:
            konflik = f"Namun dunia tidak selalu adil. {nama} belajar strategi, keberanian, dan kadang mengambil risiko demi tujuannya.\n"

        masa_sekarang = f"Sekarang di level {level}, {nama} memulai perjalanan barunya. Setiap langkah menentukan masa depan.\n"
        masa_depan = f"Perjalanan masih panjang. Apakah {nama} akan dihormati atau ditakuti, tergantung pilihannya.\n"

        story = intro + masa_kecil + perkembangan + konflik + masa_sekarang + masa_depan
        return story

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        cd_remaining = cooldown_active(user_id)
        if cd_remaining:
            await interaction.response.send_message(
                f"⏳ **Maaf {interaction.user.mention}, kamu masih cooldown!**\n"
                f"Sisa waktu: `{cd_remaining}`\n"
                f"Tunggu sampai cooldown habis, atau hubungi **OWNER** ⚡",
                ephemeral=True
            )
            return

        nama = self.nama.value
        level = self.level.value
        gender = self.gender.value
        tgl_lahir = self.tgl_lahir.value
        kota = self.kota.value

        story = self.generate_story(nama, gender, kota, level)

        embed = discord.Embed(
            title=f"🎉 Character Story - {self.side}",
            color=0x2ecc71
        )
        embed.add_field(name="Nama IC", value=nama, inline=False)
        embed.add_field(name="Level", value=level, inline=False)
        embed.add_field(name="Jenis Kelamin", value=gender, inline=False)
        embed.add_field(name="Tanggal Lahir", value=tgl_lahir, inline=False)
        embed.add_field(name="Kota Asal", value=kota, inline=False)
        embed.add_field(name="Story", value=story[:1024], inline=False)
        embed.set_footer(text=f"Dibuat oleh {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
        bot.cooldowns[user_id] = datetime.datetime.now() + datetime.timedelta(hours=24)

# ================= VIEW =================
class CSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="😇 Goodside", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("Goodside"))

    @discord.ui.button(label="😈 Badside", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal("Badside"))

# ================= COMMANDS =================
@bot.command()
@channel_only()
async def cs(ctx):
    user_id = ctx.author.id
    cd_remaining = cooldown_active(user_id)
    if cd_remaining:
        await ctx.send(
            f"⏳ **Maaf {ctx.author.mention}, kamu masih cooldown!**\n"
            f"Sisa waktu: `{cd_remaining}`\n"
            f"Tunggu sampai cooldown habis, atau hubungi **OWNER** ⚡"
        )
        return

    view = CSView()
    await ctx.send("Pilih sisi karakter kamu untuk membuat Character Story:", view=view)

@bot.command()
@channel_only()
async def menu(ctx):
    embed = discord.Embed(
        title="📜 Menu Story Crafter",
        description=f"Selamat datang, {ctx.author.mention}! Berikut command yang tersedia:",
        color=0x5865f2
    )
    embed.add_field(name="!cs", value="Buka tombol Goodside / Badside untuk membuat Character Story.", inline=False)
    embed.add_field(name="!cekcd", value="Cek apakah kamu masih cooldown.", inline=False)
    embed.add_field(name="!help", value="Panduan membuat Character Story.", inline=False)
    embed.add_field(name="!reset @user", value="Reset cooldown user (Hanya OWNER).", inline=False)
    embed.add_field(name="!cekcdall", value="Cek semua cooldown (Hanya OWNER).", inline=False)
    embed.add_field(name="!ping", value="Cek apakah bot aktif.", inline=False)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@channel_only()
async def help(ctx):
    embed = discord.Embed(
        title="❓ Panduan Story Crafter",
        description="Langkah-langkah membuat Character Story:",
        color=0xf1c40f
    )
    embed.add_field(name="1️⃣ !cs", value="Klik tombol Goodside / Badside untuk memulai.", inline=False)
    embed.add_field(name="2️⃣ Isi Form", value="Lengkapi Nama IC, Level, Jenis Kelamin, Tanggal Lahir, Kota Asal.", inline=False)
    embed.add_field(name="3️⃣ Submit", value="Story akan otomatis dibuat di channel ini.", inline=False)
    embed.add_field(name="⌛ Cooldown", value="1x sehari per user. Jika masih cooldown, gunakan !cekcd untuk melihat sisa waktu.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@channel_only()
async def cekcd(ctx):
    cd_remaining = cooldown_active(ctx.author.id)
    if cd_remaining:
        await ctx.send(f"❌ {ctx.author.mention}, kamu masih cooldown! Sisa waktu: `{cd_remaining}` ⏳")
    else:
        await ctx.send(f"✅ {ctx.author.mention}, kamu bisa membuat Character Story sekarang!")

@bot.command()
@channel_only()
async def reset(ctx, member: discord.Member):
    if OWNER_ROLE_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send(
            f"❌ **Maaf {ctx.author.mention}, kamu tidak memiliki izin untuk menggunakan fitur ini!**\n"
            f"Fitur ini hanya bisa digunakan oleh **OWNER** ⚡"
        )
        return

    bot.cooldowns.pop(member.id, None)
    await ctx.send(
        f"♻️ {member.mention}, cooldown-mu telah direset oleh **OWNER**! ✅ Sekarang kamu bisa membuat Character Story lagi."
    )

@bot.command()
@channel_only()
async def cekcdall(ctx):
    if OWNER_ROLE_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("❌ Maaf, fitur ini hanya bisa digunakan oleh **OWNER** ⚡")
        return

    now = datetime.datetime.now()
    msg = "⏱️ **Cooldown Semua Player:**\n"
    for user_id, cd in bot.cooldowns.items():
        remaining = int((cd - now).total_seconds())
        if remaining > 0:
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            msg += f"<@{user_id}> : `{hours}h {minutes}m {seconds}s`\n"
        else:
            msg += f"<@{user_id}> : ✅ Bisa digunakan\n"
    await ctx.send(msg)

@bot.command()
@channel_only()
async def ping(ctx):
    await ctx.send(f"🏓 **Pong!** Bot aktif dan siap digunakan, {ctx.author.mention} ✅")

# ================= RUN =================
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKEN tidak ditemukan di environment variable.")
