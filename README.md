# Model Update Server

Минимальный backend-сервис на FastAPI для загрузки `.pt` моделей, их в `.ort`, хранения метаданных в SQLite и выдачи последней модели устройствам.

## Эндпоинты

- `POST /models` - загрузка новой `.pt` модели с версией
- `GET /models/latest` - метаданные последней модели
- `GET /models/latest/download` - скачивание последней `.ort` модели

## API

Все API-запросы требуют заголовок авторизации:

```http
X-API-Key: <server-issued-key>
```

Ключи выпускаются вручную на сервере и задаются через переменную окружения `API_KEYS`.
Можно указать один ключ или несколько ключей через запятую.

### `POST /models`

Загружает новую модель и регистрирует её как актуальную.

Принимает:

- `Content-Type: multipart/form-data`
- поле `file` - файл модели в формате `.pt`
- поле `version` - строковая версия модели, например `1.0.3`

Возвращает:

- `201 Created` и JSON:

```json
{
  "version": "1.0.3",
  "created_at": "2026-05-12T10:00:00Z",
  "filename": "model_v1.0.3.ort",
  "is_latest": true
}
```

Ошибки:

- `400` - пустая версия или файл не `.pt`
- `409` - такая версия уже существует
- `500` - ошибка конвертации

### `GET /models/latest`

Возвращает метаданные последней доступной модели.

Принимает:

- ничего

Возвращает:

- `200 OK` и JSON:

```json
{
  "version": "1.0.3",
  "created_at": "2026-05-12T10:00:00Z",
  "filename": "model_v1.0.3.ort"
}
```

Ошибки:

- `404` - если моделей ещё нет

### `GET /models/latest/download`

Возвращает файл последней `.ort` модели.

Принимает:

- query-параметр `version`
- query-параметр `filename`

Возвращает:

- `200 OK`
- бинарный файл `.ort`
- заголовок `Content-Disposition` для скачивания

Ошибки:

- `404` - если моделей нет, файл отсутствует на диске или `version`/`filename` не совпадают с актуальной моделью

## Требования

- Python 3.11+

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Сервис будет доступен на `http://127.0.0.1:8000`.

Пример запуска с API-ключом:

```bash
API_KEYS="local-dev-key" uvicorn app.main:app --reload
```

Сгенерировать 10 API-ключей и экспортировать их в текущую shell:

```bash
source scripts/generate_api_keys.sh
uvicorn app.main:app --reload
```

Сгенерировать 10 API-ключей и сохранить их в env-файл:

```bash
scripts/generate_api_keys.sh --env-file .env
set -a
source .env
set +a
uvicorn app.main:app --reload
```

## Переменные окружения

- `MODELS_DIR` - директория хранения итоговых `.ort` моделей
- `TMP_DIR` - директория для временно загруженных `.pt`
- `DATABASE_URL` - URL подключения к SQLite, например `sqlite:///./db/app.db`
- `API_KEYS` - один или несколько API-ключей через запятую, например `key-1,key-2`

По умолчанию используются:

- `storage/models`
- `tmp`
- `sqlite:///db/app.db`
- пустой список API-ключей, при котором API-запросы будут отклоняться с `401`

## Архитектура

Проект разложен по слоям clean architecture:

- `app/domain` - сущности, интерфейсы репозиториев и доменные исключения
- `app/application` - use cases и DTO
- `app/infrastructure` - SQLite, файловое хранилище, stub-конвертер, bootstrap
- `app/presentation` - FastAPI routes, зависимости и response-схемы

Точка входа приложения: [app/main.py](/Users/tanexc/PyCharmMiscProject/convert-and-update-model-server/app/main.py).

## Примеры запросов

Загрузка модели:

```bash
curl -X POST "http://127.0.0.1:8000/models" \
  -H "X-API-Key: local-dev-key" \
  -F "version=1.0.3" \
  -F "file=@./example.pt"
```

Получение метаданных:

```bash
curl -H "X-API-Key: local-dev-key" \
  "http://127.0.0.1:8000/models/latest"
```

Скачивание последней модели:

```bash
curl -OJ -H "X-API-Key: local-dev-key" \
  "http://127.0.0.1:8000/models/latest/download?version=1.0.3&filename=model_v1.0.3.ort"
```

## Docker

Сборка:

```bash
docker build -t model-update-server .
```

Сгенерировать ключи в `.env`:

```bash
scripts/generate_api_keys.sh --env-file .env
```

Запуск через env-файл:

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/storage/models:/app/storage/models" \
  -v "$(pwd)/db:/app/db" \
  model-update-server
```

Файл `.env` содержит реальные ключи и не должен попадать в репозиторий. Шаблон без секретов находится в `.env.example`.

## systemd

Пример unit-файла находится в `deploy/systemd/model-update-server.service`.
Он читает переменные окружения из `/etc/model-update-server/model-update-server.env`.

Установка env-файла с ключами:

```bash
sudo mkdir -p /etc/model-update-server
scripts/generate_api_keys.sh --env-file /tmp/model-update-server.env
sudo install -m 600 /tmp/model-update-server.env /etc/model-update-server/model-update-server.env
rm /tmp/model-update-server.env
```

Установка unit-файла:

```bash
sudo cp deploy/systemd/model-update-server.service /etc/systemd/system/model-update-server.service
sudo systemctl daemon-reload
sudo systemctl enable --now model-update-server
```

## Структура данных

Таблица `models`:

- `id`
- `version`
- `filename`
- `file_path`
- `created_at`
- `is_latest`
