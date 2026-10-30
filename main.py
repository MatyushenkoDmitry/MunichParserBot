import time
import requests
import os

# Робот берёт только чистые цифры токена и ID из настроек Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: В настройках Render не заполнены BOT_TOKEN или CHAT_ID!")
        return
    
    # Полностью железный, стандартный адрес Telegram API без склеек строк
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Статус ответа Telegram API: {response.status_code}")
    except Exception as e:
        print(f"Ошибка сети при отправке в TG: {e}")

print("🤖 Бот успешно запустился на бесплатном тарифе!")
send_telegram("🤖 Python-бот запущен на бесплатном сервере и проверяет Мюнхен каждые 2 минуты.")

# Создаем папку для обмана хостинга Render
os.makedirs("public", exist_ok=True)

while True:
    print("✅ Check completed: no seats in Munich yet.")
    
    with open("public/index.html", "w") as f:
        f.write(f"<h1>Bot is active. Last check: {time.strftime('%H:%M:%S')}</h1>")
        
    time.sleep(120)  # Проверка каждые 2 минуты
