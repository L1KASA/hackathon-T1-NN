# Hackathon T1 NN

*Участники:*
- Тахмазова Анжелика (@tahmazova) - Backend
- Алмаз Зиастинов (@almaz_ziastinov) - ML
- Данила Толстов (@onlyoneIDK) - ML

## Инструкция по локальному развертыванию
1. Заполнить .env (пример в .env.example).
2. Выполнить `docker compose -f docker-compose.dev.yml up -d`.
3. Применить миграции в alembic: `docker-compose -f docker-compose.dev.yml run --rm web alembic upgrade head`

## Создать и применить миграцию в alembic
```
docker-compose -f docker-compose.dev.yml run --rm web alembic revision --autogenerate -m "Fix employee skills relationships"
docker-compose -f docker-compose.dev.yml run --rm web alembic upgrade head
```

## Запуск линтеров
```
docker-compose -f docker-compose.dev.yml exec app poetry run ruff check app --fix
docker-compose -f docker-compose.dev.yml exec app poetry run mypy app
```


## Пересобрать Docker образ:
```
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```
## Открыть документацию можно с помощью Swagger UI: http://localhost:8000/docs

## Если нужно посмотреть ERD для БД, необходимо:
### 1. Раскомментить в docker-compose.dev.yml pgAdmin
### 2. Перейти по http://localhost:8080, ввести логин и пароль: из .env.
### 3. Добавить сервер в pgAdmin (Правой кнопкой на "Servers" → "Create" → "Server"), указать данные из `.env`.
### 4. Сохранить с помощью кнопки Save.
### 5. Нажать по hr_consultant_db правой кнопкой мыши и выбрать ERD for Database.

## Описание таблиц

- **Employee** – базовая таблица сотрудников.
- **Skill** и **EmployeeSkill** – для описания навыков и их владения сотрудниками.
- **ExperiencePoints** – учет опыта, полученного сотрудником за действия.
- **Level** – уровни, соответствующие накопленному опыту.
- **Reward** и **EmployeeReward** – система наград и их получение.
- **Quest** и **EmployeeQuest** – квесты/миссии и их выполнение сотрудниками.
- **CareerRoadmap** и связанные таблицы – карьера и связанные требования.
- **Leaderboard** и связанные таблицы – рейтинги и критерии.
- **Tip** – система взаимных благодарностей между сотрудниками (tip).
- **Project** – таблица проектов.
- **ProjectRequiredSkill** – требуемые навыки для проектов.

## Технологический стек
- **Backend**: FastAPI (высокая производительность, асинхронность)

- **База данных**: PostgreSQL + SQLAlchemy (Async) (надежность и скорость)

- **Качество кода**: Ruff (линтер), Mypy (статическая типизация)

- **Контейнеризация**: Docker & Docker Compose (легкость развертывания)

- **Управление зависимостями**: Poetry (современный и удобный инструмент)

## Возможные точки роста/улучшения
- **Интерфейсы (ABCs)**: Для Repository и Service классов можно создать абстрактные базовые классы, чтобы явнее обозначить контракты и упростить подмену реализаций (например, для тестов).

- **Фоновая очередь задач (Celery/ARQ)**: Обработку событий, особенно тяжелых, можно выносить в фоновые задачи, чтобы не блокировать HTTP-ответ.

- **Кеширование (Redis)**: Для часто запрашиваемых данных, например, прогресса по квестам или списка навыков.

- **Более сложная система событий**: Использование специализированных библиотек как broadcaster или pyvent для настоящего Pub/Sub с брокерами сообщений (Redis, Kafka).

- **Unit-тесты**: Благодаря DI и разделению слоев, каждый компонент (сервисы, роутеры) легко покрывается модульными и интеграционными тестами.