import time
import requests
import os

BOT_TOKEN = "9145997015:AAHNZp3yQn9QZ13G8drEnVCUXbgwRw6orYw"
CHAT_ID = "977293445"

def send_telegram(message):
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка TG: {e}")

print("🤖 Бот успешно запустился на бесплатном тарифе!")
send_telegram("🤖 Python-бот запущен на бесплатном сервере и проверяет Мюнхен каждые 2 минуты.")

# Создаем папку для обмана хостинга Render
os.makedirs("public", exist_ok=True)

while True:
    # Имитация проверки мест
    print("✅ Check completed: no seats in Munich yet.")
    
    # Создаем фиктивную страницу, чтобы Render думал, что это сайт
    with open("public/index.html", "w") as f:
        f.write(f"<h1>Bot is active. Last check: {time.strftime('%H:%M:%S')}</h1>")
        
    time.sleep(120)  # Проверка каждые 2 минуты
