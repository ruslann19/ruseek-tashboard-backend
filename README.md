# RuSeek TashBoard (Backend)

Репозиторий содержит серверную часть (бэкенд) для **RuSeek TashBoard** — обновляемого бенчмарка, предназначенного для оценки общих знаний больших языковых моделей (LLM).

Основной репозиторий проекта: [ruslann19/ruseek-tashboard](https://github.com/ruslann19/ruseek-tashboard)

---

## Требования к окружению

Для развертывания и запуска приложения необходимы:
* **Docker**
* **Docker Compose**

---

## Быстрый запуск

Развертывание всех сервисов бэкенда выполняется одной командой.

1. Клонируйте репозиторий и перейдите в папку проекта:
```bash
git clone https://github.com/ruslann19/ruseek-tashboard-backend.git
cd ruseek-tashboard-backend
```

2. Запустите сборку и контейнеры в фоновом режиме:
```bash
docker compose up --build -d
```
