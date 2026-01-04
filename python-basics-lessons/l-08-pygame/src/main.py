import pygame
import random

pygame.init()

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 800

PLAYER_RADIUS = 10
PLAYER_VELOCITY = 5

COOKIE_RADIUS = 15
COOKIES_NUMBER = 25

screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Поедатель печенек")

game_time = 0

player_pos = [DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2]

cookies = [(random.randint(0, DISPLAY_WIDTH), random.randint(0, DISPLAY_HEIGHT)) for _ in range(COOKIES_NUMBER)]

# Игровой цикл
dt = 0
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
    # Отрисовка игровых сущностей
    for c in cookies:
        pygame.draw.circle(screen, "yellow", c, COOKIE_RADIUS)
    # Отрисовка таймера
    font1 = pygame.font.SysFont('freesanbold.ttf', 50)
    text_your_time = font1.render(f'{game_time:.2f} сек.', True, (255, 0, 0))
    text_rect_your_time = text_your_time.get_rect()
    text_rect_your_time.center = (DISPLAY_WIDTH / 2, 50)
    screen.blit(text_your_time, text_rect_your_time)

    # Обработка нажатий на клавиши игроком
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= PLAYER_VELOCITY *60*dt
    if keys[pygame.K_RIGHT] and player_pos[0] < DISPLAY_WIDTH:
        player_pos[0] += PLAYER_VELOCITY *60*dt
    if keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= PLAYER_VELOCITY *60*dt
    if keys[pygame.K_DOWN] and player_pos[1] < DISPLAY_HEIGHT:
        player_pos[1] += PLAYER_VELOCITY *60*dt

    # Обход печенек с конца (с конца чтобы легче было их удалять в случае съедания)
    for i in range(len(cookies) - 1, -1, -1):
        # Удаление печеньки, если пользователь соприкоснулся с ней
        dx = player_pos[0] - cookies[i][0]
        dy = player_pos[1] - cookies[i][1]
        sum_r = PLAYER_RADIUS + COOKIE_RADIUS
        if (dx * dx) + (dy * dy) < (sum_r * sum_r):
            cookies.pop(i)
            PLAYER_RADIUS += 3
            PLAYER_VELOCITY += 0.5

    # Подсчет прошедшего времени
    dt = clock.tick(60) / 1000
    game_time += dt

    # Поменять кадр на экране
    pygame.display.flip()

# Корректное закрытие всех модулей Pygame
pygame.quit()
