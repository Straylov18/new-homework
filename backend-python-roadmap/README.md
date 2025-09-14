# Путь становления python backend разработчика

В данном документе предлагается последовательность изучения технологий 
для начинающего backend разработчика.

## Основы Python

[Курс python для начинающих](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/python-basic-lessons/README.md).

## Базовое понимание сетевых взаимодействий между web приложениями

Поскольку backend приложения зачастую взаимодействуют с frontend приложениями, 
backend разработчик должен иметь хотя бы базовое представление о работе сетевых протоколов.
[Курс по основам сетевых взаимодействий](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/network-basics/README.md).

## Backend фреймворк (FastAPI)

[Курс уроков по FastAPI](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/README.md).

## Базы данных

После изучения базового курса по FastAPI 
рекомендуется продолжить изучение типов БД и механизмов взаимодействия с ними.

### SQL

В рамках [курса уроков по FastAPI](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/README.md)
рассматривается взаимодействие с SQL базами данных на примере взаимодействия FastAPI с SQLite и PostgreSQL.
Однако backend разработчик должен уметь в случае чего делать запросы к реляционным БД с помощью SQL запросов, 
и должен понимать специфику работы с конкретной реляционной БД (хоть во многом они и похожи).

Так что предлагается пощупать другие SQL базы данных самостоятельно.

### No-SQL базы данных

В рамках [курса уроков по FastAPI](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/fastapi-lessons/README.md)
рассматривается взаимодействие с SQL базами данных на примере MongoDB.
Также предлагается ознакомиться с еще одним-двумя вариантами no-sql баз данных 
(например рассмотреть примеры использования in-memory баз данных на подобии Celery или Redis).

## Тестирование

[//]: # (TODO unit, integrational, etc)

## Docker

Базовый курс для ознакомления с базовыми принципами запуска Docker контейнеров.
[введение в Docker](https://github.com/TheYeniseiTrireme/homework-materials/blob/main/docker-basics/README.md)

[//]: # (TODO сборка проектов с помощью docker и их запуск с помощью docker-compose)
