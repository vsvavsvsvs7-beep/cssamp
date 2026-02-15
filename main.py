import discord
import os
import json
import psutil
import zipfile
import py7zr
import re
import io
import aiohttp
import asyncio
import random
import string
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

# ================= KONFIGURASI ID =================
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

# ================= SCANNER ENGINE (ORIGINAL) =================
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
        "os.execute": "os.execute",
        "io.popen": "io.popen",
        "loadstring": "loadstring",
        "sampGetPlayerNickname": "sampGetPlayerNickname",
        "sampGetCurrentServerAddress": "sampGetCurrentServerAddress",
        "LuaObfuscator.com": "LuaObfuscator.com (L8)",
        "exec": "exec"
    }

    for key, label in danger_map.items():
        if key in content:
            pola_terdeteksi.append(label)

    return pola_terdeteksi, found_links

# ================= MODALS FOR FLOODING =================
class DiscordModal(discord.ui.Modal, title="🔵 Spam Discord Webhook"):
    url = discord.ui.TextInput(label="Webhook URL", placeholder="https://discord.com/api/webhooks/...", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        await start_flooding(interaction, "Discord Webhook", self.url.value)

class TeleAutoModal(discord.ui.Modal, title="✈️ Spam Telegram (Auto ID)"):
    token = discord.ui.TextInput(label="Bot Token", placeholder="123456:ABC-DEF...", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.telegram.org/bot{self.token.value}/getUpdates") as resp:
                data = await resp.json()
                if data.get("result") and len(data["result"]) > 0:
                    chat_id = data["result"][-1]["message"]["chat"]["id"]
                    await start_flooding(interaction, "Telegram Auto", self.token.value, chat_id)
                else:
                    await interaction.response.send_message("❌ Gagal mencari Chat ID secara otomatis. Pastikan bot sudah di-chat!", ephemeral=True)

class TeleManualModal(discord.ui.Modal, title="✈️ Spam Telegram (Manual)"):
    token = discord.ui.TextInput(label="Bot Token", required=True)
    chat_id = discord.ui.TextInput(label="Chat ID", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        await start_flooding(interaction, "Telegram Manual", self.token.value, self.chat_id.value)

# ================= FLOODING SYSTEM (DASHBOARD STYLE) =================
async def start_flooding(interaction, mode, target, chat_id=None):
    vips = load_vips()
    if interaction.user.id not in vips:
        return await interaction.response.send_message("❌ Fitur ini khusus VIP!", ephemeral=True)

    await interaction.response.send_message(f"🚀 Memproses target...", ephemeral=True)
    
    embed = discord.Embed(title="🎯 SA-MP Keylogger Counter", color=0xff0000)
    embed.add_field(name="🎯 Mode", value=f"🔵 {mode}", inline=True)
    embed.add_field(name="📊 Status", value="🔵 Berjalan", inline=True)
    embed.add_field(name="👤 Operator", value=f"**{interaction.user.name}**", inline=True)
    msg = await interaction.channel.send(embed=embed)

    success_count = 0
    async with aiohttp.ClientSession() as session:
        for i in range(1, 101):
            payload = {"content": generate_fake_data()} if "Discord" in mode else {"chat_id": chat_id, "text": generate_fake_data()}
            url = target if "Discord" in mode else f"https://api.telegram.org/bot{target}/sendMessage"
            
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status in [200, 204]: success_count += 1
                    elif resp.status == 429: await asyncio.sleep(5)
            except: break
            
            if i % 10 == 0 or i == 100:
                bar = "█" * (i // 10) + "░" * (10 - (i // 10))
                new_embed = embed.copy()
                new_embed.clear_fields()
                new_embed.add_field(name="🎯 Mode", value=f"🔵 {mode}", inline=True)
                new_embed.add_field(name="📊 Status", value="🔵 Berjalan" if i < 100 else "🔴 Selesai", inline=True)
                new_embed.add_field(name="👤 Operator", value=f"**{interaction.user.name}**", inline=True)
                new_embed.add_field(name="🛰️ Progress", value=f"{i}/100 pesan", inline=False)
                new_embed.add_field(name="📈 Hasil", value=f"✅ {success_count} terkirim ❌ {i-success_count} gagal", inline=True)
                new_embed.add_field(name="📊 Bar", value=f"[{bar}] {i}%", inline=False)
                await msg.edit(embed=new_embed)
            await asyncio.sleep(0.3)

# ================= UI PANEL MENU =================
class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Spam Discord", style=discord.ButtonStyle.primary, emoji="🔵")
    async def spam_discord(self, interaction, button):
        await interaction.response.send_modal(DiscordModal())

    @discord.ui.button(label="Spam Telegram", style=discord.ButtonStyle.primary, emoji="✈️")
    async def spam_tele(self, interaction, button):
        await interaction.response.send_modal(TeleAutoModal())

    @discord.ui.button(label="Telegram Manual", style=discord.ButtonStyle.secondary, emoji="✈️")
    async def tele_manual(self, interaction, button):
        await interaction.response.send_modal(TeleManualModal())

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⬛")
    async def stop_op(self, interaction, button):
        await interaction.response.send_message("🔴 Operasi dihentikan oleh operator.", ephemeral=True)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def preview_data(self, interaction, button):
        await interaction.response.send_message(f"**Contoh data yang dikirim:**\n{generate_fake_data()}", ephemeral=True)

# ================= BOT INITIALIZATION =================
class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot Online: {self.user}")

bot = TatangBot()

# ================= ALL SLASH COMMANDS =================
@bot.tree.command(name="menu", description="Dashboard Utama Tatang Bot")
async def menu(it: discord.Interaction):
    embed = discord.Embed(title="📄 TATANG BOT | DASHBOARD MENU", color=0x3498db)
    embed.description = "Pusat kendali fitur keamanan dan manajemen VIP server."
    embed.add_field(name="👑 **ADMINISTRATION**", value="`/addvip` • `/removevip` • `/listvip`", inline=False)
    embed.add_field(name="🛠️ **UTILITY**", value="`/status` • `/help` • `/createpanelwebhook`", inline=False)
    embed.add_field(name="🛡️ **SECURITY STATUS**", value=f"**Scanner:** Aktif ✅\n**Format:** .lua, .zip, .7z", inline=False)
    embed.set_footer(text="Premium Management System • v2.1")
    await it.response.send_message(embed=embed, view=MenuView())

@bot.tree.command(name="createpanelwebhook")
async def cpw(it: discord.Interaction):
    embed = discord.Embed(title="🎯 SA-MP Keylogger Counter", color=0xff0000)
    embed.description = (
        "Balas para pengedar keylogger SA-MP dengan **membanjiri channel mereka** "
        "menggunakan data palsu yang realistis.\n\n"
        "SA-MP Community Defender • Data 100% Palsu"
    )
    embed.set_footer(text="Official: youtube.com/@tatangchit")
    await it.response.send_message(embed=embed, view=MenuView())

@bot.tree.command(name="status")
async def status(it: discord.Interaction):
    ram, ping = psutil.virtual_memory().percent, round(bot.latency * 1000)
    embed = discord.Embed(title="🚀 SYSTEM STATUS", color=0x2ecc71)
    embed.add_field(name="RAM Usage", value=f"{ram}%", inline=True)
    embed.add_field(name="Bot Latency", value=f"{ping}ms", inline=True)
    await it.response.send_message(embed=embed)

@bot.tree.command(name="help")
async def help_cmd(it: discord.Interaction):
    embed = discord.Embed(title="❓ PANDUAN DEEP SCANNER", color=0x9b59b6)
    embed.add_field(name="1. Upload File", value="Kirim file `.lua`, `.zip`, atau `.7z` di <#1469740150522380299>.", inline=False)
    embed.add_field(name="2. Analisis Pola", value="Bot akan membongkar file dan mencari link Webhook atau Stealer.", inline=False)
    embed.set_footer(text="Support: youtube.com/@tatangchit")
    await it.response.send_message(embed=embed)

@bot.tree.command(name="addvip")
async def addvip(it: discord.Interaction, member: discord.Member):
    role = it.guild.get_role(ADMIN_ROLE_ID)
    if role not in it.user.roles and not it.user.guild_permissions.administrator:
        return await it.response.send_message("❌ No Permission", ephemeral=True)
    vips = load_vips()
    if member.id not in vips:
        vips.append(member.id); save_vips(vips)
        await it.response.send_message(f"✅ {member.mention} Berhasil menjadi VIP!")
    else: await it.response.send_message("User sudah VIP.", ephemeral=True)

@bot.tree.command(name="listvip")
async def listvip(it: discord.Interaction):
    vips = load_vips()
    mentions = "\n".join([f"• <@{uid}>" for uid in vips]) if vips else "Database Kosong."
    await it.response.send_message(embed=discord.Embed(title="👑 DATABASE VIP", description=mentions, color=0xf1c40f))

# ================= SCANNER LOGIC (ORIGINAL TAMPILAN) =================
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

            pola, links = list(set(pola)), list(set(links))
            if links:
                status, color, conf = "🔴 🚨 BAHAYA TINGGI", 0xff0000, "75%"
                analisis_msg = f"Ditemukan {len(links)} link webhook berbahaya."
            elif len(pola) >= 2:
                status, color, conf = "🟠 ⚠️ SANGAT MENCURIGAKAN", 0xe67e22, "75%"
                analisis_msg = f"Ditemukan {len(pola)} pola mencurigakan."
            elif len(pola) == 1:
                status, color, conf = "🟡 🤔 MENCURIGAKAN", 0xf1c40f, "75%"
                analisis_msg = "Ditemukan 1 pola mencurigakan."
            else:
                status, color, conf = "✅ 🛡️ AMAN", 0x2ecc71, "85%"
                analisis_msg = "Analisis manual tidak menemukan pola berbahaya."

            embed = discord.Embed(title=status, color=color)
            embed.description = (
                f"**File:** `{attachment.filename}`\n"
                f"**Analisis:** {analisis_msg}\n\n🎯 **Confidence**\n{conf}\n\n"
                f"📊 **Info**\nSize: {len(file_data):,} bytes"
            )

            if pola: embed.add_field(name="📝 Pola Terdeteksi", value="\n".join([f"• {p}" for p in pola]), inline=False)
            if links: embed.add_field(name="🌐 Webhook Found", value="\n".join([f"🔗 [KLIK LINK]({l})" for l in links]), inline=False)
            embed.set_footer(text=f"Check: {files_count} file(s) | youtube.com/@tatangchit")
            await message.reply(embed=embed)
            await message.remove_reaction("⏳", bot.user)

bot.run(TOKEN)
