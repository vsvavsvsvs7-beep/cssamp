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

# ================= KONFIGURASI ID =================
TOKEN = os.getenv("TOKEN")
SCAN_CHANNEL_ID = 1469740150522380299      # Channel khusus Scanner
PANEL_CHANNEL_ID = 1471935338065694875     # Channel khusus /panel
REQ_VIP_CHANNEL_ID = 1472535677634740398   
ADMIN_ROLE_ID = 1471265207945924619        
VIP_FILE = "vips.json"

# ================= UTILITY =================
def load_vips():
    if not os.path.exists(VIP_FILE):
        with open(VIP_FILE, "w") as f: json.dump([], f)
    try:
        with open(VIP_FILE, "r") as f: return json.load(f)
    except: return []

def save_vips(vips):
    with open(VIP_FILE, "w") as f: json.dump(vips, f)

def generate_fake_data():
    nicks = ["Dika_Ganteng", "Admin_SAMP", "Player_Pro", "Tatang_Sakti", "Bocah_SAMP", "Rizky_Gaming"]
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
        "os.execute": "os.execute (Potensi RCE)", 
        "io.popen": "io.popen (Eksekusi System)", 
        "loadstring": "loadstring (Obfuscated Code)",
        "sampGetPlayerNickname": "sampGetPlayerNickname (Data Logger)", 
        "sampGetCurrentServerAddress": "Server Address Logger",
        "LuaObfuscator.com": "LuaObfuscator (L8 Detected)", 
        "exec": "exec"
    }
    for key, label in danger_map.items():
        if key in content: pola_terdeteksi.append(label)
    return pola_terdeteksi, found_links

# ================= FLOODING UI & LOGIC =================
class DiscordModal(discord.ui.Modal, title="🔵 Spam Discord Webhook"):
    url = discord.ui.TextInput(label="Webhook URL", placeholder="https://discord.com/api/webhooks/...", required=True)
    async def on_submit(self, it: discord.Interaction): await start_flood(it, "Discord Webhook", self.url.value)

class TeleAutoModal(discord.ui.Modal, title="✈️ Spam Telegram (Auto ID)"):
    token = discord.ui.TextInput(label="Bot Token", placeholder="123456:ABC-DEF...", required=True)
    async def on_submit(self, it: discord.Interaction):
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://api.telegram.org/bot{self.token.value}/getUpdates") as r:
                d = await r.json()
                if d.get("result") and len(d["result"]) > 0:
                    cid = d["result"][-1]["message"]["chat"]["id"]
                    await start_flood(it, "Telegram Auto", self.token.value, cid)
                else: await it.response.send_message("❌ Gagal cari Chat ID secara otomatis. Pastikan bot sudah dikirim pesan!", ephemeral=True)

class TeleManualModal(discord.ui.Modal, title="✈️ Spam Telegram (Manual)"):
    token = discord.ui.TextInput(label="Bot Token", required=True)
    cid = discord.ui.TextInput(label="Chat ID", required=True)
    async def on_submit(self, it: discord.Interaction): await start_flood(it, "Telegram Manual", self.token.value, self.cid.value)

async def start_flood(it, mode, target, cid=None):
    await it.response.send_message("🚀 Memulai operasi counter...", ephemeral=True)
    embed = discord.Embed(title="🎯 SA-MP Keylogger Counter", color=0xff0000)
    embed.add_field(name="🎯 Mode", value=f"🔵 {mode}", inline=True)
    embed.add_field(name="📊 Status", value="🔵 Berjalan", inline=True)
    embed.add_field(name="👤 Operator", value=f"**{it.user.name}**", inline=True)
    msg = await it.channel.send(embed=embed)
    
    success = 0
    async with aiohttp.ClientSession() as s:
        for i in range(1, 101):
            p = {"content": generate_fake_data()} if "Discord" in mode else {"chat_id": cid, "text": generate_fake_data()}
            u = target if "Discord" in mode else f"https://api.telegram.org/bot{target}/sendMessage"
            try:
                async with s.post(u, json=p) as r:
                    if r.status in [200, 204]: success += 1
                    elif r.status == 429: await asyncio.sleep(5)
            except: break
            
            if i % 10 == 0 or i == 100:
                bar = "█" * (i // 10) + "░" * (10 - (i // 10))
                e = embed.copy()
                e.clear_fields()
                e.add_field(name="🎯 Mode", value=f"🔵 {mode}", inline=True)
                e.add_field(name="📊 Status", value="🔵 Berjalan" if i < 100 else "🔴 Dihentikan", inline=True)
                e.add_field(name="👤 Operator", value=f"**{it.user.name}**", inline=True)
                e.add_field(name="🛰️ Progress", value=f"{i}/100 pesan", inline=False)
                e.add_field(name="📈 Hasil", value=f"✅ {success} terkirim ❌ {i-success} gagal", inline=True)
                e.add_field(name="📊 Bar", value=f"[{bar}] {i}%", inline=False)
                await msg.edit(embed=e)
            await asyncio.sleep(0.3)

class PanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Spam Discord", style=discord.ButtonStyle.primary, emoji="🔵")
    async def d(self, it, b): await it.response.send_modal(DiscordModal())
    @discord.ui.button(label="Spam Telegram", style=discord.ButtonStyle.primary, emoji="✈️")
    async def t(self, it, b): await it.response.send_modal(TeleAutoModal())
    @discord.ui.button(label="Telegram Manual", style=discord.ButtonStyle.secondary, emoji="✈️")
    async def tm(self, it, b): await it.response.send_modal(TeleManualModal())
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⬛")
    async def s(self, it, b): await it.response.send_message("🔴 Operasi dihentikan oleh operator.", ephemeral=True)
    @discord.ui.button(label="Preview", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def p(self, it, b): await it.response.send_message(f"**Contoh data yang dikirim:**\n{generate_fake_data()}", ephemeral=True)

# ================= BOT INITIALIZATION =================
class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="/", intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = TatangBot()

# ================= SLASH COMMANDS =================

@bot.tree.command(name="menu", description="Daftar lengkap perintah bot")
async def menu_cmd(it: discord.Interaction):
    embed = discord.Embed(title="📄 TATANG BOT | PREMIUM DASHBOARD", color=0x3498db)
    embed.description = "Sistem keamanan dan utilitas untuk komunitas SA-MP Indonesia."
    
    embed.add_field(
        name="👑 **ADMINISTRATION (Admin Only)**", 
        value="• `/addvip` : Menambah user ke database VIP\n• `/removevip` : Menghapus akses VIP user\n• `/listvip` : Melihat semua daftar VIP aktif", 
        inline=False
    )
    embed.add_field(
        name="🛡️ **SECURITY & TOOLS**", 
        value=f"• `/panel` : Panel flooding (Khusus VIP & Channel <#{PANEL_CHANNEL_ID}>)\n• `/status` : Cek kesehatan mesin bot\n• `/help` : Panduan lengkap penggunaan scanner", 
        inline=False
    )
    embed.add_field(
        name="⚡ **DEEP SCANNER**", 
        value=f"Kirim file `.lua`, `.zip`, atau `.7z` di channel <#{SCAN_CHANNEL_ID}> untuk analisis otomatis.", 
        inline=False
    )
    
    embed.set_footer(text="Official Tatang Bot • youtube.com/@tatangchit")
    await it.response.send_message(embed=embed)

@bot.tree.command(name="panel", description="Buka Panel Spam Keylogger (VIP ONLY)")
async def panel_cmd(it: discord.Interaction):
    # Cek VIP
    if it.user.id not in load_vips():
        embed = discord.Embed(title="🔒 PREMIUM ACCESS REQUIRED", color=0xf1c40f)
        embed.description = "Fitur **Spam Panel** hanya dapat diakses oleh user **VIP**."
        return await it.response.send_message(embed=embed, ephemeral=True)
    
    # Cek Channel Khusus
    if it.channel_id != PANEL_CHANNEL_ID:
        return await it.response.send_message(f"❌ Command ini hanya bisa digunakan di channel <#{PANEL_CHANNEL_ID}>", ephemeral=True)

    embed = discord.Embed(title="🎯 SA-MP Keylogger Counter", color=0xff0000)
    embed.description = (
        "Balas para pengedar keylogger SA-MP dengan **membanjiri channel mereka** menggunakan data palsu.\n"
        "--------------------------------------------------\n"
        "📜 **CARA PENGGUNAAN**\n"
        "🔵 **Spam Discord** — Input Webhook URL target.\n"
        "✈️ **Spam Telegram** — Input Bot Token, bot otomatis cari Chat ID.\n"
        "✈️ **Telegram Manual** — Input Bot Token & Chat ID secara manual.\n"
        "⬛ **Stop** — Menghentikan operasi flooding seketika.\n"
        "👁️ **Preview** — Melihat contoh data palsu yang akan dikirim.\n\n"
        "**Note:** Gunakan dengan bijak untuk membasmi stealer!"
    )
    embed.set_footer(text="SA-MP Community Defender • Data 100% Palsu")
    await it.response.send_message(embed=embed, view=PanelView())

@bot.tree.command(name="help", description="Panduan lengkap penggunaan bot")
async def help_cmd(it: discord.Interaction):
    embed = discord.Embed(title="❓ PANDUAN LENGKAP TATANG BOT", color=0x9b59b6)
    
    embed.add_field(
        name="🛡️ Cara Kerja Scanner", 
        value=(
            "1. Masuk ke channel khusus scanner.\n"
            "2. Upload file (Lua, Zip, atau 7z).\n"
            "3. Bot akan memberikan reaksi ⏳ dan membongkar file.\n"
            "4. Jika ditemukan link Webhook atau pola stealer, bot akan menandai file tersebut sebagai **BAHAYA**."
        ), 
        inline=False
    )
    embed.add_field(
        name="🚀 Cara Kerja Panel Spam", 
        value=(
            "1. Pastikan kamu memiliki status **VIP**.\n"
            "2. Gunakan `/panel` di channel khusus spam.\n"
            "3. Pilih target (Discord/Telegram) dan masukkan data yang diminta.\n"
            "4. Bot akan mengirim 100 data palsu secara otomatis untuk merusak database penipu."
        ), 
        inline=False
    )
    
    embed.set_footer(text="Bantu kami membasmi keylogger! youtube.com/@tatangchit")
    await it.response.send_message(embed=embed)

@bot.tree.command(name="addvip")
async def add_vip(it: discord.Interaction, member: discord.Member):
    if not it.user.guild_permissions.administrator: return await it.response.send_message("❌ Hanya Admin yang bisa menambah VIP.", ephemeral=True)
    vips = load_vips()
    if member.id not in vips:
        vips.append(member.id); save_vips(vips)
        embed = discord.Embed(title="✨ VIP ACCESS GRANTED", color=0x2ecc71)
        embed.description = f"{member.mention} Berhasil menjadi VIP! ✅"
        await it.response.send_message(embed=embed)
    else: await it.response.send_message(f"{member.name} sudah ada di database VIP.", ephemeral=True)

@bot.tree.command(name="status")
async def status_cmd(it: discord.Interaction):
    embed = discord.Embed(title="🚀 SYSTEM STATUS", color=0x2ecc71)
    embed.add_field(name="RAM Usage", value=f"{psutil.virtual_memory().percent}%", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.set_footer(text="Bot berjalan lancar di server.")
    await it.response.send_message(embed=embed)

# ================= SCANNER EVENT =================
@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != SCAN_CHANNEL_ID: return
    if message.attachments:
        if message.author.id not in load_vips():
            embed = discord.Embed(title="🔒 PREMIUM ACCESS REQUIRED", color=0xf1c40f)
            embed.description = f"Halo {message.author.mention}, fitur **Deep Scanner** hanya untuk VIP.\n\n🛡️ **Minta Akses:** <#{REQ_VIP_CHANNEL_ID}>"
            return await message.reply(embed=embed)
        
        for attachment in message.attachments:
            ext = os.path.splitext(attachment.filename)[1].lower()
            if ext not in [".lua", ".txt", ".zip", ".7z"]: continue
            
            await message.add_reaction("⏳")
            file_data = await attachment.read(); pola, links, files_count = [], [], 0
            
            try:
                if ext in [".lua", ".txt"]:
                    c = file_data.decode(errors="ignore"); p, l = analyze_content(c)
                    pola.extend(p); links.extend(l); files_count = 1
                elif ext == ".zip":
                    with zipfile.ZipFile(io.BytesIO(file_data)) as z:
                        for f in z.namelist():
                            if f.lower().endswith((".lua", ".txt")):
                                c = z.read(f).decode(errors="ignore"); p, l = analyze_content(c); pola.extend(p); links.extend(l); files_count += 1
                elif ext == ".7z":
                    with py7zr.SevenZipFile(io.BytesIO(file_data), mode='r') as z:
                        names = [n for n in z.getnames() if n.lower().endswith((".lua", ".txt"))]
                        if names:
                            contents = z.read(names)
                            for name, bio in contents.items():
                                c = bio.read().decode(errors="ignore"); p, l = analyze_content(c); pola.extend(p); links.extend(l); files_count += 1
            except: pass

            pola, links = list(set(pola)), list(set(links))
            if links:
                status, color, conf = "🔴 🚨 BAHAYA TINGGI", 0xff0000, "100%"
                msg_ana = f"Ditemukan {len(links)} link webhook stealer aktif!"
            elif pola:
                status, color, conf = "🟠 ⚠️ SANGAT MENCURIGAKAN", 0xe67e22, "75%"
                msg_ana = f"Ditemukan {len(pola)} pola instruksi berbahaya."
            else:
                status, color, conf = "✅ 🛡️ AMAN", 0x2ecc71, "85%"
                msg_ana = "Tidak ditemukan indikasi keylogger secara otomatis."

            embed = discord.Embed(title=status, color=color)
            embed.description = (
                f"**File:** `{attachment.filename}`\n"
                f"**Analisis:** {msg_ana}\n\n"
                f"🎯 **Confidence**\n{conf}\n\n"
                f"📊 **Info**\nSize: {len(file_data):,} bytes"
            )
            if pola: embed.add_field(name="📝 Pola Terdeteksi", value="\n".join([f"• {p}" for p in pola]), inline=False)
            if links: embed.add_field(name="🌐 Webhook Found", value="\n".join([f"🔗 [KLIK LINK]({l})" for l in links]), inline=False)
            
            embed.set_footer(text=f"Analisis Selesai: {files_count} file | youtube.com/@tatangchit")
            await message.reply(embed=embed)
            await message.remove_reaction("⏳", bot.user)

bot.run(TOKEN)
