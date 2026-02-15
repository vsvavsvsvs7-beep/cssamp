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

# ================= KONFIGURASI =================
TOKEN = os.getenv("TOKEN")
SCAN_CHANNEL_ID = 1469740150522380299      
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

# ================= FLOODING UI & MODALS =================
class DiscordModal(discord.ui.Modal, title="🔵 Spam Discord Webhook"):
    url = discord.ui.TextInput(label="Webhook URL", placeholder="https://discord.com/api/webhooks/...", required=True)
    async def on_submit(self, it: discord.Interaction): await start_flood(it, "Discord Webhook", self.url.value)

class TeleAutoModal(discord.ui.Modal, title="✈️ Spam Telegram (Auto ID)"):
    token = discord.ui.TextInput(label="Bot Token", placeholder="123456:ABC-DEF...", required=True)
    async def on_submit(self, it: discord.Interaction):
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://api.telegram.org/bot{self.token.value}/getUpdates") as r:
                d = await r.json()
                if d.get("result"):
                    cid = d["result"][-1]["message"]["chat"]["id"]
                    await start_flood(it, "Telegram Auto", self.token.value, cid)
                else: await it.response.send_message("❌ Gagal cari Chat ID.", ephemeral=True)

class TeleManualModal(discord.ui.Modal, title="✈️ Spam Telegram (Manual)"):
    token = discord.ui.TextInput(label="Bot Token", required=True)
    cid = discord.ui.TextInput(label="Chat ID", required=True)
    async def on_submit(self, it: discord.Interaction): await start_flood(it, "Telegram Manual", self.token.value, self.cid.value)

async def start_flood(it, mode, target, cid=None):
    if it.user.id not in load_vips(): return await it.response.send_message("❌ Khusus VIP!", ephemeral=True)
    await it.response.send_message("🚀 Memulai...", ephemeral=True)
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
                e.add_field(name="📊 Bar", value=f"{bar} {i}%", inline=False)
                await msg.edit(embed=e)
            await asyncio.sleep(0.3)

class PanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Spam Discord", style=discord.ButtonStyle.primary)
    async def d(self, it, b): await it.response.send_modal(DiscordModal())
    @discord.ui.button(label="Spam Telegram", style=discord.ButtonStyle.primary)
    async def t(self, it, b): await it.response.send_modal(TeleAutoModal())
    @discord.ui.button(label="Telegram Manual", style=discord.ButtonStyle.secondary)
    async def tm(self, it, b): await it.response.send_modal(TeleManualModal())
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def s(self, it, b): await it.response.send_message("🔴 Operasi dihentikan.", ephemeral=True)
    @discord.ui.button(label="Preview", style=discord.ButtonStyle.secondary)
    async def p(self, it, b): await it.response.send_message(generate_fake_data(), ephemeral=True)

# ================= BOT CORE =================
class TatangBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="/", intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = TatangBot()

@bot.tree.command(name="menu", description="Lihat semua perintah")
async def menu_cmd(it: discord.Interaction):
    embed = discord.Embed(title="📄 TATANG BOT | MENU", color=0x3498db)
    embed.add_field(name="👑 ADMIN", value="`/addvip` • `/removevip` • `/listvip`", inline=False)
    embed.add_field(name="🛠️ TOOLS", value="`/panel` • `/status` • `/help`", inline=False)
    await it.response.send_message(embed=embed)

@bot.tree.command(name="panel", description="Buka Panel Spam Webhook")
async def panel_cmd(it: discord.Interaction):
    embed = discord.Embed(title="🎯 SA-MP Keylogger Counter", color=0xff0000)
    embed.description = (
        "Balas para pengedar keylogger SA-MP dengan **membanjiri channel mereka** menggunakan data palsu.\n"
        "--------------------------------------\n"
        "📜 **Cara Pakai**\n"
        "🔵 **Spam Discord** — input webhook URL target\n"
        "✈️ **Spam Telegram** — input token -> bot auto-cari chat ID!\n"
        "✈️ **Telegram Manual** — input token + chat ID sendiri\n"
        "⬛ **Stop** — hentikan operasi\n"
        "👁️ **Preview** — lihat contoh data yang dikirim\n\n"
        "SA-MP Community Defender • Semua user bisa ikut membantu • Data 100% Palsu"
    )
    await it.response.send_message(embed=embed, view=PanelView())

@bot.tree.command(name="help", description="Panduan Scan & Spam")
async def help_cmd(it: discord.Interaction):
    embed = discord.Embed(title="❓ CARA PAKAI BOT", color=0x9b59b6)
    embed.add_field(name="🛡️ Scan Keylogger", value=f"Kirim file .lua/.zip di <#{SCAN_CHANNEL_ID}>. Khusus VIP.", inline=False)
    embed.add_field(name="🎯 Spam Webhook", value="Gunakan `/panel` untuk membanjiri log penipu.", inline=False)
    await it.response.send_message(embed=embed)

@bot.tree.command(name="addvip")
async def add_vip(it: discord.Interaction, member: discord.Member):
    if not it.user.guild_permissions.administrator: return await it.response.send_message("❌ Admin only", ephemeral=True)
    vips = load_vips()
    if member.id not in vips:
        vips.append(member.id); save_vips(vips)
        embed = discord.Embed(title="✨ VIP ACCESS GRANTED", color=0x2ecc71)
        embed.description = f"{member.mention} Berhasil menjadi VIP! ✅"
        await it.response.send_message(embed=embed)

@bot.tree.command(name="status")
async def status_cmd(it: discord.Interaction):
    embed = discord.Embed(title="🚀 SYSTEM STATUS", color=0x2ecc71)
    embed.add_field(name="RAM", value=f"{psutil.virtual_memory().percent}%")
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms")
    await it.response.send_message(embed=embed)

# ================= SCANNER LOGIC (TAMPILAN TETAP ASLI) =================
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
            file_data = await attachment.read(); pola, links, count = [], [], 0
            try:
                if ext in [".lua", ".txt"]:
                    c = file_data.decode(errors="ignore"); p, l = analyze_content(c)
                    pola.extend(p); links.extend(l); count = 1
                elif ext == ".zip":
                    with zipfile.ZipFile(io.BytesIO(file_data)) as z:
                        for f in z.namelist():
                            if f.lower().endswith((".lua", ".txt")):
                                c = z.read(f).decode(errors="ignore"); p, l = analyze_content(c); pola.extend(p); links.extend(l); count += 1
                elif ext == ".7z":
                    with py7zr.SevenZipFile(io.BytesIO(file_data), mode='r') as z:
                        names = [n for n in z.getnames() if n.lower().endswith((".lua", ".txt"))]
                        if names:
                            contents = z.read(names)
                            for name, bio in contents.items():
                                c = bio.read().decode(errors="ignore"); p, l = analyze_content(c); pola.extend(p); links.extend(l); count += 1
            except: pass
            pola, links = list(set(pola)), list(set(links))
            status, color = ("🔴 🚨 BAHAYA TINGGI", 0xff0000) if links else (("🟠 ⚠️ MENCURIGAKAN", 0xe67e22) if pola else ("✅ 🛡️ AMAN", 0x2ecc71))
            embed = discord.Embed(title=status, color=color)
            embed.description = f"**File:** `{attachment.filename}`\n**Analisis:** {'Ditemukan link' if links else 'Pola berbahaya' if pola else 'Aman'}\n\n🎯 **Confidence**\n{ '100%' if links else '75%' }\n\n📊 **Info**\nSize: {len(file_data)} bytes"
            if pola: embed.add_field(name="📝 Pola", value="\n".join(pola))
            if links: embed.add_field(name="🔗 Webhook", value="\n".join(links))
            embed.set_footer(text=f"Check: {count} file | youtube.com/@tatangchit")
            await message.reply(embed=embed)
            await message.remove_reaction("⏳", bot.user)

bot.run(TOKEN)
