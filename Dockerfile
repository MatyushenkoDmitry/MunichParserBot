
# Этап 1: Сборка кода в виртуальной машине
FROM alpine:3.18 AS builder
RUN apk add --no-cache openjdk17-jdk maven
WORKDIR /build

COPY pom.xml .
COPY src ./src

# Собираем проект и сразу переименовываем финальный тяжелый файл в app.jar
RUN mvn clean package -DskipTests && \
    mv target/*-shaded.jar target/app.jar || mv target/*.jar target/app.jar

# Этап 2: Запуск без использования кэша путей
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Копируем уже гарантированно существующий и переименованный файл app.jar
COPY --from=builder /build/target/app.jar ./app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
