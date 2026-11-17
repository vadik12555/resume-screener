# AI Resume Screener

Веб-сервис для HR: создаёшь вакансию, загружаешь пачку резюме (PDF/DOCX), локальная LLM оценивает каждого кандидата (0–100, сильные стороны, пробелы, вопросы для собеседования) и строит рейтинг.

Портфолио-проект junior Python-разработчика. Код должен быть читаемым и объяснимым на собеседовании.

## Главное ограничение
Никаких внешних API и ключей. LLM — только локальная Ollama в Docker. Модель по умолчанию `qwen2.5:3b` (хороший русский, идёт на CPU), скачивается автоматически при первом запуске.

## Стек
- Python 3.12, Django 5, PostgreSQL 16
- Celery + Redis — фоновая обработка резюме
- Ollama (HTTP API на `http://ollama:11434`)
- Tailwind CSS (CDN) + HTMX — интерфейс без отдельного фронтенда
- pypdf, python-docx — извлечение текста; openpyxl — экспорт в Excel
- pytest + pytest-django
- Docker Compose

## Структура
```
resume-screener/
├── docker-compose.yml        # web, worker, db, redis, ollama, ollama-pull
├── Dockerfile
├── .env.example
├── manage.py
├── config/                   # settings, settings_test, urls, celery.py
├── core/                     # лендинг, StyledFormMixin, templatetags/ui.py (цвета оценок)
├── accounts/                 # регистрация/вход HR
├── vacancies/                # вакансии и требования
├── candidates/               # резюме, кандидаты, оценки, статусы
│   ├── services/
│   │   ├── parsing.py        # PDF/DOCX → текст
│   │   ├── llm.py            # клиент Ollama, промпт, валидация JSON, ретраи
│   │   └── export.py         # Excel
│   ├── tasks.py              # Celery-задачи
│   └── management/commands/load_demo.py
├── templates/                # base.html + шаблоны и HTMX-партиалы
├── demo_data/                # демо-резюме
└── tests/
```

## Команды
- Запуск: `docker compose up --build`
- Миграции: `docker compose exec web python manage.py migrate`
- Демо-данные: `docker compose exec web python manage.py load_demo`
- Тесты: `docker compose exec web pytest` (или локально `.venv\Scripts\python -m pytest`; тесты на SQLite)
- Без Docker: `$env:USE_SQLITE="1"; .\.venv\Scripts\python manage.py runserver` — SQLite, Celery в eager-режиме, LLM — локальная Ollama (OLLAMA_URL=http://localhost:11434 в .env)
- Суперюзер: `docker compose exec web python manage.py createsuperuser`

## Правила
- Type hints везде; бизнес-логика в `services/`, а не во views.
- Каждый пользователь видит только свои вакансии и кандидатов (проверка владельца в каждом view).
- Ответ LLM всегда валидируется (pydantic-схема). Невалидный JSON → 1 повторный запрос → понятная ошибка в статусе кандидата.
- Секреты только через `.env`; `.env.example` поддерживаем в актуальном виде.
- Тесты не ходят в настоящую Ollama — LLM-клиент мокается.
- Работаем по этапам: после каждого этапа — инструкция, как проверить руками.
- Интерфейс на русском, код и комментарии — на английском.
