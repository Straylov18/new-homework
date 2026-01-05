import pygame

from cookie import Cookie
from game_constants import COOKIE_RADIUS, DISPLAY_HEIGHT, DISPLAY_WIDTH, PLAYER_RADIUS_INCREASING, PLAYER_VELOCITY_INCREASING
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

    def restart_game(self):
        self.player = Player()
        self.cookies = Cookie.generate_cookies_list()
        self.dt = 0
        self.game_time = 0

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
        # Обработка перезапуска игры
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.restart_game()
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
        # Подсчет прошедшего времени в секундах
        self.dt = self.clock.tick(60) / 1000
        if len(self.cookies) > 0:
            self.game_time += self.dt
        elif self.best_time is None or self.best_time > self.game_time:
                self.best_time = self.game_time
