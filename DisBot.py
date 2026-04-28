import time
import discord
import asyncio
from aiohttp import web
import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv

# 🔹 загрузка .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
SERVER_EXE = os.getenv("SERVER_EXE", "DedicatedServer.exe")
SECRET = os.getenv("SECRET")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# 🔧 НАСТРОЙКИ
CHANNELS = {
    "public": int(os.getenv("CHANNEL_PUBLIC")),
    #"extended": int(os.getenv("CHANNEL_EXTENDED")),
    "admin": int(os.getenv("CHANNEL_ADMIN"))
}

LEVELS = {
    "basic": ["public", "admin"],
    "admin": ["admin"]
}

# 🧠 Анти-дубль
last_events = {}

# 📤 УНИВЕРСАЛЬНАЯ ОТПРАВКА
async def send_by_level(level, message):
    targets = LEVELS.get(level, [])

    for key in targets:
        channel_id = CHANNELS.get(key)
        if not channel_id:
            continue

        try:
            channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
            await channel.send(message)
        except Exception as e:
            print(f"Ошибка отправки в {key}:", e)

def is_duplicate(key, cooldown=2):
    now = time.time()

    if key in last_events and now - last_events[key] < cooldown:
        return True

    last_events[key] = now
    return False

# 🌐 HTTP обработчик
async def handle_event(request):
    try:
        data = await request.json()
    except:
        return web.Response(status=400)

    # 🔐 проверка ключа
    if data.get("key") != SECRET:
        return web.Response(status=403)

    event = data.get("event")
    sub = data.get("sub", "Неизвестно")

    print("EVENT:", data)

    # 🧠 анти-дубли
    if is_duplicate(f"{event}:{sub}"):
        return web.Response(text="duplicate")

    # 🟢 старт
    if event == "start":
        await send_by_level("basic", f"🌊 Корабль **{sub}** отправился в поход")

    # ✅ успех
    elif event == "end_success":
        await send_by_level("basic", f"⚓ Корабль **{sub}** добрался до аванпоста")

    # 🔴 провал
    elif event == "end_fail":
        await send_by_level("basic", f"⚓ Корабль **{sub}** пропал без вести")

    return web.Response(text="ok")


# ❤️ health-check (для Render/VPS)
async def ping(request):
    return web.Response(text="ok")


# 🌐 запуск HTTP
async def start_web():
    app = web.Application()
    app.router.add_post('/event', handle_event)
    app.router.add_get('/', ping)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 5000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    async def ping(request):
        return web.Response(text="ok")

    print(f"HTTP сервер запущен на {port}")


# 🚀 запуск бота
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    bot.loop.create_task(start_web())


bot.run(TOKEN)