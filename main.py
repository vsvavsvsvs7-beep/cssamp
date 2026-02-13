import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1471935338065694875

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ================= GOOD SIDE STORY =================

def generate_goodside_story(nama, level, gender, ttl, kota):

    return (
        f"{nama} adalah seorang {gender} yang lahir pada tanggal {ttl} dan berasal dari kota {kota}. "
        f"Sejak kecil, {nama} dikenal sebagai pribadi yang tenang dan memiliki semangat besar untuk mencapai masa depan yang lebih baik. "
        f"Kehidupan di kota {kota} mengajarkan banyak hal tentang arti perjuangan, tanggung jawab, dan pentingnya menjaga prinsip hidup.\n\n"

        f"Masa kecilnya dipenuhi dengan berbagai pengalaman yang membentuk karakter dan mentalnya. "
        f"{nama} belajar untuk menghadapi berbagai tantangan hidup dengan kesabaran dan tekad yang kuat. "
        f"Ia selalu percaya bahwa kerja keras dan kejujuran adalah kunci utama untuk mencapai kesuksesan.\n\n"

        f"Seiring berjalannya waktu, {nama} mulai memahami bagaimana dunia bekerja. "
        f"Berbagai pertemuan dan pengalaman membuatnya semakin dewasa dalam mengambil keputusan. "
        f"Ia berusaha untuk menjadi pribadi yang dihormati dan dipercaya oleh orang-orang di sekitarnya.\n\n"

        f"Kini, sebagai karakter dengan level {level}, {nama} memulai perjalanan barunya. "
        f"Dengan tekad yang kuat, ia siap menghadapi berbagai tantangan yang ada di depannya. "
        f"Ia percaya bahwa masa depan dapat dibangun dengan usaha, kerja keras, dan keyakinan pada diri sendiri.\n\n"

        f"Perjalanan hidup {nama} masih panjang, dan setiap langkah yang ia ambil akan menentukan masa depannya. "
        f"Dengan prinsip dan tekad yang ia miliki, ia siap membangun kisah hidupnya sendiri."
    )


# ================= BAD SIDE STORY =================

def generate_badside_story(nama, level, gender, ttl, kota):

    return (
        f"{nama} adalah seorang {gender} yang lahir pada tanggal {ttl} di kota {kota}. "
        f"Kehidupan yang keras telah membentuknya menjadi pribadi yang kuat dan tidak mudah menyerah. "
        f"Sejak kecil, ia telah memahami bahwa dunia tidak selalu berjalan sesuai harapan.\n\n"

        f"Lingkungan tempat ia tumbuh memberikan banyak pelajaran berharga. "
        f"{nama} belajar bagaimana bertahan hidup, menghadapi tekanan, dan membuat keputusan sulit. "
        f"Semua pengalaman tersebut membentuk mentalnya menjadi lebih tangguh.\n\n"

        f"Seiring waktu, ia mulai membangun jalannya sendiri. "
        f"Ia tidak takut menghadapi risiko dan siap menghadapi segala konsekuensi dari setiap keputusan yang ia ambil. "
        f"Baginya, kekuatan dan keberanian adalah kunci untuk bertahan di dunia yang keras.\n\n"

        f"Kini, sebagai karakter dengan level {level}, {nama} memulai babak baru dalam hidupnya. "
        f"Kota ini menjadi tempat di mana ia akan menentukan masa depannya sendiri. "
        f"Ia siap menghadapi siapa pun dan apa pun yang menghalangi jalannya.\n\n"

        f"Masa depan {nama} masih menjadi misteri. "
        f"Namun satu hal yang pasti, ia akan terus berjalan maju tanpa rasa takut."
    )


# ================= MODAL =================

class CSModal(discord.ui.Modal):

    def __init__(self, side):
        super().__init__(title="Form Character Story")
        self.side = side

        self.nama = discord.ui.TextInput(
            label="Nama Lengkap Karakter (IC) *",
            placeholder="Contoh: John Washington, Kenji Tanaka",
            required=True
        )

        self.level = discord.ui.TextInput(
            label="Level Karakter *",
            placeholder="Contoh: 1",
            required=True
        )

        self.gender = discord.ui.TextInput(
            label="Jenis Kelamin *",
            placeholder="Contoh: Laki-laki / Perempuan",
            required=True
        )

        self.tanggal_lahir = discord.ui.TextInput(
            label="Tanggal Lahir *",
            placeholder="Contoh: 17 Agustus 1995",
            required=True
        )

        self.kota = discord.ui.TextInput(
            label="Kota Asal *",
            placeholder="Contoh: Los Santos / San Fierro / Las Venturas",
            required=True
        )

        self.add_item(self.nama)
        self.add_item(self.level)
        self.add_item(self.gender)
        self.add_item(self.tanggal_lahir)
        self.add_item(self.kota)

    async def on_submit(self, interaction: discord.Interaction):

        nama = self.nama.value
        level = self.level.value
        gender = self.gender.value
        ttl = self.tanggal_lahir.value
        kota = self.kota.value

        if self.side == "Goodside":
            story = generate_goodside_story(nama, level, gender, ttl, kota)
        else:
            story = generate_badside_story(nama, level, gender, ttl, kota)

        embed = discord.Embed(
            title="CHARACTER STORY",
            color=0x2ecc71
        )

        embed.add_field(name="Nama Lengkap Karakter (IC)", value=nama, inline=False)
        embed.add_field(name="Level Karakter", value=level, inline=False)
        embed.add_field(name="Jenis Kelamin", value=gender, inline=False)
        embed.add_field(name="Tanggal Lahir", value=ttl, inline=False)
        embed.add_field(name="Kota Asal", value=kota, inline=False)
        embed.add_field(name="Side Character", value=self.side, inline=False)
        embed.add_field(name="Character Story", value=story, inline=False)

        embed.set_footer(text=f"Dibuat oleh {interaction.user}")

        await interaction.response.send_message(embed=embed)


# ================= VIEW =================

class CSView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Goodside", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(CSModal("Goodside"))

    @discord.ui.button(label="Badside", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(CSModal("Badside"))


# ================= COMMAND =================

@bot.command()
async def panelcs(ctx):

    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="CS GENERATOR PANEL",
        description=(
            "Silakan pilih side character.\n\n"
            "Isi data sesuai karakter roleplay kamu.\n\n"
            "Contoh Kota GTA SAMP:\n"
            "• Los Santos\n"
            "• San Fierro\n"
            "• Las Venturas"
        ),
        color=0x5865f2
    )

    await ctx.send(embed=embed, view=CSView())


# ================= RUN =================

bot.run(TOKEN)
