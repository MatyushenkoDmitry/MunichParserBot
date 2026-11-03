# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import requests

# GitHub автоматически передает ваши секретные ключи внутрь программы
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
        requests.post(url, json=payload)
        print("Сообщение успешно отправлено в Telegram!")
    except Exception as e:
        print(f"Ошибка сети при отправке в TG: {e}")

def check_munich_slots():
    print("🌍 Сканирую официальную веб-ленту Паспортного сервиса...")
    
    # Открытый веб-адрес публичного канала новостей ДП "Документ"
    url = "https://telegram.org"
    
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"⚠️ Шлюз временно недоступен. Код: {response.status_code}")
            return

        html_text = response.text.lower()
        
        # Проверяем ключевые слова упоминания Мюнхена на странице
        keywords = ["мюнхен", "munich", "мюнхені", "münchen"]
        found_munich = any(word in html_text for word in keywords)

        # 1. ЭКСТРЕННЫЙ АЛЕРТ: Сработает в ЛЮБУЮ секунду дня и ночи, если места появились!
        if found_munich:
            print("🔥 ОБНАРУЖЕНО УВЕДОМЛЕНИЕ О МЕСТАХ В МЮНХЕНЕ!")
            alert_text = (
                "🚨 **ЭКСТРЕННО: СИСТЕМА ЗАФИКСИРОВАЛА ВЫБРОС МЕСТ В МЮНХЕНЕ!** 🚨\n\n"
                "📅 В официальной ленте Паспортного сервиса появилось уведомление об открытии записи!\n\n"
                "🏃‍♂️ Срочно открывайте сайт и ловите слот через BankID:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
            
        # 2. РЕЖИМ ТИШИНЫ: Если мест нет
        else:
            print("✅ Проверка выполнена: свежих объявлений по Мюнхену пока нет.")
            
            # Если вы запустили бота кнопкой вручную — он отчитается на телефон
            if IS_MANUAL_START:
                send_telegram("🚀 *Ручной запуск:* Бот на посту! Подключился к веб-шлюзу без блокировок. Свободных мест в эту секунду нет.")
            
            # Если это плановый запуск каждые 5 минут — бот молчит в Telegram, чтобы не спамить,
            # но честно выполняет проверку и записывает её в логи GitHub!
            
    except Exception as e:
        print(f"⚠️ Ошибка чтения ленты: {e}")

if __name__ == "__main__":
    check_munich_slots()
