"""Fictional demo data: one vacancy and 8 resumes of different levels.

Evaluations are pre-computed so the demo looks complete even without the LLM.
Run `load_demo --llm` to have the local model re-evaluate them.
"""

VACANCY = {
    "title": "Python-разработчик (Middle)",
    "description": (
        "Развиваем B2B-платформу для логистики: личный кабинет, интеграции с перевозчиками, "
        "фоновая обработка заказов. Команда — 6 бэкендеров, код-ревью, CI/CD, без легаси на Python 2."
    ),
    "must_have": "Python 3\nDjango\nPostgreSQL\nREST API\nGit",
    "nice_to_have": "Celery\nRedis\nDocker\npytest\nCI/CD",
}

CANDIDATES: list[dict] = [
    {
        "name": "Алексей Смирнов",
        "decision": "invited",
        "score": 92,
        "summary": "Сильный middle+ с 5 годами коммерческой разработки на Django; закрывает все обязательные и почти все желательные требования.",
        "strengths": [
            "5 лет коммерческой разработки на Django и DRF",
            "Опыт с Celery и Redis под высокой нагрузкой (≈2 млн задач в сутки)",
            "Оптимизация запросов PostgreSQL: индексы, EXPLAIN, партиционирование",
            "Настраивал CI/CD в GitLab и деплой в Docker",
            "Менторил двух junior-разработчиков",
        ],
        "gaps": ["Нет опыта с интеграциями в логистике"],
        "questions": [
            "Как вы снизили время ответа API со 1.2 с до 180 мс — какие узкие места нашли?",
            "Как устроены ретраи и идемпотентность ваших Celery-задач?",
            "Когда бы вы выбрали партиционирование таблицы, а когда — архивирование?",
        ],
        "text": """Алексей Смирнов
Python-разработчик · Москва · alexey.smirnov@example.com

Опыт работы
2021–н.в. — ООО «ДеливерТех», Senior Python Developer
- Разработка API на Django + DRF для сервиса доставки (300k пользователей)
- Фоновая обработка заказов на Celery + Redis, ≈2 млн задач в сутки
- Оптимизация PostgreSQL: индексы, EXPLAIN ANALYZE, партиционирование — API быстрее в 6 раз (1.2 с → 180 мс)
- Настроил CI/CD в GitLab, деплой в Docker
- Менторство двух junior-разработчиков

2019–2021 — «Финсофт», Python Developer
- Django-монолит для учёта платежей, покрытие тестами pytest с 30% до 80%

Навыки: Python 3.12, Django, DRF, PostgreSQL, Celery, Redis, Docker, pytest, Git, GitLab CI
Образование: МГТУ им. Баумана, Прикладная информатика, 2019""",
    },
    {
        "name": "Мария Ковалёва",
        "decision": "invited",
        "score": 84,
        "summary": "Уверенный middle, 3 года на FastAPI и год на Django; хорошая база в PostgreSQL и тестировании.",
        "strengths": [
            "3 года бэкенд-разработки на Python (FastAPI, Django)",
            "Проектировала REST API и схемы БД в PostgreSQL",
            "Пишет тесты на pytest, знакома с Docker",
            "Опыт интеграций с внешними API (платёжные шлюзы)",
        ],
        "gaps": ["Django-опыт около года", "Нет опыта с Celery"],
        "questions": [
            "Что показалось самым непривычным при переходе с FastAPI на Django?",
            "Как бы вы вынесли тяжёлую операцию из запроса в фон без Celery и с ним?",
            "Расскажите про самую сложную миграцию схемы БД, которую вы делали.",
        ],
        "text": """Мария Ковалёва
Backend-разработчик · Санкт-Петербург

Опыт
2023–н.в. — «ПэйЛайн», Python Developer
- Перенос сервиса биллинга с FastAPI на Django, REST API для партнёров
- PostgreSQL: проектирование схемы, миграции, оптимизация запросов
2021–2023 — «Стартап Мэпс», Junior Python Developer
- Микросервисы на FastAPI, интеграции с платёжными шлюзами (ЮKassa, CloudPayments)
- Тесты на pytest, Docker Compose для локальной разработки

Навыки: Python, FastAPI, Django, SQLAlchemy, PostgreSQL, REST, Docker, pytest, Git
Английский — B2""",
    },
    {
        "name": "Дмитрий Орлов",
        "decision": "new",
        "score": 76,
        "summary": "Middle с сильным Django, но слабым опытом в инфраструктуре и тестах.",
        "strengths": [
            "4 года на Django: админки, ORM, шаблоны",
            "Хорошее знание PostgreSQL",
            "Делал REST API для мобильного приложения",
        ],
        "gaps": ["Нет опыта с Docker и CI/CD", "Тесты пишет эпизодически", "Не работал с Celery"],
        "questions": [
            "Как вы проверяете, что изменения не ломают существующий функционал без автотестов?",
            "Как запускали и деплоили проект без Docker?",
            "Приведите пример проблемы N+1 в ORM и как вы её решили.",
        ],
        "text": """Дмитрий Орлов
Python/Django-разработчик · Казань (удалённо)

2020–н.в. — веб-студия «Пиксель», Django-разработчик
- Интернет-магазины и CRM на Django, кастомные админки
- REST API (DRF) для мобильного приложения сети кофеен
- Оптимизация ORM-запросов, select_related/prefetch_related
Деплой — вручную на VPS (nginx + gunicorn)

Навыки: Python, Django, DRF, PostgreSQL, HTML/CSS, Git, Linux""",
    },
    {
        "name": "Екатерина Белова",
        "decision": "new",
        "score": 68,
        "summary": "Сильный Python-специалист из анализа данных, бэкенд-опыт небольшой.",
        "strengths": [
            "Отличное знание Python и SQL",
            "Писала внутренние API на Flask",
            "Опыт с Docker и Airflow",
        ],
        "gaps": ["Нет коммерческого опыта с Django", "REST API — только внутренние сервисы"],
        "questions": [
            "Почему решили перейти из data-инженерии в веб-разработку?",
            "Чем, на ваш взгляд, Django отличается от Flask в большом проекте?",
            "Как вы бы спроектировали API для выгрузки отчётов, которые строятся 5 минут?",
        ],
        "text": """Екатерина Белова
Data Engineer → Backend · Новосибирск

2021–н.в. — ритейл «Северный», Data Engineer
- ETL-пайплайны на Python + Airflow, хранилище в PostgreSQL
- Внутренний API на Flask для отчётов
- Docker, Git, CI в GitHub Actions
Пет-проект: трекер привычек на Django (GitHub)

Навыки: Python, SQL, PostgreSQL, Pandas, Airflow, Flask, Docker, Git""",
    },
    {
        "name": "Иван Петров",
        "decision": "new",
        "score": 55,
        "summary": "Junior без коммерческого опыта, но с аккуратными pet-проектами на нужном стеке.",
        "strengths": [
            "Pet-проекты на Django и DRF с Docker",
            "Знает основы PostgreSQL и Git",
            "Пишет тесты в своих проектах",
        ],
        "gaps": ["Нет коммерческого опыта", "Нет опыта командной разработки и код-ревью"],
        "questions": [
            "Расскажите об архитектуре вашего самого большого pet-проекта.",
            "Как вы организуете работу с ветками в Git?",
            "Чем отличаются транзакции на уровне Django ORM и PostgreSQL?",
        ],
        "text": """Иван Петров
Junior Python Developer · Екатеринбург

Проекты
- «Бронь столиков» — Django + DRF + PostgreSQL, Docker Compose, тесты pytest
- Telegram-бот расписания для студентов (aiogram), 400 пользователей
Курсы: Python-разработчик (2024), алгоритмы на LeetCode — 150 задач

Навыки: Python, Django, DRF, PostgreSQL, Docker, Git, pytest
Образование: УрФУ, Информатика, 2024""",
    },
    {
        "name": "Ольга Никитина",
        "decision": "new",
        "score": 47,
        "summary": "Опытный PHP-разработчик, Python знает на базовом уровне.",
        "strengths": ["6 лет веб-разработки (PHP/Laravel)", "Хорошее знание MySQL и REST API"],
        "gaps": ["Python — только курсы", "Нет опыта с Django", "Не работала с PostgreSQL"],
        "questions": [
            "Какие концепции Laravel вы ожидаете встретить в Django?",
            "Что вы уже писали на Python?",
            "Как вы проектировали версионирование REST API?",
        ],
        "text": """Ольга Никитина
Web-разработчик · Ростов-на-Дону

2018–н.в. — PHP-разработчик (Laravel), агентство «Вебпро»
- REST API для мобильных приложений, MySQL, Redis
Сейчас изучаю Python: курс «Python для веб-разработчиков», телеграм-бот на aiogram

Навыки: PHP, Laravel, MySQL, Redis, REST, Git, базовый Python""",
    },
    {
        "name": "Сергей Волков",
        "decision": "rejected",
        "score": 31,
        "summary": "QA-инженер с автотестами на Python; бэкенд-разработкой не занимался.",
        "strengths": ["Пишет автотесты на Python и pytest", "Знает SQL для проверки данных"],
        "gaps": ["Нет опыта бэкенд-разработки", "Нет Django и проектирования API"],
        "questions": [
            "Что из backend-разработки вы уже пробовали сами?",
            "Как бы вы протестировали REST API для создания заказа?",
            "Почему хотите сменить направление?",
        ],
        "text": """Сергей Волков
QA Automation · Самара

2020–н.в. — QA Automation Engineer, «ТелекомСофт»
- Автотесты UI и API на Python (pytest, requests, Selenium)
- Проверка данных в PostgreSQL через SQL
Навыки: Python, pytest, Selenium, Postman, SQL, Jenkins""",
    },
    {
        "name": "Анна Лебедева",
        "decision": "rejected",
        "score": 18,
        "summary": "Frontend-разработчик на React; обязательных бэкенд-навыков нет.",
        "strengths": ["Опыт интеграции фронтенда с REST API"],
        "gaps": ["Нет Python", "Нет Django и PostgreSQL", "Нет бэкенд-опыта"],
        "questions": [
            "Есть ли у вас опыт серверной разработки на любом языке?",
            "Как вы видите свой переход в бэкенд?",
            "С какими REST API вы интегрировались и какие проблемы встречали?",
        ],
        "text": """Анна Лебедева
Frontend Developer · Москва

2021–н.в. — React-разработчик, «Медиа Групп»
- SPA на React + TypeScript, Redux Toolkit
- Интеграция с REST API бэкенда, Storybook, Jest
Навыки: JavaScript, TypeScript, React, Next.js, CSS, Figma""",
    },
]


def _c(name, score, decision, summary, strengths, gaps, questions, text):
    return {
        "name": name, "score": score, "decision": decision, "summary": summary,
        "strengths": strengths, "gaps": gaps, "questions": questions, "text": text,
    }


FRONTEND_VACANCY = {
    "title": "Frontend-разработчик (React)",
    "description": "Делаем личный кабинет клиента и внутреннюю админку. Дизайн-система в Figma, код-ревью, релизы раз в неделю.",
    "must_have": "JavaScript\nTypeScript\nReact\nHTML/CSS\nGit",
    "nice_to_have": "Next.js\nRedux Toolkit\nJest\nFigma",
}

FRONTEND_CANDIDATES = [
    _c("Полина Морозова", 88, "invited",
       "Middle React-разработчик с 4 годами опыта и сильным TypeScript; закрывает все обязательные требования.",
       ["4 года на React и TypeScript", "Строила дизайн-систему на Storybook", "Next.js в продакшене", "Тесты на Jest и Testing Library"],
       ["Мало опыта с Redux Toolkit"],
       ["Как вы организовали версионирование дизайн-системы?", "Когда вы выбираете SSR, а когда SSG в Next.js?", "Как вы тестируете компоненты с асинхронной загрузкой данных?"],
       "Полина Морозова\nFrontend Developer · Москва\n2021–н.в. — «КлаудБанк», React + TypeScript, дизайн-система на Storybook, Next.js\n2020–2021 — веб-студия, вёрстка и JavaScript\nНавыки: React, TypeScript, Next.js, Jest, Testing Library, Figma, Git"),
    _c("Артём Зайцев", 71, "new",
       "Уверенный React-разработчик, но TypeScript использует поверхностно.",
       ["3 года на React", "Redux Toolkit и RTK Query", "Хорошая вёрстка, адаптив"],
       ["TypeScript на базовом уровне", "Нет опыта с тестами"],
       ["Какие типы TypeScript вы используете чаще всего и почему?", "Как бы вы покрыли тестами форму оформления заказа?", "Как вы боретесь с лишними ререндерами?"],
       "Артём Зайцев\nReact Developer · Краснодар\n2022–н.в. — интернет-магазин «Домострой», React, Redux Toolkit, RTK Query\nНавыки: JavaScript, React, Redux, HTML/CSS, SCSS, Git, базовый TypeScript"),
    _c("Кирилл Соколов", 52, "new",
       "Junior-разработчик с хорошим портфолио pet-проектов, без коммерческого опыта.",
       ["Pet-проекты на React и TypeScript", "Аккуратная вёрстка по макетам Figma"],
       ["Нет коммерческого опыта", "Не работал в команде с код-ревью"],
       ["Расскажите о самом сложном баге в вашем pet-проекте.", "Как вы храните состояние формы из 10 полей?", "Что такое ключи в списках React и зачем они нужны?"],
       "Кирилл Соколов\nJunior Frontend · Воронеж\nПроекты: трекер задач (React + TypeScript + Vite), лендинги по макетам Figma\nКурсы: Frontend-разработчик, 2024\nНавыки: JavaScript, TypeScript, React, HTML/CSS, Git"),
    _c("Денис Фролов", 24, "rejected",
       "Backend-разработчик на Java; фронтенд-опыта почти нет.",
       ["Сильная инженерная база", "Знает Git и командные процессы"],
       ["Нет React", "Нет TypeScript", "Вёрстка только на уровне основ"],
       ["Что вы уже делали на фронтенде?", "Почему хотите перейти во фронтенд?", "Как вы видите разницу между серверным и клиентским рендерингом?"],
       "Денис Фролов\nJava Developer · Пермь\n2019–н.в. — Spring Boot, PostgreSQL, Kafka\nНавыки: Java, Spring, SQL, Git, немного HTML/CSS"),
]

ANALYST_VACANCY = {
    "title": "Аналитик данных (Junior+)",
    "description": "Аналитика маркетплейса: дашборды для категорийных менеджеров, A/B-тесты, исследования поведения покупателей.",
    "must_have": "SQL\nPython\nPandas\nExcel\nСтатистика",
    "nice_to_have": "Power BI или Tableau\nA/B-тесты\nAirflow",
}

ANALYST_CANDIDATES = [
    _c("Виктория Ершова", 86, "invited",
       "Сильный junior+ аналитик: уверенный SQL и Python, опыт A/B-тестов в e-commerce.",
       ["2 года аналитики в e-commerce", "Сложный SQL: оконные функции, CTE", "Проводила A/B-тесты и считала значимость", "Дашборды в Power BI"],
       ["Нет опыта с Airflow"],
       ["Как вы выбирали размер выборки для A/B-теста?", "Приведите пример запроса с оконной функцией из вашей работы.", "Какой дашборд принёс бизнесу самую большую пользу?"],
       "Виктория Ершова\nData Analyst · Москва\n2023–н.в. — маркетплейс «Корзинка», SQL, Python (pandas), A/B-тесты, Power BI\nОбразование: ВШЭ, Экономика\nНавыки: SQL, Python, Pandas, SciPy, Power BI, Excel"),
    _c("Никита Кузнецов", 63, "new",
       "Аналитик с сильным Excel и SQL, Python изучает.",
       ["Уверенный SQL", "Продвинутый Excel: сводные, Power Query", "Понимание продуктовых метрик"],
       ["Python и pandas на базовом уровне", "Нет опыта A/B-тестов"],
       ["Какие задачи вы уже решали на Python?", "Как бы вы проверили, что рост конверсии не случайный?", "Как посчитать retention по когортам в SQL?"],
       "Никита Кузнецов\nБизнес-аналитик · Нижний Новгород\n2022–н.в. — розничная сеть, отчётность в Excel и SQL (MS SQL)\nСейчас прохожу курс Python для анализа данных\nНавыки: SQL, Excel, Power Query, базовый Python"),
    _c("Татьяна Романова", 45, "new",
       "Маркетолог с аналитическими задачами; техническая база слабее требуемой.",
       ["Опыт работы с веб-аналитикой", "Понимает маркетинговые метрики"],
       ["SQL на начальном уровне", "Нет Python", "Нет опыта со статистикой"],
       ["Какие SQL-запросы вы писали сами?", "Как вы считаете ROMI кампании?", "Что для вас статистическая значимость?"],
       "Татьяна Романова\nИнтернет-маркетолог · Казань\n2020–н.в. — контекстная реклама, Яндекс Метрика, отчёты в Google Sheets\nНавыки: Метрика, Google Sheets, базовый SQL"),
    _c("Глеб Павлов", 29, "rejected",
       "Студент без опыта, знаком с аналитикой по учебным курсам.",
       ["Учебные проекты на Python"],
       ["Нет коммерческого опыта", "SQL только по курсу", "Нет опыта с BI-инструментами"],
       ["Расскажите об учебном проекте, которым гордитесь.", "Как бы вы нашли топ-10 товаров по выручке в SQL?", "Чем медиана отличается от среднего и когда что использовать?"],
       "Глеб Павлов\nСтудент 3 курса · Томск\nУчебные проекты: анализ датасета Kaggle в Jupyter\nНавыки: Python, базовый SQL"),
]

ALL_VACANCIES = [
    (VACANCY, CANDIDATES),
    (FRONTEND_VACANCY, FRONTEND_CANDIDATES),
    (ANALYST_VACANCY, ANALYST_CANDIDATES),
]


# name -> (age, position, city, years of experience, key skills)
PROFILES: dict[str, tuple[int, str, str, int, list[str]]] = {
    "Алексей Смирнов": (31, "Senior Backend-разработчик", "Москва", 7, ["Python", "Django", "DRF", "PostgreSQL", "Celery", "Redis", "Docker", "GitLab CI"]),
    "Мария Ковалёва": (27, "Backend-разработчик", "Санкт-Петербург", 3, ["Python", "FastAPI", "Django", "PostgreSQL", "SQLAlchemy", "Docker", "pytest"]),
    "Дмитрий Орлов": (35, "Django-разработчик", "Казань", 4, ["Python", "Django", "DRF", "PostgreSQL", "Linux", "nginx"]),
    "Екатерина Белова": (29, "Data Engineer", "Новосибирск", 3, ["Python", "SQL", "PostgreSQL", "Airflow", "Pandas", "Flask", "Docker"]),
    "Иван Петров": (22, "Junior Python-разработчик", "Екатеринбург", 0, ["Python", "Django", "DRF", "PostgreSQL", "Docker", "aiogram"]),
    "Ольга Никитина": (34, "PHP-разработчик", "Ростов-на-Дону", 6, ["PHP", "Laravel", "MySQL", "Redis", "REST", "Python (базовый)"]),
    "Сергей Волков": (30, "QA Automation Engineer", "Самара", 4, ["Python", "pytest", "Selenium", "SQL", "Jenkins"]),
    "Анна Лебедева": (26, "Frontend-разработчик", "Москва", 3, ["JavaScript", "TypeScript", "React", "Next.js", "Redux"]),
    "Полина Морозова": (28, "Frontend-разработчик", "Москва", 4, ["TypeScript", "React", "Next.js", "Storybook", "Jest", "Figma"]),
    "Артём Зайцев": (25, "React-разработчик", "Краснодар", 3, ["JavaScript", "React", "Redux Toolkit", "RTK Query", "SCSS"]),
    "Кирилл Соколов": (21, "Junior Frontend-разработчик", "Воронеж", 0, ["JavaScript", "TypeScript", "React", "Vite", "HTML/CSS"]),
    "Денис Фролов": (33, "Java-разработчик", "Пермь", 6, ["Java", "Spring Boot", "PostgreSQL", "Kafka"]),
    "Виктория Ершова": (24, "Аналитик данных", "Москва", 2, ["SQL", "Python", "Pandas", "SciPy", "Power BI", "A/B-тесты"]),
    "Никита Кузнецов": (27, "Бизнес-аналитик", "Нижний Новгород", 3, ["SQL", "Excel", "Power Query", "MS SQL"]),
    "Татьяна Романова": (32, "Интернет-маркетолог", "Казань", 5, ["Яндекс Метрика", "Google Sheets", "Контекстная реклама"]),
    "Глеб Павлов": (20, "Студент, аналитик-стажёр", "Томск", 0, ["Python", "Jupyter", "SQL (базовый)"]),
}
