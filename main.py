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
    print("🌍 Маскируюсь под браузер и запрашиваю сервер Мюнхена...")
    
    # Используем точный URL шлюза API Мюнхенского филиала
    url = "https://pasport.org.ua"
    
    # Максимально глубокая имитация реального браузера Google Chrome на Windows 11
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand)";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://munich.pasport.org.ua/solutions/e-queue",
        "Connection": "keep-alive"
    }
    
    # Рассчитываем точное время в Германии (UTC+1 зимнее)
    server_time = time.gmtime()
    current_hour = (server_time.tm_hour + 1) % 24
    current_minute = server_time.tm_min
    
    # Время для автоматических отчетов: с 9:00 до 9:59 утра и с 21:00 до 21:59 вечера
    is_report_hour = (current_hour == 9) or (current_hour == 21)

    try:
        # Открываем сессию, чтобы куки сохранялись между внутренними запросами сайта
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        # Если Cloudflare все равно выдал 403, пробуем зайти через главный домен для получения кук
        if response.status_code == 403:
            print("🔄 Сработала базовая защита. Пробую обходной маневр через авторизацию...")
            session.get("https://munich.pasport.org.ua/solutions/e-queue", headers=headers, timeout=15)
            response = session.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"⚠️ Сервер ответил кодом: {response.status_code}")
            if IS_MANUAL_START or is_report_hour:
                send_telegram(f"📡 *Уведомление:* Бот в сети, но сайт Мюнхена заблокировал запрос (Код {response.status_code}). Я меняю тактику и продолжаю проверки.")
            return

        # Если сервер ответил успешно (код 200)
        data = response.json()
        available_slots = data.get("slots", [])
        
        if len(available_slots) > 0:
            print(f"🔥 НАЙДЕНЫ МЕСТА! Количество: {len(available_slots)}")
            alert_text = (
                "🚨 **ЭКСТРЕННО: В МЮНХЕНЕ ПОЯВИЛИСЬ МЕСТА!** 🚨\n\n"
                f"📅 Доступно дней для записи: *{len(available_slots)}*\n"
                "🏃‍♂️ Срочно переходите на сайт и бронируйте:\n"
                "👉 https://munich.pasport.org.ua/solutions/e-queue"
            )
            send_telegram(alert_text)
        else:
            print("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
            if IS_MANUAL_START or is_report_hour:
                time_str = f"{current_hour:02d}:{current_minute:02d}"
                prefix = "🚀 *Ручной запуск*" if IS_MANUAL_START else "🟢 *Плановый отчет*"
                send_telegram(f"{prefix} ({time_str}): Бот на посту! Проверил базу данных Мюнхена — свободных мест нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка сканирования: {e}")
        if IS_MANUAL_START or is_report_hour:
            send_telegram(f"📡 *Уведомление:* Ошибка сети при чтении сайта: {e}")

if __name__ == "__main__":
    check_munich_slots()
