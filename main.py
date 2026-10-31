# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import datetime
import requests

# GitHub автоматически передаст ваши секретные ключи внутрь программы
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты BOT_TOKEN или CHAT_ID не найдены!")
        return
    
    url = "https://" + "api." + "telegram.org" + "/bot" + BOT_TOKEN + "/sendMessage"
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
    
    # Официальный адрес API Мюнхенского филиала
    url = "https://pasport.org.ua"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://pasport.org.ua"
    }
    
    # Определяем текущее время (переводим в правильный часовой пояс Германии/Украины)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))
    current_hour = now.hour
    current_minute = now.minute
    
    # Проверяем, время ли сейчас для планового отчета (утро: 09:10-09:15 или вечер: 21:10-21:15)
    # Диапазон в 5 минут нужен, так как GitHub Actions запускается примерно раз в 5 минут
    is_report_time = (current_hour == 9 and 10 <= current_minute <= 15) or (current_hour == 21 and 10 <= current_minute <= 15)

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️ Сервер временно недоступен. Код: {response.status_code}")
            if is_report_time:
                send_telegram(f"📡 *Плановый отчет:* Связь есть, но сам сайт ДП 'Документ' сейчас выдает ошибку {response.status_code}. Я продолжаю попытки!")
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
            # Если мест нет, но наступило время отчета — присылаем "сигнал жизни"
            if is_report_time:
                time_str = now.strftime('%H:%M')
                send_telegram(f"🟢 *Плановый отчет ({time_str}):* Бот на посту! Проверил базу данных Мюнхена — свободных мест пока нет. Следующий отчет вечером.")
                
    except Exception as e:
        print(f"⚠️ Ошибка при чтении сайта: {e}")
        if is_report_time:
            send_telegram("📡 *Плановый отчет:* Я в сети, но не смог достучаться до сайта Мюнхена (возможно, защита Cloudflare). Продолжаю сканирование!")

if __name__ == "__main__":
    check_munich_slots()
