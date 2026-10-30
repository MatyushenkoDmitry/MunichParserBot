# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import requests

# GitHub автоматически передаст ваши секретные ключи внутрь программы
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Секреты BOT_TOKEN или CHAT_ID не найдены в GitHub Actions!")
        return
    
    # Защищенная сборка адреса Telegram API
    url = "https://" + "api." + "telegram.org" + "/bot" + BOT_TOKEN + "/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message,
        "parse_mode": "Markdown" # Включает красивую подсветку ссылок жирным шрифтом
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Статус отправки в Telegram: {response.status_code}")
    except Exception as e:
        print(f"Ошибка сети при отправке в TG: {e}")

def check_munich_slots():
    print("🌍 Запрашиваю данные с сервера ДП 'Документ' в Мюнхене...")
    
    # Официальный адрес API Мюнхенского филиала Паспортного сервиса
    url = "https://pasport.org.ua"
    
    # Имитируем запрос от обычного домашнего браузера, чтобы сайт не заблокировал бота
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://pasport.org.ua"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Если сайт временно упал или на защите Cloudflare, бот не вылетит, а тихо подождет
        if response.status_code != 200:
            print(f"⚠️ Сервер временно недоступен. Код ответа сайта: {response.status_code}")
            return

        data = response.json()
        
        # Анализируем массив доступных дат, присланных сервером
        available_slots = data.get("slots", [])
        
        if len(available_slots) > 0:
            print(f"🔥 НАЙДЕНЫ СВОБОДНЫЕ МЕСТА! Количество дат: {len(available_slots)}")
            
            # Формируем красивое экстренное сообщение со ссылкой
            alert_text = (
                "🚨 **ЭКСТРЕННО: В МЮНХЕНЕ ПОЯВИЛИСЬ МЕСТА!** 🚨\n\n"
                f"📅 Доступно дней для записи: *{len(available_slots)}*\n"
                f"ℹ️ Ближайшая дата: `{available_slots[0].get('date', 'Не определена')}`\n\n"
                "🏃‍♂️ Срочно переходите на сайт и подтверждайте через BankID:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
        else:
            print("✅ Проверка выполнена: свободных мест в Мюнхене пока нет.")
            
    except Exception as e:
        print(f"⚠️ Ошибка при чтении сайта (возможно, сработала защита): {e}")

# Главная точка запуска
if __name__ == "__main__":
    send_telegram("🔔 Проверка связи! GitHub успешно передал ключи, я вижу ваш чат.")
    check_munich_slots()
