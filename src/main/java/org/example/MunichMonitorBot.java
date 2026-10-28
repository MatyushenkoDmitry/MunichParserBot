package org.example;

import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.meta.generics.TelegramClient;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class MunichMonitorBot {




    private static final String BOT_TOKEN = "9145997015:AAHNZp3yQn9QZ13G8drEnVCUXbgwRw6orYw";
    private static final String MY_CHAT_ID = "977293445";


    private static final String URL_MUNICH = "https://cherga24.com/ua/munich";
    private static final TelegramClient telegramClient = new OkHttpTelegramClient(BOT_TOKEN);
    private static final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(15))
            .followRedirects(HttpClient.Redirect.ALWAYS)
            .build();

    public static void main(String[] args) {
        System.out.println("🤖 Java-bot is running on the computer!");
        sendTelegramMessage("🤖 Bot started. Scan accuracy reset. I check Munich every 2 minutes.");

        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleAtFixedRate(MunichMonitorBot::checkSlots, 0, 2, TimeUnit.MINUTES);
    }

    private static void checkSlots() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(URL_MUNICH))
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9")
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                String html = response.body();


                if (!html.contains("Мюнхен") && !html.contains("Munich")) {
                    System.out.println("⚠️ Сайт выдал заглушку защиты. Попробуем в следующий цикл.");
                    return;
                }


                String lowerHtml = html.toLowerCase();

                boolean noSlots = lowerHtml.contains("моніторинг активний") ||
                        lowerHtml.contains("почати моніторинг") ||
                        lowerHtml.contains("місця відсутні") ||
                        lowerHtml.contains("немає вільних місць");

                if (!noSlots) {

                    String alertText = "🚨 **МЮНХЕН: ПОЯВИЛИСЬ СВОБОДНЫЕ МЕСТА!** 🚨\n\n" +
                            "СUrgently go to the portal and log in via BankID:\n" +
                            "https://pasport.org.ua";
                    sendTelegramMessage(alertText);
                    System.out.println("🔥 Slots are actually found! Message sent.");
                } else {

                    System.out.println("✅ Check completed: no seats in Munich yet.");
                }
            } else {
                System.out.println("❌ Server error: code " + response.statusCode());
            }

        } catch (Exception e) {
            System.out.println("⚠️ Network error\n: " + e.getMessage());
        }
    }

    private static void sendTelegramMessage(String text) {
        SendMessage message = SendMessage.builder()
                .chatId(MY_CHAT_ID)
                .text(text)
                .parseMode("Markdown")
                .build();
        try {
            telegramClient.execute(message);
        } catch (TelegramApiException e) {
            System.err.println("Ошибка Telegram API: " + e.getMessage());
        }
    }
}

