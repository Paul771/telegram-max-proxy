# Тестирование telegram-max-proxy

## Обзор

Проект содержит комплексный набор тестов для проверки функциональности telegram-max-proxy.

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Общие фикстуры и настройки
├── unit/                    # Unit тесты
│   ├── __init__.py
│   ├── test_telegram_models.py    # Тесты моделей Telegram
│   ├── test_max_models.py         # Тесты моделей MAX
│   ├── test_telegram_adapter.py   # Тесты Telegram адаптера
│   ├── test_max_adapter.py        # Тесты MAX адаптера
│   └── test_proxy_service.py      # Тесты прокси-сервиса
└── integration/             # Интеграционные тесты
    ├── __init__.py
    └── test_integration.py        # End-to-end тесты
```

## Статистика тестов

### Unit тесты
- **Всего тестов**: 109
- **Успешно**: 109 (100%)
- **Провалено**: 0

### Покрытие кода
- **Общее покрытие**: 71%
- **Модели**: 100%
- **Адаптеры**: 84-91%
- **Сервисы**: 90%

## Запуск тестов

### Все unit тесты
```bash
.\venv\Scripts\Activate.ps1
pytest tests/unit/ -v
```

### С покрытием кода
```bash
pytest tests/unit/ -v --cov=. --cov-report=html --cov-report=term-missing
```

### Только определенный модуль
```bash
pytest tests/unit/test_telegram_models.py -v
```

### Интеграционные тесты
```bash
pytest tests/integration/ -v -m integration
```

### Все тесты
```bash
pytest tests/ -v
```

## Категории тестов

### 1. Тесты моделей (test_*_models.py)
- Валидация данных Pydantic
- Сериализация/десериализация
- Обязательные и опциональные поля
- Граничные значения

### 2. Тесты адаптеров (test_*_adapter.py)
- HTTP клиенты (Telegram и MAX API)
- Отправка и получение сообщений
- Обработка ошибок
- Управление соединениями
- Webhook операции

### 3. Тесты сервисов (test_proxy_service.py)
- Маршрутизация сообщений
- Конвертация форматов
- Маппинг чатов
- Обработка inline клавиатур
- Обработка ошибок

### 4. Интеграционные тесты (test_integration.py)
- End-to-end потоки
- API endpoints
- Жизненный цикл клиентов
- Конкурентная обработка

## Фикстуры

Основные фикстуры определены в `conftest.py`:

- `telegram_bot_token` - тестовый токен Telegram
- `max_api_token` - тестовый токен MAX
- `chat_user_mapping` - маппинг чатов
- `telegram_user`, `telegram_chat`, `telegram_message` - модели Telegram
- `max_user`, `max_message`, `max_update` - модели MAX
- `mock_telegram_client`, `mock_max_client` - моки клиентов
- `proxy_service` - сервис с моками

## Отчеты о покрытии

HTML отчет генерируется в директории `htmlcov/`:
```bash
# Открыть отчет
start htmlcov/index.html  # Windows
```

## Маркеры тестов

- `@pytest.mark.unit` - unit тесты
- `@pytest.mark.integration` - интеграционные тесты
- `@pytest.mark.slow` - медленные тесты
- `@pytest.mark.asyncio` - асинхронные тесты

## Примеры использования

### Запуск только быстрых тестов
```bash
pytest tests/ -v -m "not slow"
```

### Запуск с подробным выводом
```bash
pytest tests/ -vv --tb=long
```

### Запуск с остановкой на первой ошибке
```bash
pytest tests/ -x
```

## Зависимости для тестирования

```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
```

## Рекомендации

1. Запускайте тесты перед каждым коммитом
2. Поддерживайте покрытие кода выше 80%
3. Добавляйте тесты для новой функциональности
4. Используйте моки для внешних API
5. Пишите понятные имена тестов

## Troubleshooting

### Ошибка импорта модулей
```bash
# Убедитесь, что виртуальное окружение активировано
.\venv\Scripts\Activate.ps1

# Переустановите зависимости
pip install -r requirements.txt
```

### Тесты не находятся
```bash
# Проверьте pytest.ini и структуру директорий
pytest --collect-only
```

### Проблемы с async тестами
```bash
# Убедитесь, что установлен pytest-asyncio
pip install pytest-asyncio
```
