# Explainer MVP

🚀 **Explainer MVP** — сервис для автоматической генерации объясняющих видео из **изображений / PDF / PPTX / текста**.  
Собирает видео **Manim CE → MP4**, озвучку через **ElevenLabs**, подгоняет длительность, генерирует **SRT**, даёт **UI** и **API**, работает через **FastAPI + RQ (Redis)**, с **CI** на GitHub Actions.

---

## Quick Demo

### 1) Быстрый старт (Docker Compose)

```bash
git clone https://github.com/your-org/explainer-mvp.git
cd explainer-mvp
cp .env.example .env
# В .env укажите OPENAI_API_KEY и ELEVENLABS_API_KEY
docker-compose up --build
# Откройте UI: http://localhost:8000
```

**В UI**:
1. Перетащите изображение **или** выберите *source_type* (image/pdf/pptx/text).
2. Задайте длительность (15/30/60/90 сек), аудиторию, стиль (default/whiteboard/slides), язык и тон.
3. Нажмите **Создать видео** — увидите прогресс и ссылку на скачивание MP4 + SRT.

### 2) Demo по API (curl)

**Текст → видео (30 сек):**
```bash
curl -s -X POST http://localhost:8000/api/upload   -F "source_type=text"   -F "text=Короткий пример для демо генерации видео."   -F "video_duration_sec=30"   -F "audience_preset=начинающие"   -F "style=slides" | jq .
# => {"job_id":"<ID>"}
```

Проверьте статус:
```bash
curl -s http://localhost:8000/api/status/<ID> | jq .
# state: processing|done|error, progress, message, logs, output paths
```

Скачайте результат:
```bash
curl -o final.mp4 http://localhost:8000/api/download/<ID>
curl -o subtitles.srt "http://localhost:8000/api/download/<ID>?kind=srt"
```

### 3) Схема пайплайна (Mermaid)

```mermaid
flowchart LR
    A[Upload: image/pdf/pptx/text] --> B[Ingest<br/>PDF/PPTX/Text Extract]
    B --> C{source_type}
    C -->|image| V[Vision (OpenAI: описание/объекты/текст)]
    C -->|pdf/pptx| M[1-я страница/слайд → Vision<br/>+ объединение с извлечённым текстом]
    C -->|text| T[Формирование ExtractedContent<br/>из текста напрямую]
    V --> S[ScriptWriter (LLM): beats+narration]
    M --> S
    T --> S
    S --> MN[Manim: генерация кода и рендер]
    S --> ST[SRT: генерация субтитров]
    S --> TT[ElevenLabs TTS: WAV/MP3]
    MN --> MX[Mux (ffmpeg): склейка A/V]
    TT --> MX
    ST -.-> OUT[(Final MP4 + SRT)]
    MX --> OUT
```

---

## Возможности

- Вход: **image / pdf / pptx / text**
- Vision → **ExtractedContent** (описание, объекты, текст, секции)
- ScriptWriter (LLM) → **ScriptPackage** (бииты, озвучка, таймкоды; попадание в длительность)
- Manim CE → **MP4** (1920×1080, 30fps по умолчанию)
- ElevenLabs TTS → **MP3/WAV**, склейка через **ffmpeg**
- **SRT** субтитры
- UI: drag-n-drop, параметры, прогресс, скачивание
- **Асинхронный воркер** на **RQ + Redis**, кэширование Vision/Script
- Стили сцен: **default**, **whiteboard**, **slides**
- **CI**: `black`, `isort`, `flake8`, `pytest` + Docker build

---

## Архитектура (папки)

```
app/
  api/               # FastAPI маршруты
  core/              # настройки, pydantic-модели, утилиты
  services/          # vision/script/manim/tts/mux/srt + ingest + preprocess
    ingest/          # pdf.py, pptx.py, text.py
  storage/           # storage abstraction (fs)
  workers/           # RQ: pipeline, worker, очередь
  web/               # index.html + app.js (UI)
assets/
  manim_templates/   # шаблоны сцен Manim
tests/               # pytest
.github/workflows/ci.yml
Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
```

---

## Установка

### Вариант A — Docker Compose (рекомендуется)

1) Заполните `.env`:
```env
OPENAI_API_KEY=sk-...           # Vision + Script LLM
ELEVENLABS_API_KEY=xi-...       # TTS
WORK_DIR=/data/jobs
REDIS_URL=redis://redis:6379/0
PREPROCESS_IMAGE=0              # 1 — включить OpenCV препроцессинг
MAX_UPLOAD_MB=25
MAX_PAGES=20
```

2) Поднимите сервисы:
```bash
docker-compose up --build
# UI: http://localhost:8000
```

### Вариант B — Локально (без Docker)

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Установите системные зависимости:
# - ffmpeg
# - (опц.) tesseract-ocr, если нужен pytesseract OCR
# - зависимости Manim (см. README Manim CE)

uvicorn main:app --reload --port 8000
```

---

## Конфигурация

Основные переменные в `.env` (или окружении):

| Переменная             | Назначение                                    | По умолчанию |
|------------------------|-----------------------------------------------|--------------|
| `OPENAI_API_KEY`       | Ключ OpenAI                                   | — (required) |
| `OPENAI_MODEL_VISION`  | Модель Vision                                  | `gpt-4o-mini`|
| `OPENAI_MODEL_TEXT`    | Модель для сценария                            | `gpt-4o-mini`|
| `ELEVENLABS_API_KEY`   | Ключ ElevenLabs                               | — (required) |
| `ELEVENLABS_VOICE`     | Голос по умолчанию                            | `Rachel`     |
| `WORK_DIR`             | Каталог артефактов job                        | `./_jobs`    |
| `PREPROCESS_IMAGE`     | Включить OpenCV препроцессинг                 | `0`          |
| `MAX_UPLOAD_MB`        | Лимит размера входного файла                  | `25`         |
| `MAX_PAGES`            | Лимит страниц PDF/PPTX                        | `20`         |
| `REDIS_URL`            | URL Redis                                     | `redis://localhost:6379/0` |
| `RQ_QUEUE_NAME`        | Имя очереди RQ                                | `explainer`  |

---

## API

### POST `/api/upload`
Принимает вход и параметры генерации.  
**Поля (multipart/form-data):**
- `source_type`: `image | pdf | pptx | text` (по умолчанию `image`)
- `image`: файл (`.jpg/.png/.pdf/.pptx`) — обязателен, если `source_type != text`
- `text`: исходный текст — обязателен, если `source_type = text`
- `video_duration_sec`: `15 | 30 | 60 | 90`
- `audience_preset`: `"школьники"|"начинающие"|"продвинутые"|"руководители"`
- `voice_id` / `voice_name`: (опционально)
- `narration_language`: по умолчанию `ru`
- `tone`: по умолчанию `"дружелюбный, объяснительный"`
- `style`: `default|whiteboard|slides`

**Ответ:** `{ "job_id": "..." }`

### GET `/api/status/{job_id}`
- `state`: `queued|processing|done|error`
- `progress`: `0–100`
- `message`, `logs[]`
- `output_video_path`, `srt_path`

### GET `/api/download/{job_id}`
- без параметров — скачивание `final.mp4`
- `?kind=srt` — скачивание `subtitles.srt`

---

## UI

Минимальная страница (`/`) с drag-n-drop зоны, формой параметров и полосой прогресса.  
Показывает статус задачи и две ссылки: **MP4** и **SRT**.

---

## CI (GitHub Actions)

Файл: `.github/workflows/ci.yml`  
Запускается на `push`/`pull_request`.

- **Lint**: `black --check`, `isort --check-only`, `flake8`
- **Test**: `pytest -q`
- **Docker**: build (без push)

Для локальной проверки стиля/тестов:
```bash
make lint
make test
```

---

## Тесты

Запуск:
```bash
pytest -q
```

Что проверяется (на данном этапе):
- Расчёты длительности речи, схемы Pydantic
- Ingest для текста, базовый препроцессинг изображений
- (Больше интеграционных тестов можно включить с моками OpenAI/ElevenLabs)

---

## Тонкости и ограничения

- **Vision/LLM** и **TTS** — платные API: следите за ключами и квотами.
- **Manim** рендер CPU-интенсивный: для продакшна рекомендованы отдельные воркеры и приоритетные очереди.
- **OCR** (pytesseract) — опционально; требует `tesseract-ocr` в системе/Docker.
- Лимиты на загрузки и страницы регулируются `MAX_UPLOAD_MB`, `MAX_PAGES`.

---

## Roadmap (рекомендации)

- Приоритетные очереди (high/normal), параллелизм рендера → throughput
- История задач с предпросмотром и переиспользованием артефактов
- Экспорт на YouTube/Vimeo; Slack/Telegram нотификации
- S3/MinIO для артефактов
- Расширенные шаблоны Manim: flow, compare, timeline
- Метрики Prometheus + дашборды

---

## Лицензия

**MIT** — свободно используйте, форкайте, вносите улучшения.
