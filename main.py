import discord
import os
import json
import psutil
import zipfile
import py7zr
import re
import io
import math
import aiohttp
import asyncio
import random
import string
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

# ================= KONFIGURASI (RAILWAY & ID) =================
TOKEN = os.getenv("TOKEN")
SCAN_CHANNEL_ID = 1469740150522380299      
REQ_VIP_CHANNEL_ID = 1472535677634740398   
ADMIN_ROLE_ID = 1471265207945924619        
VIP_FILE = "vips.json"

# ================= UTILITY FUNCTIONS =================
def load_vips():
    if not os.path.exists(VIP_FILE):
        with open(VIP_FILE, "w") as f: json.dump([], f)
    try:
        with open(VIP_FILE, "r") as f: return json.load(f)
    except: return []

def save_vips(vips):
    with open(VIP_FILE, "w") as f: json.dump(vips, f)

def generate_fake_data():
    nicks = ["Dika_Ganteng", "Admin_SAMP", "Player_Pro", "Tatang_Sakti", "Bocah_SAMP"]
    ips = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    pw = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return (
        "```ascii\n"
        "╔═══════════════════════════════════════════════╗\n"
        "║          TATANG COMUNITY SAMP LOGS            ║\n"
        "╠═══════════════════════════════════════════════╣\n"
        f"  > Nickname : {random.choice(nicks)}\n"
        f"  > Password : {pw}\n"
        f"  > IP Addr  : {ips}\n"
        "╠═══════════════════════════════════════════════╣\n"
        "  SUBSCRIBE : [youtube.com/@tatangchit](https://youtube.com/@tatangchit)           \n"
        "╚═══════════════════════════════════════════════╝\n"
        "```"
    )

# ================= SCANNER ENGINE =================
def analyze_content(content):
    pola_terdeteksi = []
    found_links = []
    dw_regex = r"https://discord\.com/api/webhooks/\d+/\S+"
    tg_regex = r"https://api\.telegram\.org/bot\d+:\S+"
    dw_links = re.findall(dw_regex, content)
    tg_links = re.findall(tg_regex, content)
    if dw_links: found_links.extend(dw_links)
    if tg_links: found_links.extend(tg_links)
    danger_map = {
        "os.execute": "os.execute", "io.popen": "io.popen", "loadstring": "loadstring",
        "sampGetPlayerNickname": "sampGetPlayerNickname", "sampGetCurrentServerAddress": "sampGetCurrentServerAddress",
        "LuaObfuscator.com": "LuaObfuscator.com (L8)", "exec": "exec"
    }
    for key, label in danger_map.items():
        if key in content: pola_terdeteksi.append(label)
    return pola_terdeteksi, found_links

# ================= UI COMPONENTS (PANEL MENU) =================
class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Subscribe YouTube", url="https://youtube.com/@tatangchit", style=discord.ButtonStyle.link))

    @discord.ui.button(label="🔵 Spam Discord", style=discord.ButtonStyle.primary, custom_id="spam_discord")
    async def spam_discord(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WebhookModal())

    @discord.ui.button(label="⬛ Stop", style=discord.ButtonStyle.danger, custom_id="stop_op")
    async def stop_op(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔴 **Operasi Dihentikan!**", ephemeral=False)

    @discord.ui.button(label="👁️ Preview", style=discord.ButtonStyle.secondary, custom_id="preview_data")
    async def preview_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"**Contoh data yang dikirim:**\n{generate_fake_data()}", ephemeral=True)

class WebhookModal(discord.ui.Modal, title="🎯 SA-MP Keylogger Counter"):
    webhook_url = discord.ui.TextInput(label="URL Webhook Target", placeholder="Tempel URL penipu...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        vips = load_vips()
        if interaction.user.id not in vips:
            return await interaction.response.send_message("❌ **Akses Ditolak!** Fitur ini khusus VIP.", ephemeral=True)

        await interaction.response.send_message("🚀 Memulai banjir data palsu...", ephemeral=True)
        embed = discord.Embed(title="🎯 Flooding Webhook", color=0xff0000)
        msg = await interaction.channel.send(embed=embed)

        async with aiohttp.ClientSession() as session:
            for i in range(1, 101):
                payload = {"content": generate_fake_data()}
                try:
                    async with session.post(self.webhook_url.value, json=payload) as resp:
                        if resp.status == 429:
                            await asyncio.sleep(5); continue
                except: break
                if i % 10 == 0:
                    bar = "█" * (i // 10) + "░" * (10 - (i // 10))
                    new_embed = embed.copy()
                    new_embed.add_field(name="Progress", value=f"[{bar}] {i}%", inline=False)
                    await msg.edit(embed=new_embed)
                await asyncio.sleep(0.4)
        await msg.edit(content="✅ **Selesai!** 100 log palsu terkirim.")

# ================= BOT INITIALIZATION =================
class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="/", intents=intents) # Prefix default diubah ke /

    async def setup_hook(self):
        await self.tree.sync()

bot = TatangBot()

# ================= SLASH COMMANDS (SEMUA MENGGUNAKAN /) =================

@bot.tree.command(name="menu", description="Dashboard Utama Tatang Bot")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(title="📄 TATANG BOT | DASHBOARD MENU", color=0x3498db)
    embed.description = "Pusat kendali fitur keamanan dan manajemen VIP server."
    embed.add_field(name="👑 **ADMINISTRATION**", value="`/addvip` • `/removevip` • `/listvip`", inline=False)
    embed.add_field(name="🛠️ **UTILITY**", value="`/status` • `/help` • `/start_counter`", inline=False)
    embed.add_field(name="🛡️ **SECURITY STATUS**", value=f"**Scanner:** Aktif ✅\n**Format:** .lua, .zip, .7z", inline=False)
    embed.set_footer(text="Premium Management System • v2.1")
    await interaction.response.send_message(embed=embed, view=MenuView())

@bot.tree.command(name="help", description="Panduan Deep Scanner & Counter")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="❓ PANDUAN TATANG BOT", color=0x9b59b6)
    embed.add_field(name="1. Deep Scanner", value="Kirim file `.lua`, `.zip`, atau `.7z` di <#1469740150522380299>. Bot otomatis membongkar isi file.", inline=False)
    embed.add_field(name="2. Keylogger Counter", value="Gunakan perintah `/menu` lalu pilih **Spam Discord** untuk membanjiri webhook penipu.", inline=False)
    embed.add_field(name="3. Tingkat Bahaya", value="**10%** = Aman\n**25-50%** = Mencurigakan\n**100%** = Bahaya (Webhook ditemukan)", inline=False)
    embed.set_footer(text="Support: youtube.com/@tatangchit")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addvip", description="Berikan akses VIP kepada user (Admin Only)")
async def addvip(interaction: discord.Interaction, member: discord.Member):
    role = interaction.guild.get_role(ADMIN_ROLE_ID)
    if role not in interaction.user.roles:
        return await interaction.response.send_message("❌ **Akses Ditolak!**", ephemeral=True)
    vips = load_vips()
    if member.id not in vips:
        vips.append(member.id)
        save_vips(vips)
        embed = discord.Embed(title="✨ VIP ACCESS GRANTED", description=f"{member.mention} Berhasil menjadi VIP! ✅", color=0x2ecc71)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("User sudah VIP.", ephemeral=True)

@bot.tree.command(name="removevip", description="Cabut akses VIP user (Admin Only)")
async def removevip(interaction: discord.Interaction, member: discord.Member):
    role = interaction.guild.get_role(ADMIN_ROLE_ID)
    if role not in interaction.user.roles:
        return await interaction.response.send_message("❌ **Akses Ditolak!**", ephemeral=True)
    vips = load_vips()
    if member.id in vips:
        vips.remove(member.id)
        save_vips(vips)
        await interaction.response.send_message(f"✅ Akses VIP {member.mention} telah dicabut.")
    else:
        await interaction.response.send_message("User bukan VIP.", ephemeral=True)

@bot.tree.command(name="listvip", description="Lihat daftar database member VIP")
async def listvip(interaction: discord.Interaction):
    vips = load_vips()
    mentions = "\n".join([f"• <@{uid}>" for uid in vips]) if vips else "Database VIP masih kosong."
    embed = discord.Embed(title="👑 DATABASE USER VIP", description=mentions, color=0xf1c40f)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Cek status server bot")
async def status(interaction: discord.Interaction):
    ram, ping = psutil.virtual_memory().percent, round(bot.latency * 1000)
    embed = discord.Embed(title="🚀 SYSTEM STATUS", color=0x2ecc71)
    embed.add_field(name="RAM Usage", value=f"{ram}%", inline=True)
    embed.add_field(name="Bot Latency", value=f"{ping}ms", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="start_counter", description="Buka panel flooding webhook")
async def start_counter(interaction: discord.Interaction):
    await menu(interaction)

@bot.tree.command(name="createpanelwebhook", description="Buat panel menu di channel")
async def createpanelwebhook(interaction: discord.Interaction):
    await menu(interaction)

# ================= SCANNER LOGIC (TAMPILAN TETAP ASLI) =================
@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != SCAN_CHANNEL_ID: return
    if message.attachments:
        vips = load_vips()
        if message.author.id not in vips:
            embed = discord.Embed(title="🔒 PREMIUM ACCESS REQUIRED", color=0xf1c40f)
            embed.description = f"Halo {message.author.mention}, fitur **Deep Scanner** hanya untuk VIP.\n\n🛡️ **Minta Akses:** <#{REQ_VIP_CHANNEL_ID}>"
            return await message.reply(embed=embed)

        for attachment in message.attachments:
            ext = os.path.splitext(attachment.filename)[1].lower()
            if ext not in [".lua", ".txt", ".zip", ".7z"]: continue
            await message.add_reaction("⏳")
            file_data = await attachment.read()
            pola, links, files_count = [], [], 0
            try:
                if ext in [".lua", ".txt"]:
                    c = file_data.decode(errors="ignore"); p, l = analyze_content(c)
                    pola.extend(p); links.extend(l); files_count = 1
                elif ext == ".zip":
                    with zipfile.ZipFile(io.BytesIO(file_data)) as z:
                        for f in z.namelist():
                            if f.lower().endswith((".lua", ".txt")):
                                c = z.read(f).decode(errors="ignore"); p, l = analyze_content(c)
                                pola.extend(p); links.extend(l); files_count += 1
                elif ext == ".7z":
                    with py7zr.SevenZipFile(io.BytesIO(file_data), mode='r') as z:
                        names = [n for n in z.getnames() if n.lower().endswith((".lua", ".txt"))]
                        if names:
                            contents = z.read(names)
                            for name, bio in contents.items():
                                c = bio.read().decode(errors="ignore"); p, l = analyze_content(c)
                                pola.extend(p); links.extend(l); files_count += 1
            except Exception as e:
                await message.remove_reaction("⏳", bot.user)
                return await message.reply(f"❌ **Read Error:** `{e}`")

            # TAMPILAN SCANNER (TETAP SESUAI KODE ASLI)
            pola, links = list(set(pola)), list(set(links))
            if links:
                status, color, conf = "🔴 🚨 BAHAYA TINGGI", 0xff0000, "75%"
                analisis_msg = f"Ditemukan {len(links)} link webhook berbahaya."
            elif len(pola) >= 2:
                status, color, conf = "🟠 ⚠️ SANGAT MENCURIGAKAN", 0xe67e22, "75%"
                analisis_msg = f"Ditemukan {len(pola)} pola mencurigakan. Pola paling berbahaya memiliki level 3."
            elif len(pola) == 1:
                status, color, conf = "🟡 🤔 MENCURIGAKAN", 0xf1c40f, "75%"
                analisis_msg = "Ditemukan 1 pola mencurigakan. Pola paling berbahaya memiliki level 2."
            else:
                status, color, conf = "✅ 🛡️ AMAN", 0x2ecc71, "85%"
                analisis_msg = "Analisis manual tidak menemukan pola berbahaya."

            embed = discord.Embed(title=status, color=color)
            embed.description = (
                f"**File:** `{attachment.filename}`\n"
                f"**Tujuan Script:** Analisis manual berbasis pola\n"
                f"**Analisis:** {analisis_msg}\n\n"
                f"🎯 **Confidence**\n{conf}\n\n"
                f"📊 **File Info**\nSize: {len(file_data):,} bytes\nType: {ext}"
            )

            if pola:
                pola_list = "\n".join([f"• {p} di {attachment.filename}" for p in pola])
                embed.add_field(name=f"📝 Pola Terdeteksi ({len(pola)})", value=pola_list, inline=False)
            if links:
                links_list = "\n".join([f"🔗 [KLIK LINK WEBHOOK]({l})" for l in links])
                embed.add_field(name="🌐 Webhook Found", value=links_list, inline=False)

            embed.set_footer(text=f"Dianalisis oleh: Manual • {files_count} file diperiksa | youtube.com/@tatangchit")
            await message.reply(embed=embed)
            await message.remove_reaction("⏳", bot.user)

bot.run(TOKEN)
