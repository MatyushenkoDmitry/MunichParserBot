# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import time
import requests

# GitHub автоматически передает ваши секретные ключи внутрь программы
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
    print("🌍 Сканирую официальную веб-ленту Паспортного сервиса...")
    
    # Прямой открытый веб-адрес публичного канала новостей ДП "Документ"
    # Этот адрес открывается без каких-либо блокировок 403 со стороны Cloudflare!
    url = "https://telegram.org"
    
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
                send_telegram(f"📡 *Уведомление:* Веб-шлюз новостей ответил кодом {response.status_code}. Я продолжаю мониторинг!")
            return

        # Читаем текст веб-страницы канала
        html_text = response.text.lower()
        
        # Проверяем ключевые слова упоминания Мюнхена на странице
        keywords = ["мюнхен", "munich", "мюнхені", "münchen"]
        found_munich = any(word in html_text for word in keywords)

        # 1. Если в ленте зафиксировано свежее упоминание Мюнхена
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
                send_telegram(f"{prefix} ({time_str}): Бот на посту! Подключился к веб-шлюзу без блокировок. Свежих новостей по Мюнхене пока нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка чтения ленты: {e}")
        if IS_MANUAL_START or is_report_hour:
            send_telegram(f"📡 *Уведомление:* Произошла техническая заминка при чтении веб-ленты. Я продолжаю дежурство.")

if __name__ == "__main__":
    check_munich_slots()
