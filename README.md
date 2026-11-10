# cbr-rates-service

HTTP API на FastAPI, который отдаёт курсы USD, EUR и CNY к рублю.
Данные берутся из открытого JSON с курсами ЦБ РФ (cbr-xml-daily.ru).

## Endpoints

| Метод | Путь      | Описание                                   |
|-------|-----------|--------------------------------------------|
| GET   | `/health` | Проверка работоспособности и версия        |
| GET   | `/rates`  | Дата и курсы USD, EUR, CNY                 |

Если источник курсов недоступен, `/rates` возвращает HTTP 502.

## Схема

```text
Браузер
   ↓ HTTP :80
nginx (Ubuntu Server)
   ↓ proxy_pass http://127.0.0.1:8001
Docker: 127.0.0.1:8001 → контейнер :8000
   ↓
uvicorn / FastAPI
   ↓ HTTPS (только для /rates)
cbr-xml-daily.ru
```

## Стек

- Python/FastAPI
- Docker
- Compose
- nginx
- Ubuntu Server

## Локальный запуск

Требуется Docker с Compose.

```bash
docker compose up -d --build --wait
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/rates
```

## Деплой на сервер

Код на сервере лежит в `/opt/cbr-rates/src` и принадлежит пользователю `cbr`.
Обновление выполняет скрипт `deploy/deploy.sh`:

1. `git pull --ff-only` — получает новый код с GitHub;
2. `docker compose up -d --build --wait` — пересобирает образ и ждёт статуса healthy;
3. устанавливает конфиг nginx, проверяет его (`nginx -t`) и перечитывает;
4. проверяет `/health` через nginx; при ошибке выводит логи контейнера и завершается с кодом 1.

```bash
/opt/cbr-rates/src/deploy/deploy.sh
```

## Структура проекта

- app/ -- код приложения
- deploy/ -- файлы для сервера: конфиг nginx и скрипт деплоя
- Dockerfile -- Описывает, как собрать образ
- compose.yaml -- Описывает, как запустить контейнер из образа