import os
import requests
from aiohttp import web

from dotenv import load_dotenv

load_dotenv("b.env")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SECRET = os.getenv("SECRET", "supersecret")

current_sub = "Неизвестно"


# 🚀 отправка в Discord
def send_discord(message):
    try:
        r = requests.post(WEBHOOK_URL, json={"content": message}, timeout=5)
        print("→ Discord:", r.status_code)
    except Exception as e:
        print("❌ ошибка отправки:", e)


# 🌐 обработка событий от Bridge
async def handle_event(request):
    global current_sub

    try:
        data = await request.json()
        print("EVENT:", data)

        # 🔐 проверка ключа
        if data.get("key") != SECRET:
            return web.Response(text="forbidden", status=403)

        event = data.get("event")
        sub = data.get("sub")

        if sub:
            current_sub = sub

        # 🌊 старт
        if event == "start":
            send_discord(f"🌊 Корабль **{current_sub}** отправился в поход")

        # ⚓ успешное завершение
        elif event == "end_success":
            send_discord(f"⚓ Корабль **{current_sub}** добрался до аванпоста")

        # ⚠️ любое другое завершение
        elif event == "end_fail":
            send_discord(f"⚠️ Корабль **{current_sub}** пропал без вести")

        return web.Response(text="ok")

    except Exception as e:
        print("❌ ошибка:", e)
        return web.Response(text="error", status=500)


# ❤️ ping (для UptimeRobot)
async def health_check(request):
    return web.Response(text="ok")


# 🚀 запуск сервера
app = web.Application()
app.router.add_post('/event', handle_event)
app.router.add_get('/', health_check)

port = int(os.getenv("PORT", 5000))
web.run_app(app, host="0.0.0.0", port=port)
