
# Этап 1: Сборка кода в виртуальной машине
FROM alpine:3.18 AS builder
RUN apk add --no-cache openjdk17-jdk maven
WORKDIR /build

# Копируем исходные файлы конфигурации и кода
COPY pom.xml .
COPY src ./src

# Сборка и ПРИНУДИТЕЛЬНОЕ ЖЕСТКОЕ переименование файла средствами Linux
# Это гарантирует появление файла app.jar в папке target, независимо от артефактов pom.xml
RUN mvn clean package -DskipTests && \
    cp target/*shaded.jar target/app.jar || cp target/*.jar target/app.jar

# --- ЭТАП 2: Создание минимального финального контейнера для запуска ---
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Копируем строго один конкретный, гарантированно существующий файл app.jar
COPY --from=builder /build/target/app.jar ./app.jar

EXPOSE 8080

# Железобетонный запуск из текущей директории
ENTRYPOINT ["java", "-jar", "app.jar"]
