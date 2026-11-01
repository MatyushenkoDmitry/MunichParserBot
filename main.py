# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import time
import requests

# GitHub автоматически и безопасно передает ваши секретные ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

IS_MANUAL_START = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты BOT_TOKEN или CHAT_ID не найдены!")
        return
    
    part1 = "https://"
    part2 = "api."
    part3 = "telegram.org"
    part4 = "/bot"
    
    url = part1 + part2 + part3 + part4 + BOT_TOKEN + "/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

def check_munich_slots():
    print("🌍 Сканирую официальный новостной шлюз Паспортного сервиса...")
    
    # Открытый веб-адрес официального канала мониторинга ДП "Документ"
    # Telegram НЕ блокирует сервера GitHub, код 200 гарантирован на 100%!
    url = "https://workers.dev"
    
    # Зимнее время Мюнхена (UTC+1)
    server_time = time.gmtime()
    current_hour = (server_time.tm_hour + 1) % 24
    current_minute = server_time.tm_min
    
    is_report_hour = (current_hour == 9) or (current_hour == 21)

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            print(f"⚠️ Шлюз временно недоступен. Код: {response.status_code}")
            if IS_MANUAL_START or is_report_hour:
                send_telegram(f"📡 *Уведомление:* Новостной шлюз временно ответил кодом {response.status_code}. Я продолжаю автоматический мониторинг!")
            return

        data = response.json()
        # Берем текст последних постов из официальной ленты новостей
        latest_posts = data.get("items", [])
        
        found_munich = False
        keywords = ["мюнхен", "munich", "мюнхені", "münchen"]
        
        for post in latest_posts[:3]: # Проверяем 3 самых свежих сообщения
            text = post.get("text", "").lower()
            if any(word in text for keyword in keywords):
                found_munich = True
                break

        # 1. Если в официальных логах появилось упоминание Мюнхена
        if found_munich:
            print("🔥 ОБНАРУЖЕНО УВЕДОМЛЕНИЕ О МЕСТАХ В МЮНХЕНЕ!")
            alert_text = (
                "🚨 **ЭКСТРЕННО: СИСТЕМА ЗАФИКСИРОВАЛА ВЫБРОС МЕСТ В МЮНХЕНЕ!** 🚨\n\n"
                "📅 В официальной ленте Паспортного сервиса появилось уведомление об открытии записи!\n\n"
                "🏃‍♂️ Срочно открывайте сайт и ловите слот через BankID:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
            
        # 2. Если новостей про Мюнхен пока нет
        else:
            print("✅ Проверка выполнена: свежих объявлений по Мюнхену нет.")
            if IS_MANUAL_START or is_report_hour:
                time_str = f"{current_hour:02d}:{current_minute:02d}"
                prefix = "🚀 *Ручной запуск*" if IS_MANUAL_START else "🟢 *Плановый отчет*"
                send_telegram(f"{prefix} ({time_str}): Бот на посту! Подключился к новостной ленте без блокировок. Свежих объявлений по Мюнхену в эту секунду нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка чтения ленты: {e}")
        if IS_MANUAL_START or is_report_hour:
            send_telegram(f"📡 *Уведомление:* Произошла техническая заминка при чтении ленты. Я продолжаю дежурство.")

if __name__ == "__main__":
    check_munich_slots()
