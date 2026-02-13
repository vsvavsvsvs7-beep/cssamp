import discord
from discord.ext import commands, tasks
import os
import random
import datetime

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875  # Channel khusus CS

OWNER_ID = 1471265207945924619
MANAGEMENT_ROLE_ID = 1465731110162927707

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

# ------------------- Modal -------------------
class CSModal(discord.ui.Modal, title="Form Character Story"):

    nama = discord.ui.TextInput(label="Nama Lengkap Karakter (IC) *", placeholder="Contoh: John Washington, Kenji Tanaka", required=True)
    level = discord.ui.TextInput(label="Level Karakter *", placeholder="Contoh: 1", required=True)
    gender = discord.ui.TextInput(label="Jenis Kelamin *", placeholder="Contoh: Laki-laki / Perempuan", required=True)
    tgl_lahir = discord.ui.TextInput(label="Tanggal Lahir *", placeholder="Contoh: 17 Agustus 1995", required=True)
    kota = discord.ui.TextInput(label="Kota Asal *", placeholder="Contoh: Los Santos / San Fierro", required=True)

    def __init__(self, side):
        super().__init__()
        self.side = side

    # ------------------ Story ------------------
    def story_goodside(self, nama, gender, kota, level):
        return (
            f"{nama} lahir di kota {kota}, dalam keluarga penuh kasih dan nilai moral yang kuat.\n\n"
            "Sejak kecil, ia dikenal peduli, penuh empati, dan selalu siap membantu orang lain.\n\n"
            "Masa kecil dan sekolah membentuk karakter: disiplin, integritas, kepemimpinan, dan rasa tanggung jawab.\n\n"
            f"Di level {level}, {nama} menapaki perjalanan baru, membangun reputasi sebagai pribadi yang dapat dipercaya.\n\n"
            "Ia bertemu mentor, membangun relasi, menghadapi konflik dengan kepala dingin, dan selalu menebar kebaikan.\n\n"
            "Setiap keputusan dipikirkan matang, seimbang antara kepentingan diri dan orang lain.\n\n"
            "Perjalanan hidupnya baru dimulai, kisahnya akan dikenang sebagai simbol keberanian, kebaikan, dan inspirasi."
        )

    def story_badside(self, nama, gender, kota, level):
        return (
            f"{nama} lahir di kota {kota}, lingkungan keras membentuknya menjadi pribadi ambisius.\n\n"
            "Sejak kecil ia belajar bertahan hidup, membaca situasi, mengambil risiko, dan kadang cara gelap.\n\n"
            f"Di level {level}, {nama} menapaki jalan intrik, strategi, dan ambisi. Ia membangun reputasi dan dominasi.\n\n"
            "Masa remaja penuh konflik, pengkhianatan, dan peluang yang harus dimanfaatkan untuk menang.\n\n"
            "Ia menghadapi dilema moral, namun selalu menemukan cara untuk menguatkan posisinya.\n\n"
            "Perjalanan hidupnya penuh intrik, ambisi, dan risiko. Masa depan {nama} tergantung keputusan yang diambilnya, "
            "dan kisahnya akan dikenang sebagai legenda yang kuat dan cerdas."
        )

    def generate_story(self, nama, gender, kota, level):
        if self.side == "Goodside":
            return self.story_goodside(nama, gender, kota, level)
        else:
            return self.story_badside(nama, gender, kota, level)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.datetime.now()

        # ------------------ Cooldown ------------------
        cd = bot.cooldowns.get(user_id)
        if cd:
            remaining = (cd - now).total_seconds()
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                await interaction.response.send_message(
                    f"⏳ Maaf {interaction.user.mention}, kamu masih cooldown.\n"
                    f"Durasi tersisa: `{minutes}m {seconds}s`\n"
                    f"Jika ingin reset cooldown, hubungi <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>",
                    ephemeral=True
                )
                return

        nama = self.nama.value
        level = self.level.value
        gender = self.gender.value
        kota = self.kota.value

        story = self.generate_story(nama, gender, kota, level)

        embed = discord.Embed(
            title=f"✨ Character Story: {nama}",
            description=story,
            color=0x2ecc71
        )
        embed.add_field(name="Nama", value=nama, inline=True)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Jenis Kelamin", value=gender, inline=True)
        embed.add_field(name="Tanggal Lahir", value=self.tgl_lahir.value, inline=True)
        embed.add_field(name="Kota Asal", value=kota, inline=True)
        embed.set_footer(text=f"CS dibuat oleh {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
        bot.cooldowns[user_id] = now + datetime.timedelta(hours=24)  # Cooldown 24 jam

# ------------------- View -------------------
class CSView(discord.ui.View):
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
        description="Pilih sisi karakter kamu dan buat Character Story epik!\n"
                    "Commands:\n"
                    "• `!menu` - Tampilkan menu ini\n"
                    "• `!help` - Bantuan\n"
                    "• `!ping` - Cek bot online\n"
                    "• `!report <pesan>` - Laporkan masalah\n"
                    "• `!reset @player` - Reset cooldown player (Owner / Management)\n"
                    "• `!cekcdall` - Cek cooldown semua player (Owner / Management)\n"
                    "• `!checkcooldown` - Cek cooldownmu sendiri",
        color=0x5865f2
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed, view=CSView())

@bot.command()
async def help(ctx):
    await menu(ctx)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Bot aktif, {ctx.author.mention}")

@bot.command()
async def report(ctx, *, pesan):
    await ctx.send(f"📣 Laporan dari {ctx.author.mention}:\n{pesan}\n"
                   f"Jika butuh bantuan segera, hubungi <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>")

# ------------------- Cooldown Commands -------------------
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
            f"Durasi tersisa: `{minutes}m {seconds}s`\n"
            f"Jika ingin reset, hubungi <@{OWNER_ID}> atau <@&{MANAGEMENT_ROLE_ID}>"
        )
    else:
        await ctx.send(f"✅ {ctx.author.mention}, kamu bisa membuat Character Story sekarang!")

@bot.command()
async def reset(ctx, member: discord.Member):
    author_roles = [r.id for r in ctx.author.roles]
    if ctx.author.id != OWNER_ID and MANAGEMENT_ROLE_ID not in author_roles:
        await ctx.send("❌ Kamu tidak punya izin untuk reset cooldown.")
        return
    bot.cooldowns.pop(member.id, None)
    await ctx.send(f"♻️ Cooldown {member.mention} berhasil direset oleh {ctx.author.mention}")

@bot.command()
async def cekcdall(ctx):
    author_roles = [r.id for r in ctx.author.roles]
    if ctx.author.id != OWNER_ID and MANAGEMENT_ROLE_ID not in author_roles:
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

# ------------------- Run Bot -------------------
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKEN tidak ditemukan.")
