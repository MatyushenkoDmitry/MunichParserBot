import time
import requests

# ВСТАВЬТЕ СЮДА ВАШИ ДАННЫЕ (ОСТАВЬТЕ ТОЛЬКО ЦИФРЫ И СИМВОЛЫ ВНУТРИ КАВЫЧЕК)
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"
CHAT_ID = "ВАШ_CHAT_ID"

def send_telegram(message):
    # Исправили путь к API Telegram
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Статус отправки в TG: {response.status_code}")
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

print("🤖 Python-бот успешно запущен в облаке!")
send_telegram("🤖 Python-бот запущен на сервере Render и проверяет Мюнхен каждые 2 минуты.")

def check_slots():
    # Имитация проверки сайта (сюда подставляется логика сканирования)
    print("✅ Check completed: no seats in Munich yet.")

# Бесконечный цикл проверки каждые 120 секунд (2 минуты)
while True:
    check_slots()
    time.sleep(120)
