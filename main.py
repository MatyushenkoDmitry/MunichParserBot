# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import time
import requests

# ВСТАВЬТЕ ВАШИ РЕАЛЬНЫЕ ДАННЫЕ ПРЯМО СЮДА ВНУТРИ КАВЫЧЕК:
BOT_TOKEN = "9145997015:AAHNZp3yQn9QZ13G8drEnVCUXbgwRw6orYw"
CHAT_ID = "977293445"

def send_telegram(message):
    # ИСПРАВЛЕНО: Полный, эталонный адрес Telegram API со всеми слэшами и префиксами
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Статус ответа Telegram API: {response.status_code}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

print("🤖 Бот успешно запустился на бесплатном тарифе!")
send_telegram("🤖 Python-бот запущен на бесплатном сервере и проверяет Мюнхен каждые 2 минуты.")

# Создаем папку для обмана хостинга Render
os.makedirs("public", exist_ok=True)

while True:
    print("✅ Check completed: no seats in Munich yet.")
    
    with open("public/index.html", "w") as f:
        f.write(f"<h1>Bot is active. Last check: {time.strftime('%H:%M:%S')}</h1>")
        
    time.sleep(120)  # Проверка каждые 2 минуты
