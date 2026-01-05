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
