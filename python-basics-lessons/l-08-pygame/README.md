# Создание простенькой игры на библиотеке pygame

Применим наши знания о python на практике. 
Чтобы было интереснее и нагляднее напишем простенькую игру.

## Настройка зависимостей проекта

В этом уроке мы будем разрабатывать телеграм бота на основе библиотеки pygame.
Существует множество библиотек для разработки игр на python.
Данная библиотека является самой простой для изучения, 
поскольку полноценное написание игр требует большого количества дополнительных знаний, 
в которые мы не будем сильно углубляться в рамках данного курса.

Для начала создадим простой python проект,
который будет состоять из одного пакета **src**.
Внутри пакета **src** будут лежать пустой **__init__.py** 
и **main.py** с логикой работы приложения.

Поскольку проект будет использовать сторонние зависимости
(как минимум тот же pygame),
для начала нужно подгрузить их в проект.
Подгружать зависимости будем с помощью библиотеки poetry.
Ее можно установить в linux с помощью команды:
```shell
curl -sSL https://install.python-poetry.org | python3
```
или же через pipx:
```shell
pipx install poetry
```

Файл с зависимостями **pyproject.toml** (и прочими настройками проекта)
можно создать с помощью того же poetry.
Для этого в корневой директории проекта 
(в данном примере корневая папка это **l-08-pygame**) выполним команду:
```shell
poetry init
```
Данная команда в интерактивном режиме поможет заполнить базовые настройки проекта.
Также данная команда создать директорию окружения проекта **.venv**, 
в которую и устанавливаются все зависимости.

Если нужно добавить зависимости уже после создания проекта, 
это можно сделать с помощью команды:
```shell
poetry add pygame
```
В данном случае добавим в зависимости библиотеку pygame.

Дальше нужно установить зависимости нашего проекта:
```shell
poetry lock
poetry install
```

## Простейшая игра

Напишем Простой код, которой для начала будет запускать игру в отдельном окне:
```python
import pygame

# Инициализация модулей pygame
pygame.init()

# Создание экрана для отрисовки
screen = pygame.display.set_mode((1000, 800))

# Игровой цикл
run_game_loop = True
while run_game_loop:
    # Обработка события выхода
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run_game_loop = False

# Корректное закрытие всех модулей Pygame
pygame.quit()
```
Здесь:
- происходит инициализация так модулей pygame (```pygame.init()```)
- создание объекта, описывающий экран внутри окна с разрешением 1000 на 800 
(```screen = pygame.display.set_mode((1000, 800))```)
- запуск основного вечного игрового цикла, 
в котором в дальнейшем будет описана логика игры, отрисовка кадров, итд.
(```while run_game_loop:```)
- проверка не закрыл ли пользователь окно во время игрового цикла, 
чтобы в случае чего остановить его
- завершение работы модулей pygame (```pygame.quit()```)

Запустим получившееся оконное приложение:
```shell
poetry run python src/main.py
```

Сейчас мы увидим просто черный экран.
Чтобы было интереснее добавим игрока, 
которым мы сможем управлять при помощи кнопок стрелок:
```python
import pygame

# Инициализация модулей pygame
pygame.init()

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 800

PLAYER_VELOCITY = 5

# Создание экрана для отрисовки
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
# Создание игрового таймера для проверки прошедшего времени
clock = pygame.time.Clock()

player_pos = [DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2]

run_game_loop = True
while run_game_loop:
    # Обработка события выхода
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run_game_loop = False

    # Отчистка экрана
    screen.fill("black")
    # Отрисовка игрока
    pygame.draw.circle(screen, "red", player_pos, PLAYER_RADIUS)

    # Обработка нажатий на клавиши игроком
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= PLAYER_VELOCITY
    if keys[pygame.K_RIGHT] and player_pos[0] < DISPLAY_WIDTH:
        player_pos[0] += PLAYER_VELOCITY
    if keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= PLAYER_VELOCITY
    if keys[pygame.K_DOWN] and player_pos[1] < DISPLAY_HEIGHT:
        player_pos[1] += PLAYER_VELOCITY

    # Поменять кадр на экране
    pygame.display.flip()
    
    # Лочим FPS на 60 кадрах
    clock.tick(60)

# Корректное закрытие всех модулей Pygame
pygame.quit()
```
Здесь:

[//]: # (TODO)

