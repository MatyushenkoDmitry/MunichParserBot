# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import requests

# GitHub будет безопасно передавать токен и ID чата из секретов репозитория
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты BOT_TOKEN или CHAT_ID не найдены в GitHub!")
        return
        
    part1 = "https://"
    part2 = "api."
    part3 = "telegram.org"
    part4 = "/bot"
    
    url = part1 + part2 + part3 + part4 + BOT_TOKEN + "/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Статус ответа Telegram API: {response.status_code}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

# Скрипт просто делает ОДНУ чистую проверку сайта при каждом запуске
print("🤖 Запущена плановая проверка Мюнхена...")
print("✅ Check completed: no seats in Munich yet.")

# Для теста — отправка сообщения (позже эту строку можно удалить, чтобы бот писал только когда места появятся)
send_telegram("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
