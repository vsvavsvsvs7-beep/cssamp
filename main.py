import discord
from discord.ext import commands
import google.generativeai as genai
import os
import io
import datetime

# ================= KONFIGURASI =================
TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = "AIzaSyCl1ScXm0tpiGISw-Cx21LYkJU8P4F6icE"
ALLOWED_CHANNEL_ID = 1471935338065694875 

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="!menu | Premium CS AI"))
        print(f"✅ {self.user} Online!")

bot = TatangBot()

# ================= MODAL SINGLE PAGE (ANTI-CRASH) =================
class CSModal(discord.ui.Modal, title="Form Pembuatan Character Story"):
    nama = discord.ui.TextInput(label="Nama IC & Level", placeholder="Contoh: John_Washington | Level 5", required=True)
    biodata = discord.ui.TextInput(label="Gender, Tgl Lahir, Kota Asal", placeholder="Contoh: Laki-laki, 17-08-1995, Chicago", required=True)
    bakat = discord.ui.TextInput(label="Bakat & Kultur", placeholder="Contoh: Supir ahli, Etnis Hispanic", required=True)
    cerita = discord.ui.TextInput(
        label="Detail Tambahan Cerita", 
        style=discord.TextStyle.paragraph, 
        placeholder="Masukkan masa lalu, tujuan hidup, atau kejadian penting karaktermu...",
        max_length=2000,
        required=True
    )

    def __init__(self, server, side):
        super().__init__()
        self.server = server
        self.side = side

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("⌛ **AI sedang memproses cerita dan file .txt...**", ephemeral=True)
        
        prompt = f"""
        Buatkan Character Story GTA SAMP untuk server {self.server}.
        Alur: {self.side}
        Identitas: {self.nama.value}
        Biodata Lengkap: {self.biodata.value}
        Keahlian: {self.bakat.value}
        Latar Belakang: {self.cerita.value}
        
        KETENTUAN:
        1. Minimal 500 kata, bahasa Indonesia formal.
        2. Gunakan format BBCode forum ([justify], [center], [b]).
        3. Cerita harus mendalam dan emosional sesuai sisi {self.side}.
        """
        
        try:
            response = ai_model.generate_content(prompt)
            cerita = response.text
            
            # Generate File .txt
            file_data = io.BytesIO(cerita.encode('utf-8'))
            discord_file = discord.File(file_data, filename=f"CS_{self.nama.value.split('|')[0].strip()}.txt")
            
            embed = discord.Embed(
                title="✅ Character Story Berhasil Dibuat!",
                description=f"Server: **{self.server}** | Sisi: **{self.side}**\n\n*Cerita lengkap terlampir di bawah dalam format teks dan file.*",
                color=0x2ecc71
            )
            
            await interaction.followup.send(embed=embed)
            await interaction.followup.send(content=f"```bbcode\n{cerita}\n```", file=discord_file)
        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan pada AI: {e}")

# ================= VIEW & SELECTION =================
class CSAlurView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.button(label="Sisi Baik (Goodside)", style=discord.ButtonStyle.success, emoji="😇")
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Goodside"))

    @discord.ui.button(label="Sisi Jahat (Badside)", style=discord.ButtonStyle.danger, emoji="😈")
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CSModal(self.server, "Badside"))

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="SSRP", emoji="🇺🇸"),
            discord.SelectOption(label="Virtual RP", emoji="💻"),
            discord.SelectOption(label="AARP", emoji="✈️"),
            discord.SelectOption(label="GCRP", emoji="🌳"),
            discord.SelectOption(label="TEN ROLEPLAY", emoji="🔟"),
            discord.SelectOption(label="CPRP", emoji="💎"),
            discord.SelectOption(label="Relative RP", emoji="👪"),
            discord.SelectOption(label="JGRP", emoji="🎮"),
            discord.SelectOption(label="FMRP", emoji="🛡️"),
        ]
        super().__init__(placeholder="Pilih server tujuan...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"📍 Server: **{self.values[0]}**. Pilih alur cerita:", 
            view=CSAlurView(self.values[0]), 
            ephemeral=True
        )

class ServerSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

# ================= COMMANDS =================
@bot.command()
async def menu(ctx):
    embed = discord.Embed(title="🌟 TATANG AI PREMIUM", description="Ketik `!panelcs` untuk mulai.", color=0x5865f2)
    await ctx.send(embed=embed)

@bot.command()
async def panelcs(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send(f"❌ Gunakan di <#{ALLOWED_CHANNEL_ID}>", delete_after=5)
    await ctx.send("🚀 **Pilih Server Tujuan Kamu:**", view=ServerSelectView())

if TOKEN:
    bot.run(TOKEN)
