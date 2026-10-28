
# Этап 1: Сборка кода в виртуальной машине
FROM alpine:3.18 AS builder
RUN apk add --no-cache openjdk17-jdk maven
WORKDIR /build

# Копируем файлы проекта
COPY pom.xml .
COPY src ./src

# Просто запускаем чистую компиляцию Maven
RUN mvn clean package -DskipTests

# Этап 2: Минимальный запуск бота в облаке
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Копируем файл app.jar, который Maven сам создал под этим именем
COPY --from=builder /build/target/app.jar ./app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
