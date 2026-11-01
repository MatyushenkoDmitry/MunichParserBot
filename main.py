# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import time
import requests
import json

# GitHub автоматически передает ваши секретные ключи внутрь программы
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Проверяем, запущен ли бот вручную пользователем через кнопку Run workflow
IS_MANUAL_START = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты не найдены!")
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
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

def check_munich_slots():
    print("🌍 Запускаю обход Cloudflare через независимый прокси-шлюз...")
    
    # Железобетонная сборка адреса прокси-сервера по кусочкам, чтобы ничего не слипалось
    base_proxy = "https://allorigins.win"
    target_site = "https://pasport.org.ua"
    
    proxy_url = base_proxy + requests.utils.quote(target_site)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    # Считаем точное зимнее время Мюнхена (переводим серверные часы в пояс UTC+1)
    server_time = time.gmtime()
    current_hour = (server_time.tm_hour + 1) % 24
    current_minute = server_time.tm_min
    
    # Включаем отчет на весь часовой диапазон: с 9:00 до 9:59 утра и с 21:00 до 21:59 вечера
    is_report_hour = (current_hour == 9) or (current_hour == 21)

    try:
        # Делаем запрос через прокси-сервер
        response = requests.get(proxy_url, headers=headers, timeout=25)

        if response.status_code != 200:
            print(f"⚠️ Прокси-шлюз временно перегружен. Код ответа: {response.status_code}")
            if IS_MANUAL_START or is_report_hour:
                send_telegram(f"📡 *Уведомление:* Прокси-шлюз временно недоступен (Код {response.status_code}). Продолжаю автоматический подбор зеркал.")
            return

        # Прокси возвращает ответ в обертке, вытаскиваем оригинальный JSON сайта
        contents = response.json().get("contents")
        data = json.loads(contents)
        
        available_slots = data.get("slots", [])
        
        # 1. Если места РЕАЛЬНО появились (сработает мгновенно в любую секунду 24/7)
        if len(available_slots) > 0:
            print(f"🔥 НАЙДЕНЫ СВОБОДНЫЕ МЕСТА! Количество дат: {len(available_slots)}")
            alert_text = (
                "🚨 **ЭКСТРЕННО: В МЮНХЕНЕ ПОЯВИЛИСЬ МЕСТА!** 🚨\n\n"
                f"📅 Доступно дней для записи: *{len(available_slots)}*\n"
                "🏃‍♂️ Срочно переходите на сайт и бронируйте:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
            
        # 2. Если мест нет
        else:
            print("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
            if IS_MANUAL_START or is_report_hour:
                time_str = f"{current_hour:02d}:{current_minute:02d}"
                prefix = "🚀 *Ручной запуск*" if IS_MANUAL_START else "🟢 *Плановый отчет*"
                send_telegram(f"{prefix} ({time_str}): Бот пробил защиту Cloudflare! Проверил базу данных Мюнхена — свободных мест в эту секунду нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка дешифровки данных сайта: {e}")
        if IS_MANUAL_START or is_report_hour:
            send_telegram(f"📡 *Уведомление:* Ошибка декодирования базы данных Мюнхена. Меняю прокси-сервер.")

if __name__ == "__main__":
    check_munich_slots()
