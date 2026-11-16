# cbr-rates-service
![CI](https://github.com/molodoy1gerzog/cbr-rates-service/actions/workflows/ci.yml/badge.svg)

HTTP API на FastAPI, который отдаёт курсы USD, EUR и CNY к рублю.
Данные берутся из открытого JSON с курсами ЦБ РФ (cbr-xml-daily.ru).
Данные курсов сохраняются в PostgreSQL и теперь можно проверять историю

## Endpoints

| Метод | Путь      | Описание                                   |
|-------|-----------|--------------------------------------------|
| GET   | `/health` | Проверка работоспособности и версия        |
| GET   | `/rates`  | Дата и курсы USD, EUR, CNY                 |
| GET   | `/rates/history` | История курсов из базы; `?limit=` — число записей (по умолчанию 30) |

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
   ↓ HTTPS (/rates)            ↓ SQL (сеть Compose, db:5432)
cbr-xml-daily.ru            PostgreSQL 18 (том pgdata)
```

## Стек

- Python/FastAPI
- Docker
- Compose
- nginx
- Ubuntu Server
- PostgreSQL 18
- SQLAlchemy

## Локальный запуск
Требуется Docker с Compose.

Перед первым запуском создай `.env` из примера и задай пароль базы:

```bash
cp .env.example .env
```

Запуск и проверка:

```bash
docker compose up -d --build --wait
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/rates
curl http://127.0.0.1:8001/rates/history
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

Перед первым деплоем на сервере нужно создать `/opt/cbr-rates/src/.env`
(владелец `cbr`, права 600). В Git этот файл не попадает.

## Бэкап и восстановление

Бэкап (на сервере, из `/opt/cbr-rates/src`):

```bash
sudo docker compose exec -T db pg_dump -U cbr -d cbr -Fc -f /tmp/cbr.dump
sudo docker compose cp db:/tmp/cbr.dump /opt/cbr-rates/backups/cbr-$(date +%F_%H%M).dump
sudo docker compose exec -T db rm /tmp/cbr.dump
```

Проверка восстановления в тестовую базу:

```bash
sudo docker compose cp /opt/cbr-rates/backups/<файл>.dump db:/tmp/restore.dump
sudo docker compose exec -T db createdb -U cbr cbr_restore_test
sudo docker compose exec -T db pg_restore -U cbr -d cbr_restore_test /tmp/restore.dump
sudo docker compose exec -T db psql -U cbr -d cbr_restore_test -c "select count(*) from rates;"
sudo docker compose exec -T db dropdb -U cbr cbr_restore_test
```

## Структура проекта

- app/ -- код приложения
- deploy/ -- файлы для сервера: конфиг nginx и скрипт деплоя
- Dockerfile -- Описывает, как собрать образ
- compose.yaml -- Описывает, как запустить контейнер из образа
- app/db.py -- подключение к базе и модель таблицы rates