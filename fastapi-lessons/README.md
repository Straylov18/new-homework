# Курс уроков по созданию backend приложений с использованием fastapi

## Урок 1

Темы урока:
- Установка зависимостей используя **poetry**
- Настройка простого приложения на фреймворке **fastapi**
- Примеры обработки базовых типов REST запросов в fastapi
- Асинхронный запуск приложения через **uvicorn**

[Итоговый проект урока 1](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-01-first-endpoint)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-01-first-endpoint/README.md)

## Урок 2

Темы урока:
- Получение настроечных переменных из окружения системы
- Использование файла **.env** для хранения переменных окружения

[Итоговый проект урока 2](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-02-environment-variables)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-02-environment-variables/README.md)

## Урок 3

Темы урока:
- Проблемы, возникающие при написании больших приложений
- Разбиение логики работы приложения на слои на примере слоя описания ручек 

[Итоговый проект урока 3](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-03-separating-project-layers)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-03-separating-project-layers/README.md)

## Урок 4

Темы урока:
- Валидация данных во время обработки запросов
- Описание более подробной документации ручек при помощи pydantic

[Итоговый проект урока 4](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-04-check-rest-content-structure)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-04-check-rest-content-structure/README.md)

## Урок 5

Темы урока:
- Подключение базы данных на примере SQLite
- Описание слоя моделей для взаимодействия с базами данных
- Настройка таблиц баз данных через миграции
- Автоматическая генерация миграций на основе моделей
- Введение в SQL
- Обновление данных в базе данных и получение данных из базы данных при помощи sqlalchemy

[Итоговый проект урока 5](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-05-connect-to-db)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-05-connect-to-db/README.md)

## Урок 6

Темы урока:
- Запуск базы данных как отдельный сервис на примере PostgreSQL
- Небольшое введение в Docker
- Запуск PostgreSQL базы данных через docker контейнер

[Итоговый проект урока 6](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-06-postgres)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-06-postgres/README.md)

## Урок 7

Темы урока:
- Создание связей между таблицами реляционной БД
- Типы связей между таблицами и случаи их применения
- Более удобная сериализация моделей

[Итоговый проект урока 7](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-07-sql-db-relation-types)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-07-sql-db-relation-types/README.md)

## Урок 8

Темы урока:
- Построение более сложных запросов с фильтрацией
- Отладка генерируемых SQL запросов

[Итоговый проект урока 8](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-08-db-more-complex-request)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-08-db-more-complex-request/README.md)

## Урок 9

Темы урока:
- Аргументы таблиц БД (индексы, ограничения итд.)

[Итоговый проект урока 9](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-09-db-indexes)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-09-db-indexes/README.md)

## Урок 10

Темы урока:
- Установки зависимостей отдельными группами
- Проверка стиля кода с использованием python библиотеки flake8
- Настройка стилизации проекта в pyproject.toml

[Итоговый проект урока 10](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-10-linting-code)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-10-linting-code/README.md)

## Урок 11

Темы урока:
- Улучшение логирования приложения

[Итоговый проект урока 11](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-11-logs-format)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-11-logs-format/README.md)

## Урок 12

Темы урока:
- Авторизация
- Аутентификация
- Аутентификация с помощью session_id и с помощью jwt токенов
- Передача токенов через хэдеры запросов
- Передача токенов через cookies в запросах
- Хранение паролей в хэшированом виде

[Итоговый проект урока 12](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-12-auth)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-12-auth/README.md)

## Урок 13

Темы урока:
- Хранение данных пользователей в БД
- Безопасное хранение паролей в хэшированом виде

[Итоговый проект урока 13](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-13-auth-db)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-13-auth-db/README.md)

## Урок 14

Темы урока:
- Получение одного или нескольких файлов
- Отправка файлов
- Потоковая отправка файлов

[Итоговый проект урока 14](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-14-files-in-requests)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-14-files-in-requests/README.md)

## Урок 15

Темы урока:
- Unit тесты (на примере pytest)
- Тесты исключений
- Запуск конкретных тестов или запуск тестов по определенным фильтрам
- Параметризированный запуск тестов через матрицу проверочных значений 
- Запуск тестов в определенной последовательности

[Итоговый проект урока 15](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-15-unit-tests)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-15-unit-tests/README.md)

## Урок 16

Темы урока:
- Конфигурация pytest
- Многопоточный запуск тестов
- Покрытие тестов (в том числе покрытие по ветвям)
- Генерация отчетов о тестировании

[Итоговый проект урока 16](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/fastapi-lessons/l-16-tests-configuration)

[Описание хода урока](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/l-16-tests-configuration/README.md)



[//]: # (TODO дальнейшие уроки)
