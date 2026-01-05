import pygame

from game_constants import DISPLAY_HEIGHT, DISPLAY_WIDTH, TEXT_FONT


class InfoRenderer:

    @staticmethod
    def render_time(game_time, screen):
        text_game_time = TEXT_FONT.render(f'{game_time:.2f} сек.', True, (255, 0, 0))
        rect_text_game_time = text_game_time.get_rect()
        rect_text_game_time.center = (DISPLAY_WIDTH / 2, 50)
        screen.blit(text_game_time, rect_text_game_time)

    @staticmethod
    def render_win_screen(game_time, best_time, screen):
        rect1 = pygame.Rect((DISPLAY_WIDTH / 2 - 250, DISPLAY_HEIGHT / 2 - 100, 500, 200))
        panel_color = (100, 150, 255)
        if best_time >= game_time:
            panel_color = (125, 255, 150)
        pygame.draw.rect(screen, panel_color, rect1)
        text_your_time = TEXT_FONT.render(f'Ты съел все за {game_time:.2f} сек.', True, (255, 0, 0))
        rect_text_your_time = text_your_time.get_rect()
        rect_text_your_time.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 - 65)
        screen.blit(text_your_time, rect_text_your_time)
        text_enter = TEXT_FONT.render('"Enter" - начать заново.', True, (255, 0, 0))
        rect_text_enter = text_enter.get_rect()
        rect_text_enter.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)
        screen.blit(text_enter, rect_text_enter)
        if best_time >= game_time:
            text_new_record = TEXT_FONT.render('Новый рекорд!', True, (255, 0, 0))
            rect_text_new_record = text_new_record.get_rect()
            rect_text_new_record.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 65)
            screen.blit(text_new_record, rect_text_new_record)
