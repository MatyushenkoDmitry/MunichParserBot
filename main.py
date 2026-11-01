# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import time
import requests

# GitHub автоматически и безопасно передает ваши секретные ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Проверяем, запущен ли бот вручную пользователем через кнопку Run workflow
IS_MANUAL_START = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты BOT_TOKEN или CHAT_ID не найдены!")
        return
    
    # Наша проверенная и безопасная сборка адреса по кусочкам
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
    
    # Прямой адрес API Мюнхенского филиала Паспортного сервиса
    url = "https://pasport.org.ua"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://pasport.org.ua"
    }
    
    # Считаем точное зимнее время Мюнхена (переводим серверные часы в пояс UTC+1)
    server_time = time.gmtime()
    current_hour = (server_time.tm_hour + 1) % 24
    current_minute = server_time.tm_min
    
    # УБРАЛИ МИНУТЫ! Окно отчета теперь открыто на весь час (с 9:00 до 9:59 и с 21:00 до 21:59)
    # В какую бы минуту этого часа GitHub ни запустил бота — отчет уйдет!
    is_report_hour = (current_hour == 9) or (current_hour == 21)

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️ Сервер временно недоступен. Код ответа сайта: {response.status_code}")
            if IS_MANUAL_START or is_report_hour:
                send_telegram(f"📡 *Уведомление:* Бот в сети, но сайт Мюнхена сейчас выдает ошибку {response.status_code}.")
            return

        data = response.json()
        available_slots = data.get("slots",)
        
        # 1. Если места РЕАЛЬНО появились (сработает мгновенно в любую секунду 24/7!)
        if len(available_slots) > 0:
            print(f"🔥 НАЙДЕНЫ СВОБОДНЫЕ МЕСТА! Количество дат: {len(available_slots)}")
            alert_text = (
                "🚨 **ЭКСТРЕННО: В МЮНХЕНЕ ПОЯВИЛИСЬ МЕСТА!** 🚨\n\n"
                f"📅 Доступно дней для записи: *{len(available_slots)}*\n"
                "🏃‍♂️ Срочно переходите на сайт:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
            
        # 2. Если мест нет
        else:
            print("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
            
            # Отправляем сообщение, если это ручной старт ИЛИ плановый час отчета
            if IS_MANUAL_START or is_report_hour:
                time_str = f"{current_hour:02d}:{current_minute:02d}"
                prefix = "🚀 *Ручной запуск*" if IS_MANUAL_START else "🟢 *Плановый отчет*"
                send_telegram(f"{prefix} ({time_str}): Бот на посту! Проверил базу данных Мюнхена — свободных мест пока нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка при чтении сайта: {e}")
        if IS_MANUAL_START or is_report_hour:
            send_telegram(f"📡 *Уведомление:* Не смог достучаться до сайта. Ошибка: {e}")

if __name__ == "__main__":
    check_munich_slots()
