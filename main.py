# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import datetime
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Проверяем, запущен ли бот вручную пользователем через кнопку
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
        response = requests.post(url, json=payload)
        print(f"Статус отправки в Telegram: {response.status_code}")
    except Exception as e:
        print(f"Ошибка сети при отправке в TG: {e}")

def check_munich_slots():
    print("🌍 Запрашиваю данные с сервера ДП 'Документ' в Мюнхене...")
    url = "https://pasport.org.ua"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://pasport.org.ua"
    }
    
    # Точное немецкое время (UTC+1 зимнее)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))
    current_hour = now.hour
    
    # Отчет срабатывает, если наступил нужный час (9 или 21) ИЛИ если пользователь нажал кнопку старта вручную
    is_report_time = (current_hour == 9) or (current_hour == 21) or IS_MANUAL_START

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️ Сервер временно недоступен. Код: {response.status_code}")
            return

        data = response.json()
        available_slots = data.get("slots", [])
        
        if len(available_slots) > 0:
            print(f"🔥 НАЙДЕНЫ СВОБОДНЫЕ МЕСТА! Количество дат: {len(available_slots)}")
            alert_text = (
                "🚨 **ЭКСТРЕННО: В МЮНХЕНЕ ПОЯВИЛИСЬ МЕСТА!** 🚨\n\n"
                f"📅 Доступно дней для записи: *{len(available_slots)}*\n\n"
                "🏃‍♂️ Срочно переходите на сайт:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
            
        else:
            print("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
            if is_report_time:
                time_str = now.strftime('%H:%M')
                # Меняем текст в зависимости от типа запуска
                prefix = "🚀 *Ручной запуск*" if IS_MANUAL_START else "🟢 *Плановый отчет*"
                send_telegram(f"{prefix} ({time_str}): Бот на посту! Проверил базу данных Мюнхена — свободных мест пока нет.")
                
    except Exception as e:
        print(f"⚠️ Ошибка при чтении сайта: {e}")

if __name__ == "__main__":
    check_munich_slots()
