
# Этап 1: Сборка кода в виртуальной машине
FROM alpine:3.18 AS builder
RUN apk add --no-cache openjdk17-jdk maven
WORKDIR /build

# Копируем файлы проекта
COPY pom.xml .
COPY src ./src

# Компилируем чистый JAR
RUN mvn clean package -DskipTests

# Этап 2: Минимальный запуск бота в облаке
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Копируем всю папку target целиком во избежание ошибок масок имен
COPY --from=builder /build/target /app/target

EXPOSE 8080

# Запускаем затененный JAR напрямую по его физическому пути из логов компиляции
ENTRYPOINT ["java", "-jar", "/app/target/munich-teleg-bot-1.0-SNAPSHOT-shaded.jar"]
