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

PLAYER_RADIUS = 30
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
    # Поменять кадр на экране
    pygame.display.flip()

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
    
    # Лочим FPS на 60 кадрах
    clock.tick(60)

# Корректное закрытие всех модулей Pygame
pygame.quit()
```
Здесь:
- мы вынесли разрешение экрана в константы ```DISPLAY_WIDTH```, ```DISPLAY_HEIGHT```
- добавили объект, учитывающий время в игре ```clock = pygame.time.Clock()```
- задали игроку начальное положение в центре экрана 
```player_pos = [DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2]```
- каждую итерацию игрового цикла производим отрисовку игрока
```python
# Отчистка экрана
screen.fill("black")
# Отрисовка игрока
pygame.draw.circle(screen, "red", player_pos, PLAYER_RADIUS)
# Поменять кадр на экране
pygame.display.flip()
```
- проверяем нажатие клавиш и положение игрока 
(```keys[pygame.K_LEFT] and player_pos[0] > 0```)
и в случае, если клавиша движения нажата, и игрок может двигаться в нужном направлении, 
мы его двигаем (```player_pos[0] -= PLAYER_VELOCITY```)
- стабилизируем FPS на 60-и кадрах в секунду (```clock.tick(60)```)

## Игра "Поедатель печенек"

Теперь напишем игру, в которой нужно будет поедать печеньки на скорость.
Ты можешь запустить проект, чтобы увидеть финальную версию.

Поскольку дальше у нас кода будет становиться сильно больше, 
распишем все через классы и распихаем по отдельным файлам 
(так, как мы научились в предыдущих уроках).

Для начала вынесем все игровые константы в отдельный файл **src/game_constants.py**:
```python
import pygame

pygame.init()

TEXT_FONT = pygame.font.SysFont('freesanbold.ttf', 50)

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 800

PLAYER_INITIAL_RADIUS = 10
PLAYER_RADIUS_INCREASING = 7
PLAYER_INITIAL_VELOCITY = 250
PLAYER_VELOCITY_INCREASING = 40

COOKIE_RADIUS = 15
COOKIES_NUMBER = 30
```
Здесь мы зададим все необходимые для игры константы, 
чтобы их можно было менять в одном месте не бегая по разным файлам, 
таким образом быстро подкручивать правила игры в случае чего.
Также инициализируем модули pygame в этом файле 
и зададим шрифты для дальнейшего вывода текста.

Далее вынесем обработку игрока в отдельный класс:
```python
import pygame

from game_constants import (DISPLAY_HEIGHT, DISPLAY_WIDTH,
                            PLAYER_INITIAL_RADIUS, PLAYER_INITIAL_VELOCITY)


class Player:

    def __init__(self):
        self.x = DISPLAY_WIDTH / 2
        self.y = DISPLAY_HEIGHT / 2
        self.v = PLAYER_INITIAL_VELOCITY
        self.radius = PLAYER_INITIAL_RADIUS

    def handle_keys(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.v * dt
        if keys[pygame.K_RIGHT] and self.x < DISPLAY_WIDTH:
            self.x += self.v * dt
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.v * dt
        if keys[pygame.K_DOWN] and self.y < DISPLAY_HEIGHT:
            self.y += self.v * dt

    def draw(self, screen):
        pygame.draw.circle(screen, "red", (self.x, self.y), self.radius)
```
Здесь мы описываем обработку нажатий на клавиши, 
отрисовку и прочую логику, связанную с игроком.

Также сделаем класс печенек в ```src/cookie.py``` (которые мы будем потом съедать):
```python
import random

import pygame

from game_constants import (COOKIE_RADIUS, COOKIES_NUMBER, DISPLAY_HEIGHT,
                            DISPLAY_WIDTH)


class Cookie:

    @classmethod
    def generate_cookies_list(cls, number_of_cookies=COOKIES_NUMBER) -> list:
        output_cookies = []
        for _ in range(number_of_cookies):
            output_cookies.append(cls())
        return output_cookies

    def __init__(self):
        self.x = random.randint(0, DISPLAY_WIDTH)
        self.y = random.randint(0, DISPLAY_HEIGHT)
        self.radius = COOKIE_RADIUS

    def draw(self, screen):
        pygame.draw.circle(screen, "yellow", (self.x, self.y), self.radius)
```

Всю информацию об объектах на экране, 
и вообще состоянии игры мы можем также вынести в отдельный класс в **src/game_scene.py**:
```python
import pygame

from cookie import Cookie
from game_constants import (COOKIE_RADIUS, DISPLAY_HEIGHT, DISPLAY_WIDTH,
                            PLAYER_RADIUS_INCREASING,
                            PLAYER_VELOCITY_INCREASING)
from information_renderer import InfoRenderer
from player import Player


class GameScene:
    def __init__(self):
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Поедатель печенек")

        self.player = Player()
        self.cookies = Cookie.generate_cookies_list()

        self.dt = 0
        self.game_time = 0
        self.clock = pygame.time.Clock()

        self.best_time = None

    def _restart_game(self):
        self.player = Player()
        self.cookies = Cookie.generate_cookies_list()
        self.dt = 0
        self.game_time = 0

    def _check_restart_call(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self._restart_game()

    def _check_collisions(self):
        # Обход печенек с конца (с конца чтобы легче было их удалять в случае съедания)
        for i in range(len(self.cookies) - 1, -1, -1):
            # Удаление печеньки, если пользователь соприкоснулся с ней
            dx = self.player.x - self.cookies[i].x
            dy = self.player.y - self.cookies[i].y
            sum_r = self.player.radius + COOKIE_RADIUS
            if (dx * dx) + (dy * dy) < (sum_r * sum_r):
                self.cookies.pop(i)
                self.player.radius += PLAYER_RADIUS_INCREASING
                self.player.v += PLAYER_VELOCITY_INCREASING

    def _handle_time(self):
        # Подсчет прошедшего времени в секундах
        self.dt = self.clock.tick(60) / 1000
        # Если еще остались печеньки прибавляем текущее время
        if len(self.cookies) > 0:
            self.game_time += self.dt
        elif self.best_time is None or self.best_time > self.game_time:
            # Если игра закончилась и игрок успел за более короткое время, то новый рекорд - текущее время
            self.best_time = self.game_time

    def draw_all(self):
        # Отчистка экрана
        self.screen.fill("black")
        # Отрисовка игрока
        self.player.draw(self.screen)
        # Отрисовка игровых сущностей
        for c in self.cookies:
            c.draw(self.screen)
        # Отрисовка таймера
        InfoRenderer.render_time(self.game_time, self.screen)
        if len(self.cookies) < 1:
            InfoRenderer.render_win_screen(self.game_time, self.best_time, self.screen)
        # Поменять кадр на экране
        pygame.display.flip()

    def handle_game_logic(self):
        # Обработка нажатий на клавиши игроком
        self.player.handle_keys(self.dt)
        self._check_restart_call()
        self._check_collisions()
        self._handle_time()
```
Здесь каждый логически обособленный блок обработки игровой логики мы выносим в отдельный метод, 
чтобы код был более читаемый.
Так, мы отдельно описываем отрисовку всех объектов, все коллизии, все нажатия на кнопки.

Описание вывода текста же здесь вынесено в отдельный файл **src/information_renderer.py**:
```python
import pygame

from game_constants import DISPLAY_HEIGHT, DISPLAY_WIDTH, TEXT_FONT


class InfoRenderer:

    @staticmethod
    def _render_text(text, color, x, y, screen):
        pygame_text = TEXT_FONT.render(text, True, color)
        rect_text = pygame_text.get_rect()
        rect_text.center = (x, y)
        screen.blit(pygame_text, rect_text)

    @classmethod
    def render_time(cls, game_time, screen):
        cls._render_text(
            f'{game_time:.2f} сек.',
            (255, 0, 0),
            DISPLAY_WIDTH / 2,
            50,
            screen
        )

    @classmethod
    def render_win_screen(cls, game_time, best_time, screen):
        rect1 = pygame.Rect((DISPLAY_WIDTH / 2 - 250, DISPLAY_HEIGHT / 2 - 100, 500, 200))
        panel_color = (100, 150, 255)
        if best_time >= game_time:
            panel_color = (125, 255, 150)
        pygame.draw.rect(screen, panel_color, rect1)
        cls._render_text(
            f'Ты съел все за {game_time:.2f} сек.',
            (255, 0, 0),
            DISPLAY_WIDTH / 2,
            DISPLAY_HEIGHT / 2 - 65,
            screen
        )
        cls._render_text(
            '"Enter" - начать заново.',
            (255, 0, 0),
            DISPLAY_WIDTH / 2,
            DISPLAY_HEIGHT / 2,
            screen
        )
        text_about_record = f'Наилучший результат: {best_time:.2f}'
        if best_time >= game_time:
            text_about_record = 'Новый рекорд!'
        cls._render_text(
            text_about_record,
            (255, 0, 0),
            DISPLAY_WIDTH / 2,
            DISPLAY_HEIGHT / 2 + 65,
            screen
        )
```

И тогда по итогу **src/main..py** будет выглядеть 
как просто пара инициализаций классов и вызов пары функций:
```python
import pygame

from game_scene import GameScene

pygame.init()

scene = GameScene()

# Игровой цикл
run_game_loop = True
while run_game_loop:
    # Обработка события выхода
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run_game_loop = False
    scene.draw_all()
    scene.handle_game_logic()

# Корректное закрытие всех модулей Pygame
pygame.quit()
```

Ты же можешь попробовать написать свою игру и структурировать в ней код так, 
чтобы к нему можно было легко прикручивать новые фичи.

Подробнее о функционале библиотеки pygame ты сможешь узнать тут:
https://pg1.readthedocs.io/en/latest/index.html.
