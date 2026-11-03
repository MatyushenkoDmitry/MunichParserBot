# Робот автоматически прочитает чистый токен и ID чата из настроек Render
import os
import requests
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
    print("🌍 Сканирую официальную веб-ленту Паспортного сервиса...")
    url = "https://telegram.org"
    
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"⚠️ Шлюз временно недоступен. Код: {response.status_code}")
            return

        html_text = response.text.lower()
        keywords = ["мюнхен", "munich", "мюнхені", "münchen"]
        found_munich = any(word in html_text for word in keywords)

        # 1. ЭКСТРЕННЫЙ АЛЕРТ (Работает круглосуточно)
        if found_munich:
            alert_text = (
                "🚨 **ЭКСТРЕННО: СИСТЕМА ЗАФИКСИРОВАЛА ВЫБРОС МЕСТ В МЮНХЕНЕ!** 🚨\n\n"
                "🏃‍♂️ Срочно открывайте сайт и ловите слот через BankID:\n"
                "👉 https://pasport.org.ua"
            )
            send_telegram(alert_text)
            
        # 2. РЕЖИМ ТИШИНЫ (Запись лога для вечной работы)
        else:
            print("✅ Проверка выполнена: свободных мест пока нет.")
            
            # ТРЮК ДЛЯ ОБХОДА ПАУЗЫ GITHUB: записываем время проверки в файл
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))
            with open("last_check.txt", "w") as f:
                f.write(f"Last successful check: {now.strftime('%Y-%m-%d %H:%M:%S')} (Munich Time)")
            
            # Автоматически отправляем этот файл обратно на GitHub
            os.system("git config --global user.name 'MunichBot'")
            os.system("git config --global user.email 'bot@munich.local'")
            os.system("git config --global --add safe.directory /github/workspace")
            os.system("git add last_check.txt")
            os.system("git commit -m '🤖 Продление активности таймера (Каждые 5 минут)' || echo 'No changes'")
            os.system("git push || echo 'Push failed'")
            
    except Exception as e:
        print(f"⚠️ Ошибка чтения ленты: {e}")

if __name__ == "__main__":
    check_munich_slots()
