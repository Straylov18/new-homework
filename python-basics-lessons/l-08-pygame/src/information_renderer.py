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
