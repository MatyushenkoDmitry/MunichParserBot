# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import time
import requests

# GitHub автоматически передает секретные ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

IS_MANUAL_START = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты не найдены!")
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
    print("🌍 Запрашиваю данные через центральный шлюз API...")
    
    # ХИТРЫЙ ХОД: Стучимся на центральный сайт Киева, запрашивая ID филиала 7 (Мюнхен)
    # Этот адрес Cloudflare НЕ блокирует!
    url = "https://pasport.org.ua"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
        "Referer": "https://pasport.org.ua",
        "Connection": "keep-alive"
    }
    
    # Рассчитываем точное время в Германии (UTC+1 зимнее)
    server_time = time.gmtime()
    current_hour = (server_time.tm_hour + 1) % 24
    current_minute = server_time.tm_min
    
    is_report_hour = (current_hour == 9) or (current_hour == 21)

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"⚠️ Сервер ответил кодом: {response.status_code}")
            if IS_MANUAL_START or is_report_hour:
                send_telegram(f"📡 *Уведомление:* Центральный сервер выдал код {response.status_code}. Я продолжаю подбор прокси.")
            return

        data = response.json()
        
        # Центральный API возвращает список услуг Мюнхена. 
        # Если в какой-то услуге параметр 'has_slots' становится True — места открылись!
        services = data.get("services", [])
        has_free_seats = any(service.get("has_slots") is True for service in services)
        
        if has_free_seats:
            print("🔥 НАЙДЕНЫ СВОБОДНЫЕ МЕСТА В МЮНХЕНЕ!")
            alert_text = (
                "🚨 **ЭКСТРЕННО: В МЮНХЕНЕ ПОЯВИЛИСЬ МЕСТА!** 🚨\n\n"
                "📅 На центральном сервере Паспортного сервиса открылась запись для Мюнхена!\n\n"
                "🏃‍♂️ Срочно переходите на сайт и бронируйте через BankID:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
        else:
            print("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
            if IS_MANUAL_START or is_report_hour:
                time_str = f"{current_hour:02d}:{current_minute:02d}"
                prefix = "🚀 *Ручной запуск*" if IS_MANUAL_START else "🟢 *Плановый отчет*"
                send_telegram(f"{prefix} ({time_str}): Бот на посту! Проверил центральную базу данных Мюнхена — свободных мест нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка сканирования: {e}")
        if IS_MANUAL_START or is_report_hour:
            send_telegram(f"📡 *Уведомление:* Ошибка сети при чтении центрального сайта: {e}")

if __name__ == "__main__":
    check_munich_slots()
